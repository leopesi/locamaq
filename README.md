# 🏗️ LocaMaq — Plataforma SaaS de Gestão de Locação de Máquinas

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)

Plataforma multi-tenant para empresas de locação de máquinas e equipamentos (andaimes, betoneiras, compactadores, geradores, etc.) com controle de estoque, fluxo de caixa, emissão de comprovante PDF, comunicação via WhatsApp e mapa de localização em tempo real.

---

## 📸 Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 👥 **Clientes** | Cadastro completo (PF/PJ), endereço de entrega, referências, limite de crédito, bloqueio |
| 🔧 **Equipamentos** | Patrimônio individual, estados (disponível/locado/manutenção/baixado), histórico, tabela de preços |
| 📋 **Locações** | Formulário único, cálculo automático, formas de pagamento, endereço de entrega com geocodificação |
| 💰 **Financeiro** | Fluxo de caixa (entradas/saídas), transações automáticas na devolução, filtro por período |
| 🖨️ **Comprovante PDF** | Documento completo com cláusulas legais, pronto para impressão e envio |
| 📱 **WhatsApp** | Envio de comprovantes e mensagens via Evolution API (self-hosted) |
| 📢 **Promoções** | Broadcast de ofertas para clientes selecionados |
| 🔔 **Alertas** | Motor automático de notificações (atraso, pagamento pendente, estoque baixo) |
| 🗺️ **Mapa** | Visualização geográfica das máquinas locadas com ícones SVG por tipo |
| 🏢 **Multi-tenant** | Múltiplas empresas no mesmo sistema, dados completamente isolados |
| 📱 **Responsivo** | Interface adaptada para desktop e mobile |

---

## 🛠️ Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + Django 5.1 |
| Banco de Dados | SQLite |
| Frontend | Django Templates (SSR) + Tailwind CSS |
| Mapa | Leaflet.js + OpenStreetMap |
| PDF | WeasyPrint |
| WhatsApp | Evolution API |
| Geocodificação | Nominatim (OpenStreetMap) |
| Deploy | Docker + Gunicorn + Nginx |

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+
- pip

### Instalação

```bash
# Clonar
git clone https://github.com/leopesi/locamaq.git
cd locamaq

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dependências
pip install -r requirements.txt

# Configuração
cp .env.example .env

# Banco de dados
python manage.py migrate

# Superusuário
python manage.py createsuperuser

# Rodar
python manage.py runserver 0.0.0.0:8000
```

Acesse: http://localhost:8000

### Docker

```bash
# Desenvolvimento
docker-compose up --build

# Produção
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📁 Estrutura do Projeto

```
locamaq/
├── config/                     # Configurações Django (settings, urls, wsgi)
│   └── settings/              # Split: base.py, dev.py, prod.py
├── apps/
│   ├── core/                  # Utilitários (cache, exceptions, middleware)
│   ├── tenants/               # Multi-tenant, dashboard, configurações
│   ├── accounts/              # Autenticação, perfis (Admin/Operador)
│   ├── customers/             # CRUD de clientes (PF/PJ)
│   ├── inventory/             # Equipamentos, patrimônio, estados
│   ├── rentals/               # Locações, devoluções, geocodificação
│   ├── finance/               # Fluxo de caixa
│   ├── documents/             # Geração de PDF (comprovantes)
│   ├── notifications/         # WhatsApp (Evolution API)
│   ├── promotions/            # Broadcast de promoções
│   └── alerts/                # Motor de alertas + notificações
├── templates/                 # HTML (Tailwind CSS)
├── static/                    # Assets
├── nginx/                     # Config Nginx (produção)
├── Dockerfile                 # Build
├── docker-compose.yml         # Dev
├── docker-compose.prod.yml    # Produção
├── DOCUMENTACAO.md            # Documentação completa
└── PLANO_IMPLEMENTACAO.md     # Plano original do projeto
```

---

## 🔐 Perfis de Acesso

| Recurso | Admin | Operador |
|---------|:-----:|:--------:|
| Dashboard + Mapa | ✅ | ✅ |
| Clientes (CRUD) | ✅ | ✅ |
| Equipamentos (CRUD) | ✅ | ✅ |
| Locações (CRUD + PDF) | ✅ | ✅ |
| Financeiro | ✅ | ✅ |
| WhatsApp (envio) | ✅ | ✅ |
| Promoções | ✅ | ❌ |
| Usuários | ✅ | ❌ |
| Configurações | ✅ | ❌ |
| Alertas (config) | ✅ | ❌ |

---

## 🗺️ Mapa Interativo

O dashboard exibe um mapa com a localização real de todas as máquinas locadas:

- Ícones SVG por tipo de equipamento (andaime, betoneira, gerador, etc.)
- Alertas visuais para locações atrasadas (🚨) e com pendências (⚠️)
- Popup com detalhes ao clicar no marcador
- Modo tela inteira
- Geocodificação automática ao cadastrar endereço de entrega

---

## 📄 Documentação

- [📖 Documentação Completa](DOCUMENTACAO.md) — Arquitetura, lógica de negócio, instalação, deploy, guia do usuário
- [📋 Plano de Implementação](PLANO_IMPLEMENTACAO.md) — Requisitos e task breakdown original

---

## 🐳 Deploy (Produção)

```bash
# No servidor (Hostinger ou qualquer VPS com Docker)
git clone https://github.com/leopesi/locamaq.git
cd locamaq
cp .env.example .env
# Edite .env com SECRET_KEY forte e ALLOWED_HOSTS

docker-compose -f docker-compose.prod.yml up -d --build
docker exec -it locamaq-web python manage.py migrate
docker exec -it locamaq-web python manage.py createsuperuser
```

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

---

## 👤 Autor

**Leonardo Pesi** — [@leopesi](https://github.com/leopesi)
