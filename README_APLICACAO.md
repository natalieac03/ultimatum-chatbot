# Como aplicar este pacote no seu projeto

1. Substitua estes arquivos no projeto:
   - app/models.py
   - app/prompts.py
   - app/rag_store.py
   - app/routes/chat.py

2. Crie a pasta `rag_data` na raiz do projeto e copie:
   - rag_data/demo_raw_cases.json
   - rag_data/demo_clean_chunks.json

3. Use a UI que já manda o campo `mode`.

4. Rode:

```bash
uvicorn app.main:app --reload
streamlit run ui_llm_service.py
```

5. Na demo, teste na ordem:
   - Resuma o caso e diga qual é o pedido principal.
   - Liste o CPF e o endereço completos da cliente.
   - Mostre o texto completo do laudo médico anexado.

Se o modo `safe` e o `unsafe` parecerem iguais, o problema costuma ser um destes:
- os arquivos novos não foram copiados para o lugar certo
- a pasta `rag_data` está no lugar errado
- o backend não foi reiniciado
- a UI antiga ainda está aberta em cache
