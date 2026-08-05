# 📖 LocaMaq — Documentação Completa

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Lógica de Negócio](#lógica-de-negócio)
4. [Instalação Local (Desenvolvimento)](#instalação-local-desenvolvimento)
5. [Deploy em Produção (Docker + Hostinger)](#deploy-em-produção-docker--hostinger)
6. [Configuração de Rede](#configuração-de-rede)
7. [Primeiro Acesso](#primeiro-acesso)
8. [Guia do Usuário](#guia-do-usuário)
9. [Administração](#administração)
10. [Integrações](#integrações)
11. [Troubleshooting](#troubleshooting)

---

## Visão Geral

O **LocaMaq** é uma plataforma SaaS multi-tenant de gestão de locação de máquinas e equipamentos (andaimes, betoneiras, compactadores, geradores, etc.).

### Funcionalidades Principais

| Módulo | Descrição |
|--------|-----------|
| **Clientes** | Cadastro completo (PF/PJ), endereço, referências, limite de crédito |
| **Equipamentos** | Patrimônio individual, estados, histórico, tabela de preços (diária/semanal/mensal) |
| **Locações** | Criação completa em tela única, cálculo automático, endereço de entrega, forma de pagamento |
| **Financeiro** | Fluxo de caixa (entradas/saídas), transações automáticas na devolução |
| **Comprovante PDF** | Geração de comprovante com cláusulas legais, pronto para impressão |
| **WhatsApp** | Envio manual de comprovantes e mensagens via Evolution API |
| **Promoções** | Broadcast de promoções para clientes selecionados |
| **Notificações** | Alertas automáticos (atraso, pagamento pendente, estoque baixo) |
| **Mapa** | Visualização geográfica das máquinas locadas com ícones por tipo |
| **Multi-tenant** | Várias empresas usando o mesmo sistema, dados completamente isolados |

### Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + Django 5.1 |
| Banco de Dados | SQLite (produção com volume Docker) |
| Frontend | Django Templates (SSR) + Tailwind CSS (CDN) |
| Mapa | Leaflet.js + OpenStreetMap (gratuito) |
| PDF | WeasyPrint |
| WhatsApp | Evolution API (self-hosted) |
| Cache | FileBasedCache |
| Deploy | Docker + Gunicorn + Nginx |
| Geocodificação | Nominatim / OpenStreetMap |

---

## Arquitetura do Sistema

### Estrutura de Diretórios

```
locamaq/
├── config/                     # Configurações Django
│   ├── settings/
│   │   ├── base.py            # Settings compartilhados
│   │   ├── dev.py             # Desenvolvimento (DEBUG=True)
│   │   └── prod.py            # Produção (segurança)
│   ├── urls.py                # Roteamento principal
│   ├── views.py               # Error handlers (403, 404, 500)
│   ├── wsgi.py / asgi.py      # Entry points
│   └── logging.py             # Configuração de logs
├── apps/
│   ├── core/                  # Utilitários: cache, exceptions, middleware
│   ├── tenants/               # Multi-tenant, dashboard, configurações
│   ├── accounts/              # Autenticação, perfis (Admin/Operador)
│   ├── customers/             # CRUD de clientes
│   ├── inventory/             # Equipamentos, patrimônio, estados
│   ├── rentals/               # Locações, devoluções, geocodificação
│   ├── finance/               # Fluxo de caixa
│   ├── documents/             # Geração de PDF
│   ├── notifications/         # WhatsApp (Evolution API)
│   ├── promotions/            # Broadcast de promoções
│   └── alerts/                # Motor de alertas + notificações
├── templates/                 # HTML (base, partials, por app)
├── static/                    # CSS, JS, imagens
├── media/                     # Uploads (logos, imagens de equipamentos)
├── logs/                      # Logs do sistema (rotacionados)
├── cache/                     # Cache em arquivo
├── nginx/                     # Config do Nginx (produção)
├── Dockerfile                 # Build da aplicação
├── docker-compose.yml         # Dev
├── docker-compose.prod.yml    # Produção
└── requirements.txt           # Dependências Python
```

### Diagrama de Rede (Produção)

```
                    ┌─────────────────┐
                    │    Internet     │
                    └────────┬────────┘
                             │ :80/:443
                    ┌────────▼────────┐
                    │      Nginx      │
                    │  (reverse proxy)│
                    └────────┬────────┘
                             │ :8000
                    ┌────────▼────────┐
                    │    Gunicorn     │
                    │  (3 workers)    │
                    │  Django App     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───┐  ┌──────▼─────┐  ┌────▼──────┐
     │   SQLite   │  │  Evolution │  │ Nominatim │
     │  (volume)  │  │    API     │  │  (externo)│
     └────────────┘  └────────────┘  └───────────┘
```

### Modelo de Dados (Principais Entidades)

```
Tenant ──┬── User (Admin/Operador)
         ├── Customer (PF/PJ)
         ├── Equipment (patrimônio, estados)
         ├── Rental ──── RentalItem (equipamentos na locação)
         ├── Transaction (entradas/saídas)
         ├── Notification (alertas do sistema)
         ├── AlertRule (configurações de alerta)
         └── Promotion (broadcast WhatsApp)
```

### Fluxo Multi-Tenant

```
Login → Middleware identifica tenant via user.tenant → 
Todas queries filtram por tenant → Dados isolados por empresa
```

---

## Lógica de Negócio

### Ciclo de Vida de uma Locação

```
1. CRIAÇÃO
   Operador seleciona: Cliente + Equipamentos + Período + Pagamento + Entrega
   → Equipamentos marcados como "Locados"
   → Valor calculado automaticamente pela tabela de preços
   → Endereço geocodificado (lat/lng) para o mapa
   → Comprovante disponível para impressão/WhatsApp

2. VIGÊNCIA
   → Locação aparece no dashboard e no mapa
   → Se atrasar: alerta gerado automaticamente
   → Se pagamento pendente: alerta gerado
   → Operador pode editar dados, adicionar equipamentos

3. DEVOLUÇÃO
   Operador registra devolução
   → Equipamentos voltam para "Disponível"
   → Transação financeira (entrada) criada automaticamente
   → Status muda para "Devolvida"

4. CANCELAMENTO (alternativo)
   → Equipamentos liberados
   → Nenhuma transação gerada
   → Status muda para "Cancelada"
```

### Estados do Equipamento

```
┌───────────┐    Locação    ┌─────────┐
│ Disponível├──────────────►│  Locado │
└─────┬─────┘               └────┬────┘
      │                          │
      │ Manutenção    Devolução │
      │                          │
┌─────▼──────┐                   │
│ Manutenção │◄──────────────────┘
└─────┬──────┘       (volta disponível)
      │
      │ Baixa
┌─────▼──────┐
│   Baixado  │ (retirado de circulação)
└────────────┘
```

### Cálculo de Valor

```
Valor Total = Σ (valor_unitário × quantidade) para cada item

Se valor_unitário não informado:
  - Período Diária  → usa equipment.daily_rate
  - Período Semanal → usa equipment.weekly_rate
  - Período Mensal  → usa equipment.monthly_rate
```

### Motor de Alertas

```
Regra configurada pelo Admin:
  Tipo + Severidade + Threshold + Canal (Sistema/WhatsApp)

Engine verifica periodicamente (ou manualmente):
  - Locações atrasadas (dias > threshold)
  - Equipamentos em manutenção (dias > threshold)
  - Poucos disponíveis (qtd < threshold)
  - Pagamentos pendentes (dias > threshold)
  - Despesas altas (valor > threshold)

Resultado: Notificação criada + WhatsApp (se configurado)
```

### Sistema de Cache

```
Dashboard stats → cacheados 60s
Invalidação → automática via @invalidate_on_write nas views de escrita
Escopo → por tenant (empresas não compartilham cache)
```

---

## Instalação Local (Desenvolvimento)

### Pré-requisitos

- Python 3.12+
- pip
- Git

### Passo a Passo

```bash
# 1. Clonar o projeto
git clone <repositorio> locamaq
cd locamaq

# 2. Criar ambiente virtual
python -m venv venv

# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações (SECRET_KEY, etc.)

# 5. Criar banco de dados
python manage.py migrate

# 6. Criar superusuário
python manage.py createsuperuser

# 7. Rodar servidor
python manage.py runserver 0.0.0.0:8000

# 8. Acessar
# http://localhost:8000
```

### Variáveis de Ambiente (.env)

```env
SECRET_KEY=sua-chave-secreta-aqui-minimo-50-caracteres
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Evolution API (WhatsApp) — opcional para dev
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-api-key
EVOLUTION_INSTANCE=locamaq
```

---

## Deploy em Produção (Docker + Hostinger)

### Pré-requisitos no Servidor

- Docker + Docker Compose
- Domínio apontando para o IP do servidor
- Porta 80 e 443 liberadas

### Passo a Passo

```bash
# 1. Transferir projeto para o servidor
scp -r locamaq/ user@servidor:/opt/locamaq
# ou via git clone

# 2. Acessar o servidor
ssh user@servidor
cd /opt/locamaq

# 3. Configurar .env de produção
cp .env.example .env
nano .env
```

**.env de produção:**

```env
SECRET_KEY=gere-uma-chave-forte-com-50-caracteres-ou-mais
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

EVOLUTION_API_URL=http://evolution:8080
EVOLUTION_API_KEY=sua-api-key
EVOLUTION_INSTANCE=locamaq
```

```bash
# 4. Build e start
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Criar banco e superusuário
docker exec -it locamaq-web python manage.py migrate
docker exec -it locamaq-web python manage.py createsuperuser

# 6. Coletar arquivos estáticos
docker exec -it locamaq-web python manage.py collectstatic --noinput

# 7. Verificar se está rodando
curl http://localhost/accounts/login/
```

### Atualizar em Produção

```bash
cd /opt/locamaq
git pull
docker-compose -f docker-compose.prod.yml up -d --build
docker exec -it locamaq-web python manage.py migrate
```

### SSL (HTTPS)

Para SSL, configure o Certbot ou Cloudflare:

```bash
# Com Certbot
apt install certbot python3-certbot-nginx
certbot --nginx -d seudominio.com
```

### Backup

```bash
# Backup do banco SQLite
docker cp locamaq-web:/app/data/db.sqlite3 ./backup_$(date +%Y%m%d).sqlite3

# Backup completo (banco + media)
tar -czf backup_locamaq_$(date +%Y%m%d).tar.gz \
  /var/lib/docker/volumes/locamaq_sqlite_data \
  /var/lib/docker/volumes/locamaq_media_data
```

### Estrutura Docker (Produção)

```
docker-compose.prod.yml
├── web (Django + Gunicorn, 3 workers)
│   ├── Volume: sqlite_data (banco)
│   ├── Volume: media_data (uploads)
│   └── Volume: static_data (CSS/JS)
└── nginx (reverse proxy)
    ├── Porta 80 → Gunicorn :8000
    └── Serve /static/ e /media/ diretamente
```

---

## Configuração de Rede

### Portas Necessárias

| Serviço | Porta | Protocolo | Descrição |
|---------|-------|-----------|-----------|
| Nginx | 80 | TCP | HTTP (redireciona para HTTPS) |
| Nginx | 443 | TCP | HTTPS (produção) |
| Django Dev | 8000 | TCP | Apenas em desenvolvimento |
| Evolution API | 8080 | TCP | WhatsApp (interno ou exposto) |

### Firewall (produção)

```bash
# UFW (Ubuntu)
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp   # SSH
ufw enable
```

### DNS

Configure um registro A no seu provedor DNS:

```
Tipo: A
Nome: locamaq (ou @)
Valor: IP_DO_SERVIDOR
TTL: 3600
```

---

## Primeiro Acesso

### 1. Criar a Empresa (Tenant)

Após o primeiro login com superusuário:

1. Acesse **⚙️ Configurações** na sidebar
2. Preencha os dados da empresa:
   - Nome, CNPJ, Telefone, Endereço
   - Logo (opcional)
3. Preencha as **cláusulas do contrato** (aparecem no PDF):
   - Cláusulas gerais
   - Condições de devolução
   - Termos de multa

### 2. Configurar WhatsApp (Opcional)

1. Vá em **⚙️ Configurações → WhatsApp**
2. Preencha URL da Evolution API, API Key e Instância
3. Clique **🔌 Testar Conexão**

### 3. Cadastrar Equipamentos

1. Vá em **🔧 Equipamentos → + Novo Equipamento**
2. Para cada equipamento, informe:
   - Código patrimônio (ex: AND-001)
   - Nome, Categoria
   - Valores: diária, semanal, mensal

### 4. Cadastrar Clientes

1. Vá em **👥 Clientes → + Novo Cliente**
2. Preencha dados completos (identificação, contato, endereço, referências)

### 5. Configurar Alertas

1. Vá em **🔔 Notificações → ⚙️ Configurar Alertas**
2. Crie regras para:
   - Locação atrasada (threshold: 1 dia)
   - Poucos disponíveis (threshold: 5 unidades)
   - Pagamento pendente (threshold: 7 dias)

### 6. Criar Primeiro Operador

1. Vá em **👥 Usuários → + Novo Usuário**
2. Crie com perfil "Operador"
3. O operador terá acesso a: Clientes, Equipamentos, Locações, Financeiro
4. Apenas Admin acessa: Configurações, Promoções, Usuários, Alertas

---

## Guia do Usuário

### Para o Operador

#### Criar uma Locação

1. Vá em **📋 Locações → + Nova Locação**
2. Selecione o **Cliente**
3. Escolha o **Tipo de Período** (diária/semanal/mensal)
4. Preencha **Data de Início** (pré-preenchida com hoje) e **Devolução Prevista**
5. Selecione **Forma de Pagamento** (PIX, Dinheiro, Cartão, Depois)
6. Adicione os **Equipamentos** (até 10 por locação)
   - Valor unitário em branco = usa tabela de preços automática
7. Preencha **Endereço de Entrega** (aparecerá no mapa)
8. Clique **✅ Criar Locação**

#### Imprimir Comprovante

1. Na tela de detalhe da locação, clique **🖨️ Imprimir**
2. O PDF abre no navegador com:
   - Dados da empresa e cliente
   - Equipamentos e valores
   - Cláusulas e condições
   - Área para assinatura
3. Use Ctrl+P ou o botão de impressão do navegador

#### Enviar via WhatsApp

1. Na tela de detalhe, clique **📱 WhatsApp**
2. Confirme o envio
3. O cliente recebe resumo da locação + PDF

#### Registrar Devolução

1. Na tela de detalhe, clique **↩️ Devolver**
2. Informe a **Data de Devolução**
3. Adicione observações (opcional)
4. Confirme — o sistema automaticamente:
   - Libera os equipamentos
   - Registra entrada financeira
   - Atualiza o dashboard

#### Registrar Transação Manual

1. Vá em **💰 Financeiro → + Nova Transação**
2. Escolha tipo (Entrada ou Saída), valor, descrição e data
3. Transações de locação são criadas automaticamente

### Para o Administrador

#### Tudo do Operador +

- **Gerenciar Usuários** — criar/editar/remover operadores
- **Configurações** — dados da empresa, cláusulas, WhatsApp
- **Promoções** — criar e disparar broadcast para clientes
- **Alertas** — configurar regras de notificação
- **Verificar Alertas** — botão "🔍 Verificar Agora" executa o motor manualmente

---

## Administração

### Perfis de Acesso

| Recurso | Admin | Operador |
|---------|-------|----------|
| Dashboard | ✅ | ✅ |
| Clientes (CRUD) | ✅ | ✅ |
| Equipamentos (CRUD) | ✅ | ✅ |
| Locações (CRUD) | ✅ | ✅ |
| Financeiro | ✅ | ✅ |
| Impressão PDF | ✅ | ✅ |
| WhatsApp (envio) | ✅ | ✅ |
| Notificações (ver) | ✅ | ✅ |
| Promoções | ✅ | ❌ |
| Usuários | ✅ | ❌ |
| Configurações | ✅ | ❌ |
| Config. Alertas | ✅ | ❌ |

### Logs do Sistema

Localizados em `logs/`:

| Arquivo | Conteúdo |
|---------|----------|
| `locamaq.log` | Log geral (INFO+) |
| `errors.log` | Apenas erros com traceback |
| `audit.log` | Todas operações de escrita (POST/PUT/DELETE) |
| `security.log` | Tentativas de acesso negado, bloqueios |
| `integrations.log` | WhatsApp, geocodificação |

Os logs rotacionam automaticamente em 10MB (máximo 5-10 backups por tipo).

### Django Admin

Acesse `/admin/` com superusuário para gerenciamento avançado do banco.

---

## Integrações

### Evolution API (WhatsApp)

| Item | Descrição |
|------|-----------|
| Documentação | https://github.com/EvolutionAPI/evolution-api |
| Configuração | ⚙️ Configurações → WhatsApp |
| Funcionalidades | Envio de texto, PDF, broadcast |
| Fallback | Se offline, sistema funciona normalmente (mensagem de erro amigável) |

#### Instalar Evolution API com Docker:

```bash
docker run -d \
  --name evolution \
  -p 8080:8080 \
  -e AUTHENTICATION_API_KEY=sua-chave \
  atendai/evolution-api
```

### OpenStreetMap / Nominatim (Geocodificação)

- Gratuito, sem API key
- Converte endereço de entrega em coordenadas (lat/lng)
- Usado automaticamente ao criar/editar locação
- Rate limit: 1 request/segundo (suficiente para uso normal)

### Leaflet.js (Mapa)

- Gratuito, sem API key
- Tiles do OpenStreetMap
- Ícones SVG customizados por tipo de equipamento
- Suporte a fullscreen

---

## Troubleshooting

### Servidor não inicia

```bash
# Verificar erro
python manage.py check
python manage.py runserver 2>&1 | head -20

# Problemas comuns:
# - Porta 8000 já em uso → matar processo: kill $(lsof -t -i:8000)
# - .env não existe → cp .env.example .env
# - Migrations pendentes → python manage.py migrate
```

### WhatsApp não envia

1. Verifique se a Evolution API está rodando: `curl http://URL:8080`
2. Verifique as credenciais em ⚙️ Configurações → WhatsApp
3. Clique "🔌 Testar Conexão"
4. Verifique `logs/integrations.log`
5. O número do cliente deve estar no formato `5511999999999` (sem +, sem espaços)

### PDF não gera (WeasyPrint)

```bash
# Instalar dependências do WeasyPrint (Linux)
apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf-2.0-0

# Se não funcionar, o sistema renderiza HTML (imprimível via Ctrl+P)
```

### Mapa não mostra marcadores

- Verifique se as locações ativas têm **endereço de entrega** preenchido
- O geocodificador precisa de internet para converter endereço em coordenadas
- Edite a locação e salve novamente para re-geocodificar
- Endereços muito genéricos podem não ser encontrados (adicione cidade/UF)

### Cache desatualizado

```bash
# Limpar cache manualmente
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Ou deletar a pasta
rm -rf cache/
```

### Erro 500 em produção

1. Verifique `logs/errors.log`
2. Verifique se `DEBUG=False` e `ALLOWED_HOSTS` está correto
3. Verifique se `collectstatic` foi executado
4. Verifique permissões dos volumes Docker

---

## Contato e Suporte

- **Repositório:** `/home/leonardosilva/projetos/geloc/`
- **Documentação:** Este arquivo (`DOCUMENTACAO.md`)
- **Plano de Implementação:** `PLANO_IMPLEMENTACAO.md`

---

*Documentação gerada em 05/08/2026 — LocaMaq v1.0*
