# ADR 0001: Autenticação por Cookie HttpOnly e postura CSRF

## Status

Aceita.

## Contexto

O SGP+ é uma aplicação web que exige autenticação e RBAC server-side. É proibido armazenar token em `localStorage`/`sessionStorage`. A autenticação deve ser compatível com PWA e com uso de cookies em ambiente controlado.

## Decisão

- **Auth por cookie HttpOnly** com sessão persistida em banco (tabela `sessions`, `session_id` UUID no cookie).
- **CORS**: `allow_credentials=True` e origens explícitas (lista configurável via `CORS_ORIGINS`). Não é permitido `*` quando há uso de credentials (cookie auth).
- **Cookie**: nome configurável, `path="/"`, `SameSite=Lax` por padrão, `Secure` em produção.

## CSRF – Riscos e postura atual

- **Risco**: uso de cookies com `allow_credentials=True` exige cuidado com requisições cross-site que possam levar o browser a enviar o cookie.
- **Postura atual**: `SameSite=Lax` reduz cenários típicos de CSRF (navegação de outro site envia cookie em requests top-level seguros). Não implementamos tokens CSRF nem double-submit no front na versão atual.
- **Futuro**: se for necessário `SameSite=None` (ex.: iframes cross-site ou integrações em outros domínios), avaliar introdução de mecanismo anti-CSRF (ex.: token em cookie + header, ou double-submit) e documentar em novo ADR.

## Consequências

- Cookies exigem configuração correta de CORS (origens explícitas, sem `*`) e de path/domain no set e no clear.
- Qualquer mudança que afete `SameSite` ou uso cross-site deve passar por revisão de segurança e atualização desta decisão.
