import pytest
from transformers import AutoConfig, AutoModelForCausalLM

def test_model_loading():
    config = AutoConfig.from_pretrained('iak/gpt_pairwise')
    model = AutoModelForCausalLM.from_pretrained('iak/gpt_pairwise')
    
    assert config is not None
    assert model is not None