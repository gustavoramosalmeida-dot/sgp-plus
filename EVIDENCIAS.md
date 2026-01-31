# Evidências de Implementação - SGP+

## Lista de Arquivos Criados

### Estrutura Base
- `README.md` - Documentação principal
- `.gitignore` - Ignorar arquivos do git
- `docs/architecture.md` - Documentação de arquitetura
- `docs/environments.md` - Documentação de ambientes
- `docs/ADR/README.md` - Template para ADRs
- `packages/contracts/README.md` - Documentação do pacote contracts

### Infraestrutura
- `infra/docker/docker-compose.yml` - PostgreSQL via Docker
- `scripts/dev.sh` - Script de desenvolvimento (Linux/Mac)
- `scripts/dev.ps1` - Script de desenvolvimento (Windows)

### CI/CD
- `.github/workflows/ci.yml` - GitHub Actions CI
- `.github/PULL_REQUEST_TEMPLATE.md` - Template de PR

### Backend (apps/api)
- `pyproject.toml` - Dependências Python
- `.env.example` - Exemplo de variáveis de ambiente
- `alembic.ini` - Configuração Alembic
- `alembic/env.py` - Ambiente Alembic
- `alembic/script.py.mako` - Template de migration
- `alembic/versions/0001_initial.py` - Migration inicial

#### Código Backend
- `src/sgp_plus/__init__.py`
- `src/sgp_plus/main.py` - Aplicação FastAPI principal
- `src/sgp_plus/core/config.py` - Configuração via env vars
- `src/sgp_plus/core/security.py` - **Cookie HttpOnly, hash de senha, get_current_user**
- `src/sgp_plus/core/rbac.py` - **RBAC server-side (require_permissions)**
- `src/sgp_plus/db/base.py` - Base SQLAlchemy
- `src/sgp_plus/db/session.py` - Sessão do banco
- `src/sgp_plus/db/models/user.py` - Modelo User
- `src/sgp_plus/db/models/role.py` - Modelo Role
- `src/sgp_plus/db/models/permission.py` - Modelo Permission
- `src/sgp_plus/db/models/session.py` - Modelo Session
- `src/sgp_plus/db/models/associations.py` - Tabelas de associação
- `src/sgp_plus/db/models/__init__.py`
- `src/sgp_plus/db/seed.py` - Script de seed (admin)
- `src/sgp_plus/features/auth/router.py` - Rotas de autenticação
- `src/sgp_plus/features/auth/schemas.py` - Schemas Pydantic
- `src/sgp_plus/features/auth/service.py` - Lógica de negócio
- `src/sgp_plus/features/auth/repository.py` - Acesso a dados
- `src/sgp_plus/shared/errors.py` - Classes de erro
- `src/sgp_plus/shared/utils.py` - Utilitários
- `src/sgp_plus/tests/conftest.py` - Configuração pytest
- `src/sgp_plus/tests/test_health.py` - Testes /health
- `src/sgp_plus/tests/test_auth.py` - Testes de autenticação

### Frontend (apps/web)
- `package.json` - Dependências Node.js
- `tsconfig.json` - Configuração TypeScript
- `tsconfig.node.json` - TypeScript para Node
- `vite.config.ts` - Configuração Vite (PWA-ready)
- `index.html` - HTML principal
- `.eslintrc.cjs` - Configuração ESLint
- `.gitignore` - Ignorar arquivos do git
- `public/config.example.json` - Exemplo de config
- `public/config.json` - Config runtime (dev)
- `public/manifest.webmanifest` - Manifest PWA
- `public/icons/.gitkeep` - Placeholder para ícones

#### Código Frontend
- `src/main.tsx` - Entry point React
- `src/index.css` - Estilos globais
- `src/core/config/loadConfig.ts` - **Loader do config.json (runtime)**
- `src/core/http/client.ts` - **HTTP client com credentials: 'include'**
- `src/core/auth/authApi.ts` - Chamadas API de auth
- `src/core/auth/AuthContext.tsx` - Context de autenticação
- `src/app/routes/App.tsx` - Router principal
- `src/app/guards/RequirePermission.tsx` - Guard RBAC (scaffold)
- `src/features/auth/LoginPage.tsx` - Página de login
- `src/features/auth/LoginPage.css` - Estilos do login
- `src/features/home/HomePage.tsx` - Página home
- `src/features/home/HomePage.css` - Estilos da home
- `src/shared/types/index.ts` - Tipos compartilhados
- `src/shared/utils/index.ts` - Utilitários compartilhados

