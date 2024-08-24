# Copyright 2024 Agnostiq Inc.
from pathlib import Path

from covalent_blueprints import register_blueprints_dir

from ._prefix import PREFIX
from .llama_chatbot import llama_chatbot
from .lora_fine_tuning import lora_fine_tuning
from .nvidia_llama_rag import nvidia_llama_rag
from .sdxl_basic import sdxl_basic
from .vllm_basic import vllm_basic

__all__ = [
    "llama_chatbot",
    "lora_fine_tuning",
    "nvidia_llama_rag",
    "sdxl_basic",
    "vllm_basic",
]


register_blueprints_dir(
    name=PREFIX,
    install_dir=Path(__file__).parent,
    overwrite=True,
)
