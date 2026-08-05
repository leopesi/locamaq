# 📖 LocaMaq — Documentação Completa

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Lógica de Negócio](#lógica-de-negócio)
4. [Instalação Local (Desenvolvimento)](#instalação-local-desenvolvimento)
5. [Deploy em Produção (Hostinger)](#deploy-em-produção-hostinger)
6. [Configuração de Rede](#configuração-de-rede)
7. [Primeiro Acesso](#primeiro-acesso)
8. [Guia do Usuário](#guia-do-usuário)
9. [Administração](#administração)
10. [Integrações](#integrações)
11. [CI/CD (GitHub Actions)](#cicd-github-actions)
12. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O **LocaMaq** é uma plataforma SaaS multi-tenant de gestão de locação de máquinas e equipamentos para construção civil.

**Cliente:** Construara Locadora de Máquinas para Construção Civil — Araguari/MG (desde 1994)

### Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 👥 **Clientes** | Cadastro completo (PF/PJ), endereço entrega/obra, referências, limite de crédito, bloqueio |
| 🔧 **Equipamentos** | Patrimônio individual, estados (disponível/locado/manutenção/baixado), histórico, preços flexíveis |
| 📋 **Locações** | Formulário único com equipamentos, cálculo automático, formas de pagamento, endereço entrega |
| 💰 **Financeiro** | Fluxo de caixa (entradas automáticas na devolução + saídas manuais) |
| 🖨️ **PDF** | Comprovante com cláusulas legais (Código Civil Art. 569/570), pronto para impressão |
| 📱 **WhatsApp** | Envio de comprovantes e mensagens via Evolution API |
| 📢 **Promoções** | Broadcast para clientes selecionados |
| 🔔 **Alertas** | Motor automático (atraso, pagamento pendente, estoque baixo) |
| 🗺️ **Mapa** | Localização das máquinas com ícones SVG por tipo + alertas visuais |
| 🏢 **Multi-tenant** | Várias empresas, dados isolados, login separado |
| 📱 **Responsivo** | Desktop + mobile com sidebar hamburger |
| 📚 **Guia** | Passo a passo interativo para o administrador |

### Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + Django 5.1 |
| Banco | SQLite (volume Docker persistente) |
| Frontend | Django Templates + Tailwind CSS (CDN) |
| Mapa | Leaflet.js + OpenStreetMap |
| PDF | WeasyPrint |
| WhatsApp | Evolution API (self-hosted) |
| Geocodificação | Nominatim (OpenStreetMap) |
| Deploy | Docker + Gunicorn + Nginx |
| CI/CD | GitHub Actions → GHCR → SSH Deploy |
| Hosting | VPS Hostinger (Ubuntu 24.04, 4GB RAM) |

### Infraestrutura

| Recurso | Detalhes |
|---------|----------|
| Servidor | 76.13.66.202 (Hostinger VPS) |
| Repositório | https://github.com/leopesi/locamaq |
| Registry | ghcr.io/leopesi/locamaq |
| Container | locamaq-web (Gunicorn) + locamaq-nginx |
| Volumes | sqlite_data, media_data, static_data, logs_data |

---

## Arquitetura do Sistema

### Estrutura

```
locamaq/
├── config/                     # Settings (base/dev/prod), urls, wsgi
├── apps/
│   ├── core/                  # Cache, exceptions, middleware, signals
│   ├── tenants/               # Multi-tenant, dashboard, landing, settings, guia
│   ├── accounts/              # Auth, perfis, alterar senha
│   ├── customers/             # CRUD clientes (26+ campos)
│   ├── inventory/             # Equipamentos, patrimônio, estados, histórico
│   ├── rentals/               # Locações, devoluções, geocodificação
│   ├── finance/               # Fluxo de caixa
│   ├── documents/             # PDF (comprovantes)
│   ├── notifications/         # WhatsApp (Evolution API)
│   ├── promotions/            # Broadcast
│   └── alerts/                # Motor de alertas + notificações
├── templates/                 # HTML (landing, dashboard, forms, errors)
├── static/                    # Assets
├── nginx/                     # Nginx config
├── .github/workflows/         # CI/CD pipeline
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml         # Dev
└── docker-compose.prod.yml    # Produção (GHCR)
```

### Diagrama de Rede

```
         Internet
            │
     ┌──────▼──────┐
     │    Nginx     │ :80 (futuro :443 com SSL)
     └──────┬──────┘
            │ :8000
     ┌──────▼──────┐
     │   Gunicorn   │ 3 workers + 2 threads
     │  Django App  │
     └──────┬──────┘
            │
    ┌───────┼───────┐
    │       │       │
┌───▼──┐ ┌──▼──┐ ┌──▼───┐
│SQLite│ │Media│ │ Logs │  ← Volumes Docker (persistentes)
└──────┘ └─────┘ └──────┘
```

### Menu do Sistema

```
── Gestão ──────────────
📊 Dashboard (mapa + métricas + alertas + locações recentes)
👥 Clientes
🔧 Equipamentos
📋 Locações
💰 Financeiro
🔔 Notificações

── Administração ───────  (só admin)
📢 Promoções
👥 Usuários
🔔 Config. Alertas
⚙️ Configurações (empresa + WhatsApp)
📚 Guia Passo a Passo

── Conta ───────────────
👤 Meu Perfil (editável + alterar senha)
🚪 Sair
```

---

## Lógica de Negócio

### Ciclo de Vida da Locação

```
Criar → Equipamentos marcados "Locados" → Comprovante PDF/WhatsApp
   ↓
Vigência → Mapa mostra localização → Alertas se atrasar
   ↓
Devolver → Equipamentos voltam "Disponível" → Entrada financeira automática
```

### Formas de Pagamento

À Vista (Dinheiro) | PIX | Cartão de Crédito | Cartão de Débito | A Receber | Transferência

### Cálculo de Valor

```
Período Diária  → equipment.daily_rate × quantidade
Período Semanal → equipment.weekly_rate × quantidade
Período Mensal  → equipment.monthly_rate × quantidade
```

### Cláusulas Contratuais (PDF)

- Baseadas no **Código Civil Brasileiro** (Art. 569, 570)
- Condições de devolução com prazo e vistoria
- Multa: 10% + diária excedente
- Juros: 1% ao mês + 2% multa (CDC Art. 43)
- Foro: Comarca de Araguari/MG

---

## Instalação Local (Desenvolvimento)

```bash
git clone https://github.com/leopesi/locamaq.git
cd locamaq
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

---

## Deploy em Produção (Hostinger)

### Servidor

- **IP:** 76.13.66.202
- **OS:** Ubuntu 24.04 LTS
- **SSH:** root / (senha configurada)
- **Docker:** 29.1.3
- **Path:** /opt/locamaq

### Deploy manual

```bash
ssh root@76.13.66.202
cd /opt
git clone --depth 1 https://github.com/leopesi/locamaq.git locamaq-build
cd locamaq-build && docker build -t ghcr.io/leopesi/locamaq:latest .
cd /opt/locamaq && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d
docker exec locamaq-web python manage.py migrate --noinput
rm -rf /opt/locamaq-build
```

### Persistência

| Dado | Volume Docker | Path no container |
|------|--------------|-------------------|
| Banco SQLite | locamaq_sqlite_data | /app/data/db.sqlite3 |
| Uploads | locamaq_media_data | /app/media/ |
| Static | locamaq_static_data | /app/staticfiles/ |
| Logs | locamaq_logs_data | /app/logs/ |

**Sobrevive:** restart, rebuild, reboot. **Só perde se:** `docker volume rm`.

---

## CI/CD (GitHub Actions)

### Pipeline (`.github/workflows/deploy.yml`)

```
Push main → Testes → Build Docker (GHCR) → SSH Hostinger → docker pull + restart
```

### Secrets necessários

| Secret | Valor |
|--------|-------|
| HOST | 76.13.66.202 |
| SSH_USER | root |
| SSH_KEY | Chave privada SSH |
| SSH_PORT | 22 |

---

## Primeiro Acesso

1. Acesse http://76.13.66.202
2. Clique "Login Administrativo"
3. Use: `douglas.pereira` / `admin123`
4. Siga o **📚 Guia Passo a Passo** no menu

---

## Guia do Usuário

### Operador

- Criar locação (cliente + equipamentos + período + pagamento + entrega)
- Imprimir comprovante (PDF)
- Enviar via WhatsApp
- Registrar devolução
- Registrar despesas no financeiro

### Administrador

- Tudo do operador +
- Gerenciar usuários
- Configurar empresa e cláusulas
- Configurar WhatsApp
- Criar promoções
- Configurar alertas
- Editar perfil e senha

---

## Troubleshooting

### Container não inicia
```bash
docker logs locamaq-web
```

### Banco perdido após rebuild
Verificar se `/app/data/db.sqlite3` existe:
```bash
docker exec locamaq-web ls -la /app/data/
```

### CSRF error no login
Verificar `CSRF_TRUSTED_ORIGINS` em `config/settings/prod.py`

### SSL
Necessita domínio. Opções: Let's Encrypt (Certbot) ou Cloudflare.

---

*Atualizado em 05/08/2026 — LocaMaq v1.0*