## Trechos Críticos

### 1. Cookie HttpOnly (security.py)

```python
def set_session_cookie(response: Response, session_id: UUID) -> None:
    """Set HttpOnly session cookie"""
    max_age = settings.session_ttl_minutes * 60
    response.set_cookie(
        key=settings.cookie_name,
        value=str(session_id),
        max_age=max_age,
        httponly=True,  # ✅ HttpOnly
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
    )
```

### 2. Validação de Sessão em DB (security.py)

```python
def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Get current user from session cookie"""
    session_id = request.cookies.get(settings.cookie_name)

    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_uuid = UUID(session_id)
    repository = AuthRepository()
    session = repository.get_valid_session(db, session_uuid)  # ✅ Valida no DB

    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user
```

### 3. RBAC Server-side (rbac.py)

```python
def require_permissions(*permission_codes: str):
    """Dependency to require specific permissions"""
    async def permission_checker(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        # Get user permissions
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.code)

        # Check if user has all required permissions
        required = set(permission_codes)
        missing = required - user_permissions

        if missing:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permissions: {', '.join(missing)}",
            )

        return current_user

    return permission_checker
```

### 4. Loader do Config Runtime (loadConfig.ts)

```typescript
export async function loadConfig(): Promise<AppConfig> {
  if (configCache) {
    return configCache
  }

  try {
    const response = await fetch('/config.json', { cache: 'no-store' })  // ✅ Runtime
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.status}`)
    }
    const config = await response.json()
    configCache = config as AppConfig
    return configCache
  } catch (error) {
    console.error('Failed to load config.json:', error)
    // Fallback config
    const fallback: AppConfig = {
      env: 'DES',
      apiBaseUrl: 'http://localhost:8000',
      showEnvBadge: false,
    }
    return fallback
  }
}
```

### 5. Fetch com Credentials Include (client.ts)

```typescript
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const baseUrl = await getBaseUrl()
  const url = `${baseUrl}${endpoint}`

  const response = await fetch(url, {
    ...options,
    credentials: 'include',  // ✅ Sempre inclui cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (response.status === 401) {
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  return response.json()
}
```

## Comandos para Validação

### 1. Subir PostgreSQL
```bash
cd infra/docker
docker-compose up -d
```

### 2. Rodar Migrations
```bash
cd apps/api
alembic upgrade head
```

### 3. Seed Admin
```bash
cd apps/api
python -m sgp_plus.db.seed
```

### 4. Subir API
```bash
cd apps/api
uvicorn sgp_plus.main:app --reload --port 8000
```

### 5. Subir Web
```bash
cd apps/web
npm install
npm run dev
```

### 6. Testes Backend
```bash
cd apps/api
pytest -v
```

### 7. Build Frontend
```bash
cd apps/web
npm run build
```

### 8. Testar Health
```bash
curl http://localhost:8000/health
# Esperado: {"status":"ok"}
```

## Validação em 2 Minutos

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

3. ✅ `docker-compose up -d` (PostgreSQL)
4. ✅ `alembic upgrade head` (Migrations)

5. **Testar seed com senha >72 bytes (deve falhar):**
   ```powershell
   $env:BOOTSTRAP_ADMIN_PASSWORD = "A" * 73
   python -m sgp_plus.db.seed
   ```
   > Deve falhar com `RuntimeError` mencionando limite de 72 bytes.

6. **Criar admin com senha válida (<=72 bytes):**
   ```powershell
   $env:BOOTSTRAP_ADMIN_PASSWORD = "MinhaS3nhaF0rt3!"
   python -m sgp_plus.db.seed
   ```
   > Deve criar o admin e encerrar com sucesso.

7. ✅ Subir API: `uvicorn sgp_plus.main:app --reload --port 8000`

8. ✅ Validar endpoints:
   ```bash
   curl http://localhost:8000/health
   # Esperado: {"status":"ok"}
   
   curl -i --cookie "sgp_plus_session=not-a-uuid" http://localhost:8000/auth/me
   # Esperado: HTTP 401 (nunca 500)
   
   curl -i http://localhost:8000/admin/ping
   # Esperado: HTTP 401 sem login
   ```

### Validação de Senha >72 Bytes

**Comando PowerShell para checar bytes:**
```powershell
[Text.Encoding]::UTF8.GetByteCount($env:BOOTSTRAP_ADMIN_PASSWORD)
```

**Exemplos:**
- Senha >72 bytes: `python -m sgp_plus.db.seed` → `RuntimeError` com mensagem clara sobre limite.
- Senha <=72 bytes e forte: `python -m sgp_plus.db.seed` → sucesso e criação do admin.

## Características Implementadas

- ✅ Cookies HttpOnly (não usa localStorage/sessionStorage)
- ✅ Validação de sessão em banco de dados
- ✅ RBAC server-side obrigatório
- ✅ Config runtime no frontend (/public/config.json)
- ✅ Credentials: 'include' em todas as requisições
- ✅ Testes automatizados backend
- ✅ CI GitHub Actions
- ✅ Build do frontend funcional
- ✅ Sem segredos no repositório (.env.example)
- ✅ Estrutura de pastas conforme especificado

---

## Hardening (pós-bootstrap) — Arquivos alterados

- `apps/api/src/sgp_plus/core/security.py` — Cookie inválido→401, path no cookie, selectinload
- `apps/api/src/sgp_plus/core/config.py` — COOKIE_PATH, CORS parsing e validação anti-*
- `apps/api/.env.example` — COOKIE_PATH, CORS_ORIGINS
- `apps/api/src/sgp_plus/tests/test_auth.py` — teste cookie inválido
- `apps/api/src/sgp_plus/tests/test_config.py` — **novo** teste CORS * rejeitado
- `.github/workflows/ci.yml` — COOKIE_PATH no env dos testes
- `apps/web/src/core/http/client.ts` — tratamento 204 / content-length 0
- `docs/ADR/0001_auth_cookie_httpOnly_csrf.md` — **novo** ADR auth/cookie/CSRF

### Trechos críticos (hardening)

**1) try/except UUID em get_current_user (security.py)**  
```python
try:
    session_uuid = UUID(session_id)
except (ValueError, TypeError):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
```

**2) set_cookie com path e delete_cookie com path/domain iguais (security.py)**  
```python
# set_session_cookie
response.set_cookie(
    ...
    path=settings.cookie_path,
)
# clear_session_cookie
response.delete_cookie(
    key=settings.cookie_name,
    path=settings.cookie_path,
    domain=settings.cookie_domain,
    httponly=True,
    secure=settings.cookie_secure,
    samesite=settings.cookie_samesite,
)
```

**3) CORSMiddleware + validação anti-* (config.py + main.py)**  
- `main.py`: `allow_origins=settings.cors_origins`, `allow_credentials=True`, métodos/headers conforme já existente.
- `config.py`: `@model_validator(mode="after")` chama `_parse_cors_origins` e, se `"*" in self.cors_origins`, levanta  
  `ValueError("CORS_ORIGINS cannot contain '*' when allow_credentials=True (cookie auth).")`.

**4) User com selectinload roles/perms (security.py)**  
```python
user = (
    db.query(User)
    .filter(User.id == session.user_id)
    .options(
        selectinload(User.roles).selectinload(Role.permissions),
    )
    .first()
)
```

### Validação rápida pós-hardening

- `pytest -q` no backend: todos os testes passando (incl. cookie inválido 401 e CORS * rejeitado).
- `curl -i --cookie "sgp_plus_session=not-a-uuid" http://localhost:8000/auth/me` → HTTP 401, body `{"detail":"Not authenticated"}`.
- Logout: após logout, cookie removido (path="/"), e `/auth/me` retorna 401 sem refresh manual.
- `npm run build` no front: build ok.

---

## Auditoria 001 — Patch de Conformidade (admin default, lixo, logout, RBAC)

### Arquivos alterados

- `apps/api/src/sgp_plus/core/config.py` — `bootstrap_admin_password` default `"CHANGE_ME"`
- `apps/api/.env.example` — `BOOTSTRAP_ADMIN_PASSWORD=CHANGE_ME` e comentário “obrigatório trocar”
- `apps/api/src/sgp_plus/db/seed.py` — validação insegura antes de criar admin; `_block_insecure_bootstrap`
- `apps/api/src/sgp_plus/features/auth/router.py` — logout rastreável: `ValueError` pass, `Exception` com `logger.exception`
- `apps/api/src/sgp_plus/main.py` — rota `GET /admin/ping` protegida por `require_permissions("rbac.manage")`
- `apps/api/src/sgp_plus/tests/conftest.py` — fixture `test_user` centralizada
- `apps/api/src/sgp_plus/tests/test_auth.py` — remoção da fixture duplicada `test_user`
- `apps/api/src/sgp_plus/tests/test_rbac.py` — **novo** testes `/admin/ping`: 403 sem permissão, 200 com admin
- `README.md` — validação seed (falha sem senha / ok com senha) e checagem RBAC
- `.gitignore` — já cobre `.idea/`; se `.idea` estiver tracked: `git rm -r --cached .idea` (na raiz do repo)

### Trechos críticos

**1) Validação do seed — senha insegura (seed.py)**  
```python
INSECURE_PASSWORDS = frozenset({"", "admin123", "CHANGE_ME"})

def _block_insecure_bootstrap(*, password: str, email: str) -> None:
    if (password or "").strip() in INSECURE_PASSWORDS:
        raise RuntimeError(
            "Bootstrap admin com senha insegura ou padrão. "
            "Defina BOOTSTRAP_ADMIN_PASSWORD no .env com valor forte (não use admin123 nem CHANGE_ME)."
        )
```
Chamada antes de criar o usuário admin: `_block_insecure_bootstrap(password=..., email=...)`.

