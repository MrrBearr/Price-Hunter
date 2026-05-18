# PriceHunter

Sistema profissional de comparacao de precos estilo Busca + Honey + Zoom.

## Funcionalidades

- Busca de produtos em multiplas lojas (Amazon, Mercado Livre, Shopee)
- Comparacao de precos e frete
- Sistema de score inteligente para ofertas
- Teste automatico de cupons
- Alertas de queda de preco
- Historico de precos com graficos
- Dashboard pessoal com favoritos

## Stack Tecnologica

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Next.js 14, React, TailwindCSS, TypeScript |
| Backend | Python, FastAPI |
| Banco | PostgreSQL 15 |
| Cache/Filas | Redis 7 |
| Scraping | Playwright |
| Deploy | Docker, Docker Compose |

## Inicio Rapido

### Requisitos

- Docker e Docker Compose instalados

### Rodar o projeto

```bash
# Clone o repositorio
git clone <repo-url>
cd Price-Hunter

# Inicie todos os servicos
docker-compose up --build
```

### Acessar

| Servico | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## Arquitetura

```
Price-Hunter/
├── frontend/          # Next.js 14 + TailwindCSS
├── backend/           # FastAPI + SQLAlchemy
├── scraper/           # Playwright scrapers
├── workers/           # Background workers (Redis queues)
├── database/          # SQL schema
└── docker-compose.yml # Orchestracao
```

## API Endpoints

### Auth
- `POST /api/auth/register` - Cadastro
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Usuario atual

### Produtos
- `GET /api/products` - Listar produtos
- `GET /api/products/{id}` - Detalhe do produto
- `GET /api/products/{id}/history` - Historico de precos

### Busca
- `GET /api/search?q=query` - Buscar produtos
- `POST /api/search/trigger?q=query` - Disparar scraping

### Ofertas
- `GET /api/offers/product/{id}` - Ofertas de um produto

### Cupons
- `GET /api/coupons` - Listar cupons
- `POST /api/coupons` - Criar cupom
- `POST /api/coupons/{id}/test` - Testar cupom

### Favoritos
- `GET /api/favorites` - Listar favoritos
- `POST /api/favorites` - Adicionar favorito
- `DELETE /api/favorites/{product_id}` - Remover favorito

### Alertas
- `GET /api/alerts` - Listar alertas
- `POST /api/alerts` - Criar alerta
- `DELETE /api/alerts/{id}` - Remover alerta

## Workers

| Worker | Funcao |
|--------|--------|
| Scraper | Processa fila de scraping |
| PriceUpdater | Re-scrape de ofertas antigas (a cada 1h) |
| AlertWorker | Verifica alertas de preco (a cada 5min) |
| CouponTester | Testa cupons com Playwright |

## Score de Oferta

Algoritmo que pontua ofertas de 0-10:

| Fator | Peso |
|-------|------|
| Preco | 40% |
| Frete | 20% |
| Rating vendedor | 15% |
| Reputacao loja | 15% |
| Desconto | 10% |

## Licenca

MIT
