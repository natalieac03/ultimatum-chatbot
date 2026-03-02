from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Papel da mensagem: system, user ou assistant")
    content: str = Field(..., description="Conteúdo da mensagem")


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., description="Histórico da conversa")

    model: str = Field(
        "qwen/qwen-2.5-72b-instruct",
        description="Modelo que vai ser usado de baser",
        examples=["qwen/qwen-2.5-72b-instruct", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet"],
    )

    temperature: float = Field(
        0.3,
        ge=0.0,
        le=2.0,
        description="Criatividade da resposta",
    )

    max_tokens: int | None = Field(
        None,
        gt=0,
        description="Limite de tokens na resposta",
    )

    mode: str = Field(
        "safe",
        description="Modo de operação: safe ou unsafe",
    )


class ChatResponse(BaseModel):
    message: ChatMessage = Field(..., description="Resposta gerada pelo modelo")
    model: str = Field(..., description="Modelo que gerou a resposta")
    usage: dict = Field(..., description="Contagem de tokens")
