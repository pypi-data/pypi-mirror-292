import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv

from aq_geometric.models.torch.autoencoder_forecaster.autoencoder import AqGeometricSpatioTemporalAutoencoder


class EnhancedAutoencoderForecaster(nn.Module):
    def __init__(
            self,
            autoencoder: AqGeometricSpatioTemporalAutoencoder,
            forecast_steps: int,
            num_targets: int,
            hidden_dim: int = 256,
            num_gru_layers: int = 2,
            bidirectional_gru: bool = True, 
            use_gcn_refinement: bool = True,
            use_skip_connections: bool = True,
            verbose: bool = False,
        ):
        super().__init__()

        self.autoencoder = autoencoder

        self.forecast_steps = forecast_steps
        self.num_targets = num_targets

        self.hidden_dim = hidden_dim
        self.num_gru_layers = num_gru_layers
        self.bidirectional_gru = bidirectional_gru
        self.use_gcn_refinement = use_gcn_refinement
        self.use_skip_connections = use_skip_connections

        self.verbose = verbose

        # Freeze the weights of the autoencoder
        for param in self.autoencoder.parameters():
            param.requires_grad = False

        # 1. Learnable layers for the forecaster
        self.latent_adjustment = nn.Linear(self.autoencoder.encoder.latent_dim, self.hidden_dim)

        self.rnn_decoder = nn.GRU(
            input_size=self.hidden_dim * 2,  # Input will be the concatenation of latent representation and processed input
            hidden_size=self.hidden_dim,
            num_layers=num_gru_layers,
            batch_first=True,
            bidirectional=bidirectional_gru
        )

        if self.use_gcn_refinement:
            self.gcn_forecaster = GCNConv(self.hidden_dim * 2, self.hidden_dim * 2)

        self.input_projection = nn.Linear(num_targets, self.hidden_dim)
        self.output_refinement = nn.Linear(self.hidden_dim * 2, num_targets)

    def forward(self, x, edge_index, x_mask):

        if self.verbose: print(f"x shape: {x.shape}")
        # 1. Encode input to latent space (no gradients needed)
        with torch.no_grad():
            _, z = self.autoencoder.forward(x, edge_index, x_mask)  # z: (num_nodes, latent_dim)
        if self.verbose: print(f"z shape: {z.shape}")

        z_repeated = z.unsqueeze(1).repeat(1, x.size(1), 1)  # Repeat z along the time dimension
        if self.verbose: print(f"z_repeated shape: {z_repeated.shape}")

        # 2. Adjust latent representation and project input
        z_adjusted = self.latent_adjustment(z_repeated)  # z_adjusted: (num_nodes, hidden_dim)
        if self.verbose: print(f"z_adjusted shape: {z_adjusted.shape}")

        x_projected = self.input_projection(x)  # x_projected: (num_nodes, n_timestamps, hidden_dim)
        if self.verbose: print(f"x_projected shape: {x_projected.shape}")

        # 3. Combine latent representation with processed input (skip connection)
        combined_input = torch.cat([z_adjusted, x_projected], dim=-1)  # combined_input: (num_nodes, n_timestamps + 1, hidden_dim)
        if self.verbose: print(f"combined_input shape: {combined_input.shape}")

        # 4. Initialize hidden state for the bidirectional GRU
        num_nodes, _, input_size = combined_input.shape
        hidden_dim_0 = self.num_gru_layers * 2 if self.bidirectional_gru else self.num_gru_layers
        h0 = torch.zeros(hidden_dim_0, num_nodes, self.hidden_dim).to(z.device)
        if self.verbose: print(f"h0 shape: {h0.shape}")

        # Get node mask from x_mask
        x_mask_temporal_mean = x_mask.to(torch.float32).mean(dim=-1)
        node_mask = x_mask_temporal_mean.any(dim=-1)  # node_mask: (batch_size, num_nodes)
        if self.verbose: print(f"x_mask_temporal_mean shape: {x_mask_temporal_mean.shape}")
        if self.verbose: print(f"node_mask shape: {node_mask.shape}")

        # Forecast
        outputs = []
        for t in range(self.forecast_steps):
            # Reshape combined_input for GRU (num_nodes, 1, input_size)
            gru_input = combined_input[:, -1:, :].view(num_nodes, 1, -1)
            if self.verbose: print(f"gru_input shape: {gru_input.shape}")

            output, h0 = self.rnn_decoder(gru_input, h0)
            if self.verbose: print(f"output shape: {output.shape}")
            if self.verbose: print(f"h0 shape: {h0.shape}")

            output = output.squeeze(1)  
            if self.verbose: print(f"output shape (after squeeze): {output.shape}")

            # Update the hidden state
            if self.bidirectional_gru:
                h0_forward, h0_backward = h0.chunk(2, 0)
                h0 = torch.cat([h0_forward, h0_backward], dim=0).contiguous() 
            else:
                h0 = h0.squeeze(0)

            # Optional spatial refinement with GCN
            if self.use_gcn_refinement:
                output = self.gcn_forecaster(output, edge_index)

            # Residual connection
            if self.use_skip_connections and t > 0:
                output += combined_input[:, -1, :]

            outputs.append(output)

            # Update combined_input for the next timestep
            combined_input = torch.cat([combined_input, output.unsqueeze(1)], dim=1) 
            if self.verbose: print(f"combined_input shape (after concatenation) (timestep {t} of {self.forecast_steps}): {combined_input.shape}")

        x_hat = torch.cat(outputs, dim=1)
        if self.verbose: print(f"x_hat shape: {x_hat.shape}")
        # Reshape before applying output_refinement
        x_hat = x_hat.view(num_nodes, self.forecast_steps, -1)
        if self.verbose: print(f"x_hat shape (after view): {x_hat.shape}")

        x_hat = self.output_refinement(x_hat)
        if self.verbose: print(f"x_hat shape (after output refinement): {x_hat.shape}")

        # Reshape the output to (batch_size, num_nodes, forecast_steps, num_targets)
        x_hat = x_hat.view(num_nodes, self.forecast_steps, self.num_targets)
        if self.verbose: print(f"x_hat shape (after view 2): {x_hat.shape}")

        return x_hat