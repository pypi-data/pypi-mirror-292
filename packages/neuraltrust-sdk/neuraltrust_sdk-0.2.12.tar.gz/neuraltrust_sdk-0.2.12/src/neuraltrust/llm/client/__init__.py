from .base import ChatMessage, LLMClient
from .logger import LLMLogger
from ...utils.config import ConfigHelper

_target_client = None
_judge_client = None

def set_target_client(client: LLMClient):
    global _target_client
    _target_client = client

def set_judge_client(client: LLMClient):
    global _judge_client
    _judge_client = client


def get_judge_client() -> LLMClient:
    global _judge_client

    if _judge_client is not None:
        return _judge_client

    from .openai import OpenAIClient

    default_llm_api = ConfigHelper.load_llm_provider()
    default_llm_judge_model = ConfigHelper.load_llm_judge_model()

    try:
        from openai import AzureOpenAI, OpenAI

        client = AzureOpenAI() if default_llm_api == "azure" else OpenAI()

        _judge_client = OpenAIClient(model=default_llm_judge_model, client=client)
    except ImportError:
        raise ValueError(f"LLM scan using {default_llm_api.name} require openai>=1.0.0")

    return _judge_client



def get_target_client() -> LLMClient:
    global _target_client

    if _target_client is not None:
        return _target_client

    from .openai import OpenAIClient

    default_llm_api = ConfigHelper.load_llm_provider()
    default_llm_target_model = ConfigHelper.load_llm_target_model()

    try:
        from openai import AzureOpenAI, OpenAI

        client = AzureOpenAI() if default_llm_api == "azure" else OpenAI()

        _target_client = OpenAIClient(model=default_llm_target_model, client=client)
    except ImportError:
        raise ValueError(f"LLM scan using {default_llm_api.name} require openai>=1.0.0")

    return _target_client


__all__ = [
    "LLMClient",
    "ChatMessage",
    "LLMLogger",
    "get_target_client",
    "set_target_client",
    "get_judge_client",
    "set_judge_client",
]
