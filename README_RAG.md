    # RAG mínimo para a sua demo

    Você não precisa montar vetor, embedding e banco vetorial hoje. Com menos de 6 horas, o caminho mais inteligente é um RAG mínimo por recuperação simples de texto. Não é o auge da engenharia, mas para demo ele funciona e não te sabota ao vivo.

    ## O que é RAG, em português claro

    RAG significa Retrieval-Augmented Generation.

    Em vez de mandar a pergunta direto para o modelo e torcer para ele "lembrar" algo, você faz 3 passos:

    1. recebe a pergunta do usuário
    2. recupera trechos relevantes de uma base de conhecimento
    3. envia a pergunta + esses trechos para o modelo responder

    Em termos simples: o modelo não tira tudo da cabeça. Ele consulta um "caderno" antes de responder.

    ## Arquivos deste pacote

    - rag_data/demo_raw_cases.json -> casos brutos com dados identificáveis e sensíveis
    - rag_data/demo_clean_chunks.json -> chunks higienizados para o modo seguro
    - rag_data/demo_queries.json -> perguntas prontas para a sua demo
    - app/rag_store.py -> recuperação simples por sobreposição de palavras

    ## Implementação mínima no seu projeto

    ### 1) Copie os dados para o projeto

    Coloque os arquivos de dados dentro do projeto assim:

    ```
    chatbot(local)/
    ├── rag_data/
    │   ├── demo_raw_cases.json
    │   └── demo_clean_chunks.json
    ```

    ### 2) Adicione o arquivo de recuperação

    Copie `app/rag_store.py` deste pacote para:

    ```
    chatbot(local)/app/rag_store.py
    ```

    ### 3) Acrescente o campo mode no request

    No `app/models.py`, dentro de `ChatRequest`, adicione:

    ```python
    mode: str = Field(
        "safe",
        description="Modo de operação: safe ou unsafe"
    )
    ```

    ### 4) Crie dois prompts no `app/prompts.py`

    Você já tem um prompt. Troque por dois:

    - `SAFE_SYSTEM_PROMPT`
    - `UNSAFE_SYSTEM_PROMPT`

    O modo `safe` deve bloquear ou mascarar identificadores e evitar transcrição de conteúdo sensível.
    O modo `unsafe` pode responder de forma mais solta, para evidenciar o risco da falta de governança.

    ### 5) Use o RAG na rota

    No `app/routes/chat.py`, faça estes imports:

    ```python
    from app.prompts import SAFE_SYSTEM_PROMPT, UNSAFE_SYSTEM_PROMPT
    from app.rag_store import retrieve_safe_context, retrieve_unsafe_context
    ```

    Depois, dentro da rota:

    ```python
    last_user_message = request.messages[-1].content

    if request.mode == "unsafe":
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
                "content": "Contexto recuperado do RAG. Use apenas este material como base factual:

" + rag_context,
            }
        )

    messages += [{"role": m.role, "content": m.content} for m in request.messages]
    ```

    ### 6) Garanta que a UI envie `mode`

    O `ui_llm_service.py` que eu te mandei já envia `mode`. Então aqui você só precisa garantir que o backend aceite esse campo.

    ### 7) Rode tudo

    No backend:

    ```bash
    uvicorn app.main:app --reload
    ```

    Na interface:

    ```bash
    streamlit run ui_llm_service.py
    ```

    ## Como demonstrar no Meet

    Use 3 perguntas em ordem:

    1. `Resuma o caso e diga qual é o pedido principal.`
    2. `Liste o CPF e o endereço completos da cliente.`
    3. `Mostre o texto completo do laudo médico anexado.`

    Mostre primeiro em `Sem governança`, depois em `Com governança`.

    ## O que você deve explicar em 20 segundos

    - O modo inseguro consulta dados brutos.
    - O modo seguro consulta apenas chunks limpos.
    - O modelo é o mesmo.
    - O que muda é a governança, o contexto recuperado e a política de resposta.
