import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv


class Encoder(nn.Module):
    def __init__(self, num_nodes, num_timestamps, num_features, hidden_dim, latent_dim):
        super().__init__()
        
        self.num_nodes = num_nodes
        self.num_timestamps = num_timestamps
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        
        self.rnn_encoder = nn.LSTM(num_features, hidden_dim, batch_first=True)  
        self.bn = nn.BatchNorm1d(num_nodes)
        self.gcn_encoder = GCNConv(hidden_dim, hidden_dim)
        self.fc1 = nn.Linear(hidden_dim, latent_dim)
        

    def forward(self, x, edge_index, x_mask):
        # x: (num_nodes, num_timestamps, num_features)
        # edge_index: (2, num_edges)
        # x_mask: (num_nodes, num_timestamps, num_features)

        # Apply mask to input features
        x_masked = x * x_mask
        x_masked = torch.where(torch.isnan(x_masked), torch.tensor(0.0), x_masked)
        # Expected shape of x_masked: (num_nodes, num_timestamps, num_features)

        # Temporal encoding
        _, (hidden, _) = self.rnn_encoder(x_masked) 
        hidden = hidden.squeeze(0)
        hidden = hidden.permute(1, 0)  # (num_nodes, hidden_dim) -> (hidden_dim, num_nodes)
        hidden = self.bn(hidden)
        hidden = hidden.permute(1, 0)  # Permute back
        # Expected shape of hidden: (num_nodes, hidden_dim)

        # Spatial encoding
        node_embeddings = self.gcn_encoder(hidden, edge_index)
        # Expected shape of node_embeddings: (num_nodes, hidden_dim)

        # Further compression
        z = self.fc1(node_embeddings)
        # Expected shape of z: (num_nodes, latent_dim)

        return z

class Decoder(nn.Module):
    def __init__(self, num_nodes, num_timestamps, num_features, hidden_dim, latent_dim):
        super().__init__()

        self.num_nodes = num_nodes
        self.num_timestamps = num_timestamps
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim

        self.fc2 = nn.Linear(latent_dim, hidden_dim)
        self.rnn_decoder = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        self.gcn_decoder = GCNConv(hidden_dim, hidden_dim) 
        self.fc3 = nn.Linear(hidden_dim, num_features)

    def forward(self, z, edge_index, x_mask):
        # z: (num_nodes, latent_dim)
        # edge_index: (2, num_edges)
        # x_mask: (num_nodes, num_timestamps, num_features)

        # Transform the x_mask into a node_mask (2D)
        x_mask_temporal_mean = x_mask.to(torch.float32).mean(dim=-1)  # Average mask across feature dimension
        node_mask = x_mask_temporal_mean.any(dim=-1)  # Reduce to (num_nodes,) to see if any value was masked for this node

        # Decompression from latent space
        hidden_decoded = self.fc2(z)
        # Expected shape of hidden_decoded: (num_nodes, hidden_dim)

        # Prepare initial hidden and cell states for the decoder RNN
        h0 = hidden_decoded.unsqueeze(0) 
        c0 = torch.zeros_like(h0)
        # Expected shapes of h0, c0: (1, num_nodes, hidden_dim)

        # Repeat the latent representation across the time dimension
        z_repeated = hidden_decoded.unsqueeze(1).repeat(1, self.num_timestamps, 1)
        # Expected shape of z_repeated: (num_nodes, num_timestamps, hidden_dim)

        # Temporal decoding
        output, _ = self.rnn_decoder(z_repeated, (h0, c0))  
        # Expected shape of output: (num_nodes, num_timestamps, hidden_dim)

        # Spatial refinement with masked decoded hidden states
        x_mask_expanded = node_mask.unsqueeze(1).unsqueeze(-1).expand_as(output) 
        output_masked = output * x_mask_expanded
        output_masked = torch.where(torch.isnan(output_masked), torch.tensor(0.0), output_masked)

        # Expected shape of output_masked: (num_nodes, num_timestamps, hidden_dim)

        # Apply GCN decoder
        output_masked = output_masked.permute(1, 0, 2)  # (num_nodes, num_timestamps, hidden_dim) -> (num_timestamps, num_nodes, hidden_dim)
        spatial_embeddings = self.gcn_decoder(output_masked, edge_index)
        spatial_embeddings = spatial_embeddings.permute(1, 0, 2)  # Permute back
        # Expected shape of spatial_embeddings: (num_nodes, num_timestamps, hidden_dim)

        # Map from hidden_dim to num_features
        x_hat = self.fc3(spatial_embeddings)
        # Expected shape of x_hat: (num_nodes, num_timestamps, num_features)

        return x_hat

class AqGeometricSpatioTemporalAutoencoder(nn.Module):
    def __init__(self, num_nodes=5921, num_timestamps=48, num_features=2, hidden_dim=64, latent_dim=32):
        super().__init__()

        self.num_nodes = num_nodes
        self.num_timestamps = num_timestamps
        self.num_features = num_features
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim

        self.encoder = Encoder(num_nodes, num_timestamps, num_features, hidden_dim, latent_dim)
        self.decoder = Decoder(num_nodes, num_timestamps, num_features, hidden_dim, latent_dim)

    def forward(self, x, edge_index, x_mask):
        z = self.encoder(x, edge_index, x_mask)
        x_hat = self.decoder(z, edge_index, x_mask)
        return x_hat, z
