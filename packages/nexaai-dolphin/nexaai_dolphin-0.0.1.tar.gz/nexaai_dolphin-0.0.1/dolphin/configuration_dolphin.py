# coding=utf-8
# Copyright 2024 The Qwen team, Alibaba Group and the HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Qwen2 model configuration"""

from transformers.configuration_utils import PretrainedConfig
from transformers.utils import logging

logger = logging.get_logger(__name__)

class DolphinConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of a [`DolphinModel`]. It is used to instantiate a
    Qwen2 model according to the specified arguments, defining the model architecture. Instantiating a configuration
    with the defaults will yield a similar configuration to that of
    Qwen2-7B-beta [Qwen/Qwen2-7B-beta](https://huggingface.co/Qwen/Qwen2-7B-beta).

    Configuration objects inherit from [`PretrainedConfig`] and can be used to control the model outputs. Read the
    documentation from [`PretrainedConfig`] for more information.


    Args:
        vocab_size (`int`, *optional*, defaults to 151936):
            Vocabulary size of the Qwen2 model. Defines the number of different tokens that can be represented by the
            `inputs_ids` passed when calling [`DolphinModel`]
        hidden_size (`int`, *optional*, defaults to 4096):
            Dimension of the hidden representations.
        intermediate_size (`int`, *optional*, defaults to 22016):
            Dimension of the MLP representations.
        num_hidden_layers (`int`, *optional*, defaults to 32):
            Number of hidden layers in the Transformer encoder.
        num_attention_heads (`int`, *optional*, defaults to 32):
            Number of attention heads for each attention layer in the Transformer encoder.
        num_key_value_heads (`int`, *optional*, defaults to 32):
            This is the number of key_value heads that should be used to implement Grouped Query Attention. If
            `num_key_value_heads=num_attention_heads`, the model will use Multi Head Attention (MHA), if
            `num_key_value_heads=1` the model will use Multi Query Attention (MQA) otherwise GQA is used. When
            converting a multi-head checkpoint to a GQA checkpoint, each group key and value head should be constructed
            by meanpooling all the original heads within that group. For more details checkout [this
            paper](https://arxiv.org/pdf/2305.13245.pdf). If it is not specified, will default to `32`.
        hidden_act (`str` or `function`, *optional*, defaults to `"silu"`):
            The non-linear activation function (function or string) in the decoder.
        max_position_embeddings (`int`, *optional*, defaults to 32768):
            The maximum sequence length that this model might ever be used with.
        initializer_range (`float`, *optional*, defaults to 0.02):
            The standard deviation of the truncated_normal_initializer for initializing all weight matrices.
        rms_norm_eps (`float`, *optional*, defaults to 1e-06):
            The epsilon used by the rms normalization layers.
        use_cache (`bool`, *optional*, defaults to `True`):
            Whether or not the model should return the last key/values attentions (not used by all models). Only
            relevant if `config.is_decoder=True`.
        tie_word_embeddings (`bool`, *optional*, defaults to `False`):
            Whether the model's input and output word embeddings should be tied.
        rope_theta (`float`, *optional*, defaults to 10000.0):
            The base period of the RoPE embeddings.
        use_sliding_window (`bool`, *optional*, defaults to `False`):
            Whether to use sliding window attention.
        sliding_window (`int`, *optional*, defaults to 4096):
            Sliding window attention (SWA) window size. If not specified, will default to `4096`.
        max_window_layers (`int`, *optional*, defaults to 28):
            The number of layers that use SWA (Sliding Window Attention). The bottom layers use SWA while the top use full attention.
        attention_dropout (`float`, *optional*, defaults to 0.0):
            The dropout ratio for the attention probabilities.
    ```"""

    # The `model_type` attribute in the `DolphinConfig` class is a string variable that specifies the
    # type of model configuration. In this case, it is set to "qwen2", indicating that the
    # configuration is specifically designed for a Qwen2 model. This attribute helps identify the type
    # of model configuration being used and can be useful for distinguishing between different model
    # configurations or types within a codebase.
    model_type = "dolphin"
    keys_to_ignore_at_inference = ["past_key_values"]

    def __init__(
        self,
        vocab_size=151936,
        hidden_size=4096,
        intermediate_size=22016,
        num_hidden_layers=32,
        num_attention_heads=32,
        num_key_value_heads=32,
        hidden_act="silu",
        max_position_embeddings=32768,
        initializer_range=0.02,
        rms_norm_eps=1e-6,
        use_cache=True,
        tie_word_embeddings=False,
        rope_theta=10000.0,
        use_sliding_window=False,
        sliding_window=4096,
        max_window_layers=28,
        attention_dropout=0.0,
        encoder_config=None,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.use_sliding_window = use_sliding_window
        self.sliding_window = sliding_window
        self.max_window_layers = max_window_layers

        # for backward compatibility
        if num_key_value_heads is None:
            num_key_value_heads = num_attention_heads

        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.rope_theta = rope_theta
        self.attention_dropout = attention_dropout
        self.encoder_config = encoder_config

        super().__init__(
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )

encoder_config_dict = {
    "_name_or_path": "Qwen/Qwen2-0.5B",
    "add_cross_attention": False,
    "architectures": ["Qwen2ForCausalLM"],
    "attention_dropout": 0.0,
    "bad_words_ids": None,
    "begin_suppress_tokens": None,
    "bos_token_id": 151643,
    "chunk_size_feed_forward": 0,
    "cross_attention_hidden_size": None,
    "decoder_start_token_id": None,
    "diversity_penalty": 0.0,
    "do_sample": False,
    "early_stopping": False,
    "encoder_config": None,
    "encoder_no_repeat_ngram_size": 0,
    "eos_token_id": 151643,
    "exponential_decay_length_penalty": None,
    "finetuning_task": None,
    "forced_bos_token_id": None,
    "forced_eos_token_id": None,
    "hidden_act": "silu",
    "hidden_size": 896,
    "id2label": {"0": "LABEL_0", "1": "LABEL_1"},
    "initializer_range": 0.02,
    "intermediate_size": 4864,
    "is_decoder": False,
    "is_encoder_decoder": False,
    "label2id": {"LABEL_0": 0, "LABEL_1": 1},
    "length_penalty": 1.0,
    "max_length": 20,
    "max_position_embeddings": 131072,
    "max_window_layers": 24,
    "min_length": 0,
    "model_type": "qwen2",
    "no_repeat_ngram_size": 0,
    "num_attention_heads": 14,
    "num_beam_groups": 1,
    "num_beams": 1,
    "num_hidden_layers": 24,
    "num_key_value_heads": 2,
    "num_return_sequences": 1,
    "output_attentions": False,
    "output_hidden_states": False,
    "output_scores": False,
    "pad_token_id": None,
    "prefix": None,
    "problem_type": None,
    "pruned_heads": {},
    "remove_invalid_values": False,
    "repetition_penalty": 1.0,
    "return_dict": True,
    "return_dict_in_generate": False,
    "rms_norm_eps": 1e-06,
    "rope_theta": 1000000.0,
    "sep_token_id": None,
    "sliding_window": 131072,
    "suppress_tokens": None,
    "task_specific_params": None,
    "temperature": 1.0,
    "tf_legacy_loss": False,
    "tie_encoder_decoder": False,
    "tie_word_embeddings": True,
    "tokenizer_class": None,
    "top_k": 50,
    "top_p": 1.0,
    "torch_dtype": "bfloat16",
    "torchscript": False,
    "typical_p": 1.0,
    "use_bfloat16": False,
    "use_cache": True,
    "use_sliding_window": False,
    "vocab_size": 151936,
    "attn_implementation": None,
}

if __name__ == "__main__":
    config = DolphinConfig(encoder_config=encoder_config_dict)
    config.save_pretrained("dolphin-config")