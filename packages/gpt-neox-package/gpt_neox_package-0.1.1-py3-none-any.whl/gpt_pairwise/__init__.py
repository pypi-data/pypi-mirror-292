from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

from .modelling_gpt_neox_pairwise import GPTNeoXModel, GPTNeoXForCausalLM
from .configuration_gpt_neox import GPTNeoXConfig

# Register the custom configuration and model
AutoConfig.register('iak/gpt_pairwise', GPTNeoXConfig)
AutoModel.register(GPTNeoXConfig, GPTNeoXModel, exist_ok=True)
AutoModelForCausalLM.register(GPTNeoXConfig, GPTNeoXForCausalLM, exist_ok=True)

__all__ = ['GPTNeoXModel', 'GPTNeoXForCausalLM', 'GPTNeoXConfig']
