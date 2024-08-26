import torch
import torch.nn as nn

from aq_geometric.models.torch.autoencoder_forecaster.autoencoder import AqGeometricSpatioTemporalAutoencoder


class AutoencoderForecaster(nn.Module):
    def __init__(self, autoencoder: AqGeometricSpatioTemporalAutoencoder, forecast_steps: int, num_targets: int, num_gru_layers: int = 2, bidirectional_gru: bool = True):
        super().__init__()
        self.autoencoder = autoencoder
        self.forecast_steps = forecast_steps
        self.num_targets = num_targets
        self.num_gru_layers = num_gru_layers
        self.bidirectional_gru = bidirectional_gru

        # Freeze the weights of the autoencoder
        for param in self.autoencoder.parameters():
            param.requires_grad = False

        # Learnable layers for the forecaster (no gradients in the autoencoder's decoder)
        self.rnn_decoder = nn.GRU(
            input_size=self.autoencoder.decoder.fc2.out_features,  # Input from the latent adjustment layer
            hidden_size=self.autoencoder.decoder.rnn_decoder.hidden_size,  
            num_layers=num_gru_layers,
            batch_first=True,
            bidirectional=bidirectional_gru
        )
        self.gru_output_adjustment = nn.Linear(
            self.autoencoder.decoder.rnn_decoder.hidden_size * 2,  # Bidirectional output
            self.autoencoder.decoder.rnn_decoder.hidden_size
        )
        self.latent_adjustment = nn.Linear(self.autoencoder.encoder.latent_dim, self.autoencoder.encoder.latent_dim)
        self.output_refinement = nn.Linear(self.autoencoder.decoder.fc3.out_features, num_targets)

    def forward(self, x, edge_index, x_mask):
        # Encode input to latent space (no gradients needed)
        with torch.no_grad():
            z = self.autoencoder.encoder(x, edge_index, x_mask)

        # Adjust latent representation
        z = self.latent_adjustment(z)
        #print(f"z shape: {z.shape}")
        hidden_decoded = self.autoencoder.decoder.fc2(z)
        #print(f"hidden_decoded shape: {hidden_decoded.shape}")

        # Reshape hidden states to be 2D for the first iteration
        h0 = hidden_decoded.unsqueeze(0).repeat(4, 1, 1)
        #print(f"h0 shape: {h0.shape}")
        # Expected shapes of h0: (1, num_nodes, hidden_dim)

        # Get node mask from x_mask
        x_mask_temporal_mean = x_mask.to(torch.float32).mean(dim=-1)
        node_mask = x_mask_temporal_mean.any(dim=-1)
        #print(f"node_mask shape: {node_mask.shape}")
        # Expected shape of node_mask: (num_nodes,)

        # Forecast
        outputs = []
        for _ in range(self.forecast_steps):
            output, h0 = self.rnn_decoder(hidden_decoded.unsqueeze(1), h0)
            output = output.squeeze(0) 

            # Update the hidden state for the next step (corrected)
            if self.bidirectional_gru:
                h0_forward, h0_backward = h0.chunk(2, 0)  
                h0 = torch.cat([h0_forward, h0_backward], dim=0)  # Concatenate along the num_layers dimension
            else:
                h0 = h0.squeeze(0)
            #print(f"output shape after squeeze: {output.shape}")
            # Expected shape of output: (num_nodes, 2 * hidden_dim)

            # Adjust GRU output dimension before spatial refinement
            output = self.gru_output_adjustment(output.squeeze(0))
            #print(f"output shape after gru_output_adjustment: {output.shape}")
            # Expected shape of output: (num_nodes, hidden_dim)

            expanded_node_mask = node_mask.unsqueeze(1).unsqueeze(-1).expand_as(output) 
            output *= expanded_node_mask
            output_masked = torch.where(torch.isnan(output), torch.tensor(0.0), output)
            #print(f"output_masked shape: {output_masked.shape}")
            # Expected shape of output: (num_nodes, hidden_dim)

        
            output_masked = output_masked.permute(1, 0, 2)
            #print(f"output_masked shape after permute: {output_masked.shape}")
            spatial_embeddings = self.autoencoder.decoder.gcn_decoder(output_masked, edge_index)  # (num_nodes, 1, hidden_dim)
            #print(f"spatial_embeddings shape: {spatial_embeddings.shape}")
            spatial_embeddings = spatial_embeddings.permute(1, 0, 2)
            #print(f"spatial_embeddings shape after permute: {spatial_embeddings.shape}")

            # Update hidden_decoded for next step
            hidden_decoded = spatial_embeddings.squeeze(1)
            #print(f"hidden_decoded shape after squeeze: {hidden_decoded.shape}")

            # Map to output features and refine
            output_features = self.output_refinement(self.autoencoder.decoder.fc3(spatial_embeddings))
            #print(f"output_features shape: {output_features.shape}")
            outputs.append(output_features)
            #print(f"outputs shape: {len(outputs)}")
            # Expected shape of output_features: (num_nodes, 1, num_features)

        # Combine outputs and return
        x_hat = torch.cat(outputs, dim=1)
        #print(f"x_hat shape: {x_hat.shape}")

        return x_hat
