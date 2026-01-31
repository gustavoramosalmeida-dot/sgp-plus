# Ambientes

## Desenvolvimento (DES)

- **Database**: `sgp_plus_des` (PostgreSQL local via Docker)
- **API**: http://localhost:8000
- **Web**: http://localhost:5173
- **Config**: `.env` local + `config.json` no frontend

## Homologação (HML)

- **Database**: `sgp_plus_hml` (RDS ou container separado)
- **API**: URL configurada via env
- **Web**: URL configurada via deploy
- **Badge**: Exibe "HML" no frontend quando `env === "HML"`

## Produção (PROD)

- **Database**: RDS PostgreSQL
- **API**: URL de produção
- **Web**: URL de produção
- **Segurança**: Cookies Secure, HTTPS obrigatório

## Variáveis de Ambiente (Backend)

Ver `apps/api/.env.example` para lista completa.

Principais:
- `SGP_PLUS_ENV`: des|hml|prod
- `DATABASE_URL`: Connection string PostgreSQL
- `COOKIE_SECURE`: true em produção
- `CORS_ORIGINS`: Lista de origens permitidas

## Config Frontend (Runtime)

Arquivo `/public/config.json`:
```json
{
  "env": "DES",
  "apiBaseUrl": "http://localhost:8000",
  "showEnvBadge": true
}
```

Carregado em runtime via `fetch("/config.json")`.