**2) Logout rastreável (router.py)**  
```python
except ValueError:
    pass  # Invalid UUID, ignora
except Exception:
    logger.exception("logout: falha ao revogar sessão no DB")
```
Logout continua retornando 200 e limpando o cookie; apenas erros inesperados são logados.

**3) Rota RBAC (main.py)**  
```python
@app.get("/admin/ping")
async def admin_ping(_=Depends(require_permissions("rbac.manage"))):
    return {"ok": True}
```

### Comandos de validação (Auditoria 001)

- Postgres: `docker-compose up -d` (em `infra/docker`).
- API: `alembic upgrade head`.
- Seed sem senha configurada → deve falhar:
  - Sem alterar `BOOTSTRAP_ADMIN_PASSWORD` (ou com `CHANGE_ME`/`admin123`) → `python -m sgp_plus.db.seed` → `RuntimeError` com mensagem clara.
- Seed com senha configurada → ok:
  - `BOOTSTRAP_ADMIN_PASSWORD=MinhaS3nhaF0rt3` no `.env` → `python -m sgp_plus.db.seed` → “✅ Seed completed successfully!”.
- `curl http://localhost:8000/health` → `{"status":"ok"}`.
- `curl -i --cookie "sgp_plus_session=not-a-uuid" http://localhost:8000/auth/me` → 401.
- RBAC: sem cookie → `GET /admin/ping` → 401; com usuário sem `rbac.manage` → 403; com admin (ex.: após seed) → 200 `{"ok":true}`.
- CI: `ruff check .`, `pytest -v`, `npm run build`.

