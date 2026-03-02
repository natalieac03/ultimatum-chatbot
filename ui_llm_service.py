import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Chat LLM",
    page_icon="🤖",
    layout="centered",
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-vl-235b-a22b-thinking")
DEFAULT_TEMPERATURE = 0.5
MODE_OPTIONS = ["safe", "unsafe"]


MODE_LABELS = {
    "safe": "Com governança",
    "unsafe": "Sem governança",
}

MODE_HELP = {
    "safe": (
        "Modo pensado para a demonstração segura. "
        "O backend deve aplicar regras de privacidade, bloqueio e mascaramento."
    ),
    "unsafe": (
        "Modo pensado para a demonstração insegura. "
        "O backend tende a responder sem filtros fortes, se estiver configurado para isso."
    ),
}


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "temperature" not in st.session_state:
        st.session_state["temperature"] = DEFAULT_TEMPERATURE
    if "mode" not in st.session_state:
        st.session_state["mode"] = "safe"


def reset_chat() -> None:
    st.session_state["messages"] = []


def format_error_detail(detail: Any) -> str:
    if isinstance(detail, str):
        return detail

    if isinstance(detail, dict):
        if "message" in detail and isinstance(detail["message"], str):
            return detail["message"]
        return str(detail)

    if isinstance(detail, list):
        parts = []
        for item in detail:
            if isinstance(item, dict):
                loc = item.get("loc")
                msg = item.get("msg")
                if loc and msg:
                    parts.append(f"{loc}: {msg}")
                elif msg:
                    parts.append(str(msg))
                else:
                    parts.append(str(item))
            else:
                parts.append(str(item))
        return " | ".join(parts)

    return "Erro desconhecido."


def get_mode_label(mode: str) -> str:
    return MODE_LABELS.get(mode, mode)


def call_llm(messages: list[dict], mode: str) -> str:
    payload = {
        "messages": messages,
        "model": MODEL,
        "temperature": st.session_state["temperature"],
        "mode": mode,
    }

    try:
        response = requests.post(
            f"{API_URL}/chat",
            json=payload,
            timeout=60,
        )
    except requests.Timeout:
        return "A requisição demorou demais. O backend ou a OpenRouter estão lerdos."
    except requests.ConnectionError:
        return (
            "Não consegui conectar no backend. "
            "Confere se ele está rodando em http://127.0.0.1:8000."
        )
    except requests.RequestException as e:
        return f"Falha de conexão: {e}"

    try:
        data = response.json()
    except ValueError:
        return f"O backend respondeu com algo que não é JSON válido (HTTP {response.status_code})."

    if response.status_code != 200:
        detail = data.get("detail", "Erro desconhecido no backend.")
        return f"Erro da API: {format_error_detail(detail)}"

    try:
        content = data["message"]["content"]
    except (KeyError, TypeError):
        return "A resposta da API veio em formato inesperado."

    if not isinstance(content, str) or not content.strip():
        return "A resposta veio vazia."

    return content


def render_messages() -> None:
    for msg in st.session_state["messages"]:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.markdown(content)


def render_mode_banner() -> None:
    current_mode = st.session_state["mode"]
    label = get_mode_label(current_mode)
    description = MODE_HELP.get(current_mode, "")

    if current_mode == "safe":
        st.success(f"Modo atual: **{label}**")
    else:
        st.warning(f"Modo atual: **{label}**")

    st.caption(description)


init_session_state()

st.title("Chatbot Jurídico")
st.caption("Demonstração comparativa: mesmo modelo, políticas diferentes")

with st.sidebar:
    st.subheader("Configurações")
    st.write(f"**API:** `{API_URL}`")
    st.write(f"**Modelo:** `{MODEL}`")

    selected_mode = st.selectbox(
        "Modo do chatbot",
        options=MODE_OPTIONS,
        index=MODE_OPTIONS.index(st.session_state["mode"]),
        format_func=get_mode_label,
        help=(
            "Use 'Com governança' para a versão com regras de privacidade. "
            "Use 'Sem governança' para mostrar o contraste na demonstração."
        ),
    )
    st.session_state["mode"] = selected_mode
    st.caption(
        "Observação: esse seletor só muda o comportamento de verdade se o backend "
        "usar o campo `mode` para escolher prompts/regras diferentes."
    )

    st.session_state["temperature"] = st.slider(
        "Temperatura",
        min_value=0.1,
        max_value=0.8,
        value=float(st.session_state["temperature"]),
        step=0.1,
        help="Quanto maior, mais criativa a resposta.",
    )

    if st.button("Nova conversa", use_container_width=True):
        reset_chat()
        st.rerun()

render_mode_banner()
render_messages()

prompt = st.chat_input("Digite sua mensagem...")

if prompt and prompt.strip():
    user_message = {
        "role": "user",
        "content": prompt.strip(),
    }
    st.session_state["messages"].append(user_message)

    with st.chat_message("user"):
        st.markdown(user_message["content"])

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            answer = call_llm(st.session_state["messages"], st.session_state["mode"])
            st.markdown(answer)

    st.session_state["messages"].append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
