from pydantic import BaseModel


class LLMConfig(BaseModel):
    """
    Used to configure the LLM settings
    """
    turn_max_tokens: int
    generation_max_tokens: int
    stopping_tokens: list[str]