---

## Patch — Hatch Editable + Validação Senha >72 Bytes

### Arquivos alterados

- `apps/api/pyproject.toml` — `build-system.requires` inclui `editables>=0.5` para garantir editable install com build isolation
- `apps/api/src/sgp_plus/core/security.py` — validação de 72 bytes UTF-8 antes de chamar bcrypt em `hash_password`
- `apps/api/src/sgp_plus/db/seed.py` — tratamento de `ValueError` de senha >72 bytes com mensagem didática
- `apps/api/src/sgp_plus/tests/test_security_password_policy.py` — **novo** testes automatizados para validação de senha
- `README.md` — atualizado com "Como validar em 2 minutos" incluindo editable install e validação de senha >72 bytes
- `EVIDENCIAS.md` — atualizado com seção de validação de senha >72 bytes

### Trechos críticos

**1) Validação de 72 bytes em hash_password (security.py)**  
```python
def hash_password(password: str) -> str:
    """Hash a password"""
    password_bytes = len(password.encode("utf-8"))
    if password_bytes > 72:
        raise ValueError(
            "Password too long for bcrypt (max 72 bytes). "
            "Use a shorter password or adjust policy."
        )
    return pwd_context.hash(password)
```

**2) Tratamento no seed (seed.py)**  
```python
try:
    password_hash = hash_password(settings.bootstrap_admin_password)
except ValueError as e:
    raise RuntimeError(
        f"BOOTSTRAP_ADMIN_PASSWORD excede o limite de 72 bytes (UTF-8) do bcrypt. "
        f"Use uma senha mais curta. Detalhes: {e}"
    ) from e
```

**3) Build system com editables (pyproject.toml)**  
```toml
[build-system]
requires = ["hatchling>=1.22", "editables>=0.5"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/sgp_plus"]
```

