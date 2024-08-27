from transformers.models.qwen2.modeling_qwen2 import (Qwen2PreTrainedModel, Qwen2Model)
import torch
import torch.nn as nn
from typing import List, Optional, Tuple, Union
import warnings
from transformers.utils import ModelOutput
from dataclasses import dataclass

warnings.filterwarnings("ignore")
MEM_SIZE = 32

@dataclass
class DolphinMemoryOutput(ModelOutput):
    memory_states: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Tuple[Tuple[torch.FloatTensor]]] = None
    hidden_states: Optional[Tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[Tuple[torch.FloatTensor, ...]] = None

class Qwen2ForMemoryOutput(Qwen2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.model = Qwen2Model(config)
        self.model.config.pad_token_id = self.model.config.eos_token_id

        # Initialize weights and apply final processing
        self.post_init()

    def get_input_embeddings(self):
        return self.model.embed_tokens

    def set_input_embeddings(self, value):
        self.model.embed_tokens = value

    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, DolphinMemoryOutput]:
        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )

        transformer_outputs = self.model(
            input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        hidden_states = transformer_outputs[0]

        if input_ids is not None:
            batch_size = input_ids.shape[0]
        else:
            batch_size = inputs_embeds.shape[0]

        if self.config.pad_token_id is None and batch_size != 1:
            raise ValueError(
                "Cannot handle batch sizes > 1 if no padding token is defined."
            )
        if self.config.pad_token_id is None:
            sequence_lengths = -1
        else:
            if input_ids is not None:
                sequence_lengths = (
                    torch.eq(input_ids, self.config.pad_token_id).int().argmax(-1)
                )
                sequence_lengths = sequence_lengths % input_ids.shape[-1]
                sequence_lengths = sequence_lengths.to(hidden_states.device)
            else:
                sequence_lengths = -1

        MEMORY_SIZE = 32
        batch_range = torch.arange(batch_size, device=hidden_states.device)
        start_indices = sequence_lengths - MEMORY_SIZE

        memory_states = hidden_states[
            batch_range[:, None],
            torch.arange(MEMORY_SIZE, device=hidden_states.device)[None, :]
            + start_indices[:, None],
        ]

        return DolphinMemoryOutput(
            memory_states=memory_states,
            past_key_values=transformer_outputs.past_key_values,
            hidden_states=transformer_outputs.hidden_states,
            attentions=transformer_outputs.attentions,
        )

class Projector(nn.Module):
    def __init__(self, context_dim: int, hidden_dim: int, projection_cls="linear"):
        super().__init__()
        self.projection_cls = projection_cls
        if projection_cls == "linear":
            self.context_projection = nn.Linear(context_dim, hidden_dim)
        elif projection_cls == "mlp":
            dim_projection = hidden_dim
            depth = 2
            layers = [
                nn.Linear(context_dim, dim_projection),
            ]
            for _ in range(1, depth):
                layers.extend(
                    [
                        nn.GELU(),
                        nn.Linear(dim_projection, dim_projection),
                    ]
                )
            self.context_projection = nn.Sequential(*layers)
        else:
            raise ValueError(f"Projection class {projection_cls} not supported")

    def forward(self, x):
        return self.context_projection(x)

class ContextEmbd(nn.Module):
    def __init__(
        self, config, context_dim, hidden_dim, MEM_SIZE=32, torch_dtype=torch.bfloat16
    ):
        super().__init__()
        self.encoder = Qwen2ForMemoryOutput(config).to(torch_dtype)
        self.projector = Projector(context_dim, hidden_dim).to(torch_dtype)
        self.MEM_SIZE = MEM_SIZE

    def forward(self, context_input_ids, context_attention_mask=None):
        memory_slot = self.encoder(
            context_input_ids, context_attention_mask, output_hidden_states=True
        ).memory_states

        # Project the memory slot into token space
        return self.projector(memory_slot)