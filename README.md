# LocaMaq — Gestão de Locação de Máquinas

Plataforma SaaS para controle de estoque, locações, fluxo de caixa e comunicação via WhatsApp.

## Stack

- **Backend:** Python 3.12 + Django 5.1
- **Banco:** SQLite
- **Frontend:** Django Templates + Tailwind CSS (CDN)
- **WhatsApp:** Evolution API
- **Deploy:** Docker + Nginx + Gunicorn

## Setup Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env

# Executar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

## Docker (Dev)

```bash
docker-compose up --build
```

## Docker (Produção - Hostinger)

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## Estrutura do Projeto

```
locamaq/
├── config/          # Settings, URLs, WSGI/ASGI
├── apps/
│   ├── tenants/     # Multi-tenant
│   ├── accounts/    # Auth + Perfis
│   ├── customers/   # Clientes
│   ├── inventory/   # Equipamentos
│   ├── rentals/     # Locações
│   ├── finance/     # Fluxo de Caixa
│   ├── documents/   # PDF
│   ├── notifications/ # WhatsApp
│   └── promotions/  # Broadcast
├── templates/       # HTML
├── static/          # Assets
├── Dockerfile
└── docker-compose.yml
```
