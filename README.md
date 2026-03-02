# Demo Chatbot Jurídico 

Interface em **Streamlit** para demonstrar, de forma prática, como a governança de dados muda o comportamento de um chatbot em contexto jurídico.

A aplicação compara dois modos de operação:

- **Com governança** (`safe`): o backend deve aplicar regras de privacidade, bloqueio e mascaramento.
- **Sem governança** (`unsafe`): o backend tende a responder com menos restrições, permitindo evidenciar riscos de exposição indevida.

A proposta do projeto é mostrar que a diferença entre uma resposta mais segura e uma mais arriscada **não está só no modelo**, mas principalmente na forma como o backend controla o contexto e a saída.

---

## Objetivo

Este projeto foi criado para fins de **demonstração técnica e educacional**, especialmente em apresentações, workshops e discussões sobre:

- IA aplicada a sistemas jurídicos
- LGPD e proteção de dados
- dados pessoais e dados sensíveis
- RAG e controle de contexto
- governança de saída em aplicações com LLM

A interface permite testar rapidamente como o mesmo fluxo de chat pode produzir resultados muito diferentes dependendo das regras aplicadas no backend.

---

## Como funciona

O usuário interage com uma interface de chat local em Streamlit. A UI envia as mensagens para um backend via HTTP, no endpoint `/chat`, incluindo:

- histórico de mensagens
- modelo configurado
- temperatura
- modo da demonstração (`safe` ou `unsafe`)

O backend é responsável por decidir como tratar a requisição e qual política aplicar na resposta.

### Fluxo simplificado

```text
Usuário
  ↓
UI Streamlit (ui_llm_service.py)
  ↓
POST /chat
  ↓
Backend (API externa/local)
  ↓
LLM
  ↓
Resposta na interface
