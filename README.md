<<<<<<< HEAD
# SGP+

Sistema de Gestão de Processos Plus - Versão Web

## Stack

- **Frontend**: React + TypeScript + Vite (PWA-ready)
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy + Alembic
- **Database**: PostgreSQL
- **Auth**: Cookies HttpOnly (session-based)
- **RBAC**: Server-side obrigatório

## Estrutura do Projeto

```
sgp-plus/
├── apps/
│   ├── api/          # Backend FastAPI
│   └── web/          # Frontend React
├── infra/
│   └── docker/       # Docker Compose
├── scripts/          # Scripts de desenvolvimento
└── docs/             # Documentação
```

## Como Rodar Local

### Pré-requisitos

- Python 3.12+
- Node.js 18+
- Docker e Docker Compose
- PostgreSQL (via Docker)

### Passos

1. **Subir PostgreSQL via Docker Compose:**
   ```bash
   cd infra/docker
   docker-compose up -d
   ```

2. **Configurar variáveis de ambiente (API):**
   ```bash
   cd apps/api
   cp .env.example .env
   # Editar .env com valores apropriados
   ```

3. **Rodar migrations:**
   ```bash
   cd apps/api
   alembic upgrade head
   ```

4. **Instalar pacote em modo editable:**
   ```bash
   cd apps/api
   pip install -e .
   ```
   > O projeto declara `editables>=0.5` no `build-system.requires`, então o editable install funciona mesmo com build isolation.

5. **Criar usuário admin (seed):**
   - Defina `BOOTSTRAP_ADMIN_PASSWORD` no `.env` com valor forte (não use `admin123` nem `CHANGE_ME`).
   - **Importante**: `BOOTSTRAP_ADMIN_PASSWORD` deve ter no máximo 72 bytes (UTF-8) por limitação do bcrypt.
   ```bash
   cd apps/api
   python -m sgp_plus.db.seed
   ```
   > Seed falha se a senha for vazia, `admin123`, `CHANGE_ME` ou exceder 72 bytes UTF-8.

6. **Subir API:**
   ```bash
   cd apps/api
   uvicorn sgp_plus.main:app --reload --port 8000
   ```

7. **Subir Web:**
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```

7. **Acessar:**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Como Validar em 2 Minutos

1. **Ativar venv e instalar dependências:**
   ```powershell
   Set-Location -LiteralPath "C:\Users\gustavoalmeida\Documents\SGPbeta\sgp-plus\apps\api"
   .\.venv\Scripts\Activate.ps1
   pip install -U pip hatchling wheel
   pip install -e .
   ```

2. **Verificar import do pacote:**
   ```powershell
   python -c "import sgp_plus; print(sgp_plus.__file__)"
   ```
   > Deve apontar para `...\apps\api\src\sgp_plus\__init__.py`

3. **Subir infraestrutura:**
   ```bash
   cd infra/docker
   docker-compose up -d
   ```

4. **Rodar migrations:**
   ```bash
   cd apps/api
   alembic upgrade head
   ```

5. **Testar seed com senha >72 bytes (deve falhar):**
   ```powershell
   # No PowerShell, definir senha >72 bytes
   $env:BOOTSTRAP_ADMIN_PASSWORD = "A" * 73
   python -m sgp_plus.db.seed
   ```
   > Deve falhar com `RuntimeError` mencionando limite de 72 bytes e `BOOTSTRAP_ADMIN_PASSWORD`.

6. **Criar admin com senha válida (<=72 bytes):**
   ```powershell
   # Definir senha forte e válida (<=72 bytes)
   $env:BOOTSTRAP_ADMIN_PASSWORD = "MinhaS3nhaF0rt3!"
   python -m sgp_plus.db.seed
   ```
   > Deve criar o admin e encerrar com "✅ Seed completed successfully!".

7. **Subir API:**
   ```bash
   cd apps/api
   uvicorn sgp_plus.main:app --reload --port 8000
   ```

8. **Validar endpoints:**
   ```bash
   curl http://localhost:8000/health
   # Esperado: {"status":"ok"}
   ```

9. **Validar autenticação:**
   ```bash
   curl -i --cookie "sgp_plus_session=not-a-uuid" http://localhost:8000/auth/me
   # Esperado: HTTP 401 (nunca 500)
   
   curl -i http://localhost:8000/admin/ping
   # Esperado: HTTP 401 sem login
   ```

## Ambientes

- **DES**: Desenvolvimento local
- **HML**: Homologação (com badge "HML" no frontend)
- **PROD**: Produção

Configuração por ambiente via:
- Backend: variáveis de ambiente (.env)
- Frontend: `/public/config.json` (runtime)

## Testes

### Backend
```bash
cd apps/api
pytest
```

### Frontend
```bash
cd apps/web
npm run build
```

## CI/CD

GitHub Actions roda automaticamente:
- Lint e testes do backend (obrigatório)
- Build do frontend

## Repo limpo

- `.gitignore` já cobre `.idea/` e `.vscode/`. Se `.idea` estiver trackeado, na raiz do repositório rode:  
  `git rm -r --cached .idea`

## Segurança

- ✅ Cookies HttpOnly (não usa localStorage/sessionStorage)
- ✅ RBAC server-side obrigatório
- ✅ Validação de sessão em banco de dados
- ✅ Sem segredos no repositório (tudo via .env)
=======
# sgp-plus
>>>>>>> 77e270341c9752c7f0354882eab53ddbb5195caa
