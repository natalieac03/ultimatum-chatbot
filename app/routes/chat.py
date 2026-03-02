from fastapi import APIRouter, Body, HTTPException, status

from app.client import get_client
from app.models import ChatMessage, ChatRequest, ChatResponse
from app.prompts import SAFE_SYSTEM_PROMPT, UNSAFE_SYSTEM_PROMPT
from app.rag_store import retrieve_safe_context, retrieve_unsafe_context

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest = Body(...)):
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie ao menos uma mensagem",
        )

    client = get_client()

    last_user_message = request.messages[-1].content
    mode = (request.mode or "safe").lower().strip()

    if mode == "unsafe":
        system_prompt = UNSAFE_SYSTEM_PROMPT
        rag_context = retrieve_unsafe_context(last_user_message, top_k=1)
    else:
        system_prompt = SAFE_SYSTEM_PROMPT
        rag_context = retrieve_safe_context(last_user_message, top_k=3)

    messages = [{"role": "system", "content": system_prompt}]

    if rag_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "Contexto recuperado do RAG. "
                    "Use apenas este material como base factual:\n\n" + rag_context
                ),
            }
        )

    messages += [{"role": m.role, "content": m.content} for m in request.messages]

    try:
        response = await client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao chamar o modelo: {e}",
        ) from e

    content = response.choices[0].message.content if response.choices else ""

    return ChatResponse(
        message=ChatMessage(role="assistant", content=content or "A resposta veio vazia."),
        model=response.model,
        usage=response.usage.model_dump() if response.usage else {},
    )