**4) Teste automatizado (test_security_password_policy.py)**  
```python
def test_hash_password_rejects_password_over_72_bytes():
    """Test that hash_password raises ValueError for passwords >72 bytes"""
    long_password = "A" * 73  # 73 bytes
    with pytest.raises(ValueError, match="Password too long for bcrypt"):
        hash_password(long_password)
```

### Validação rápida

- `pip install -e .` no venv: deve concluir sem erro de "editables" ou heurística de arquivos.
- `python -c "import sgp_plus; print(sgp_plus.__file__)"`: deve apontar para `...\apps\api\src\sgp_plus\__init__.py`.
- `pytest -q`: deve passar incluindo testes de validação de senha >72 bytes.
- Seed com senha >72 bytes: `python -m sgp_plus.db.seed` → `RuntimeError` com mensagem clara.
- Seed com senha <=72 bytes: `python -m sgp_plus.db.seed` → sucesso.

---

## Patch — Fix Dependências bcrypt/passlib + Tratamento de Erros Melhorado

### Arquivos alterados

- `apps/api/pyproject.toml` — fixado `passlib[bcrypt]==1.7.4` e adicionado `bcrypt>=4.3.0,<5` para eliminar warning "(trapped) error reading bcrypt version"
- `apps/api/src/sgp_plus/db/seed.py` — tratamento de erros melhorado para distinguir entre erro de 72 bytes vs erro de backend incompatível
- `EVIDENCIAS.md` — atualizado com outputs de validação e comandos de verificação

### Trechos críticos

**1) Dependências fixadas (pyproject.toml)**  
```toml
dependencies = [
    ...
    "passlib[bcrypt]==1.7.4",
    "bcrypt>=4.3.0,<5",
    ...
]
```

**2) Tratamento de erros melhorado no seed (seed.py)**  
```python
try:
    password_hash = hash_password(settings.bootstrap_admin_password)
except ValueError as e:
    # Distinguir entre erro de 72 bytes vs erro de backend
    error_msg = str(e)
    if "72 bytes" in error_msg or "too long" in error_msg.lower():
        raise RuntimeError(
            f"BOOTSTRAP_ADMIN_PASSWORD excede o limite de 72 bytes (UTF-8) do bcrypt. "
            f"Use uma senha mais curta. Detalhes: {e}"
        ) from e
    else:
        # Erro de backend/versionamento
        raise RuntimeError(
            f"Erro ao processar senha: {error_msg}. "
            f"Verifique compatibilidade: bcrypt>=4.3.0,<5 é necessário com passlib==1.7.4. "
            f"Se usar bcrypt>=5, ele é incompatível com passlib 1.7.4 — use bcrypt<5."
        ) from e
except Exception as e:
    # Outros erros de backend (ex: AttributeError ao acessar bcrypt.__about__)
    error_type = type(e).__name__
    if "bcrypt" in str(e).lower() or "passlib" in str(e).lower():
        raise RuntimeError(
            f"Erro de backend ao processar senha ({error_type}): {e}. "
            f"Verifique compatibilidade: bcrypt>=4.3.0,<5 é necessário com passlib==1.7.4. "
            f"Se usar bcrypt>=5, ele é incompatível com passlib 1.7.4 — use bcrypt<5."
        ) from e
    raise
```

### Validação rápida

**1) Verificar versões instaladas:**
```powershell
python -c "import bcrypt, passlib; print('bcrypt', bcrypt.__version__); print('passlib', passlib.__version__)"
```
**Esperado:**
```
bcrypt 4.x.x
passlib 1.7.4
```

**2) Rodar seed sem warning:**
```powershell
$env:BOOTSTRAP_ADMIN_PASSWORD="Adria1x"
python -m sgp_plus.db.seed
```
**Esperado:**
- Sem warning "(trapped) error reading bcrypt version"
- "✅ Seed completed successfully!"

**3) Testar erro de 72 bytes:**
```powershell
$env:BOOTSTRAP_ADMIN_PASSWORD = "A" * 73
python -m sgp_plus.db.seed
```
**Esperado:**
- `RuntimeError` com mensagem específica sobre limite de 72 bytes
- Não menciona incompatibilidade de backend

**4) Testes automatizados:**
```powershell
pytest -q
```
**Esperado:**
- Todos os testes passando
- Sem warnings relacionados a bcrypt/passlib
