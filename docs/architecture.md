# Arquitetura SGP+

## Visão Geral

SGP+ é um sistema web standalone, totalmente separado do SGP desktop.

## Stack Tecnológica

### Frontend
- React 18+ com TypeScript
- Vite como build tool
- PWA-ready (manifest configurado)
- Configuração runtime via `/public/config.json`

### Backend
- FastAPI (Python 3.12+)
- SQLAlchemy 2.0+ (ORM)
- Alembic (migrations)
- PostgreSQL (via Docker em dev, RDS em produção)

## Autenticação

- **Mecanismo**: Cookies HttpOnly
- **Fluxo**:
  1. Login cria sessão no banco (UUID)
  2. Cookie HttpOnly armazena `session_id`
  3. Servidor valida sessão em cada requisição
  4. Sessão expira ou pode ser revogada

## Autorização (RBAC)

- **Server-side obrigatório**: Frontend apenas para UX (guards)
- **Modelo**: Usuário → Roles → Permissions
- **Dependency**: `require_permissions(*codes)` no FastAPI

## Estrutura de Dados

- **User**: email, password_hash, is_active
- **Role**: code (único), name
- **Permission**: code (único), name
- **Session**: user_id, expires_at, revoked_at

## Ambientes

- **DES**: Desenvolvimento local
- **HML**: Homologação (badge visual)
- **PROD**: Produção

Configuração separada por ambiente via variáveis de ambiente (backend) e config.json (frontend).
