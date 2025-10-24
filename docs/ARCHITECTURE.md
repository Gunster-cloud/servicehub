# Arquitetura do ServiceHub

## Visão Geral

ServiceHub é uma plataforma CRM moderna construída com uma arquitetura de microserviços containerizada, separando claramente o backend (Django) do frontend (React).

## Componentes Principais

### Backend (Django + DRF)

**Localização**: `/backend`

O backend é responsável por:
- Gerenciar dados e lógica de negócio
- Fornecer APIs REST para o frontend
- Autenticação e autorização (JWT)
- Processamento assíncrono (Celery)
- Cache (Redis)

**Stack**:
- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis
- Celery

### Frontend (React + Vite)

**Localização**: `/frontend`

O frontend é responsável por:
- Interface do usuário
- Consumo de APIs
- Gerenciamento de estado
- Validação de formulários

**Stack**:
- React 19
- Vite
- TanStack Query
- Material-UI (MUI)
- Emotion

### Infraestrutura

**Containerização**: Docker + Docker Compose

Serviços:
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e broker de mensagens
- **Nginx**: Reverse proxy e servidor de arquivos estáticos
- **Celery**: Processamento assíncrono

## Estrutura de Diretórios

```
servicehub/
├── backend/
│   ├── config/              # Configurações Django
│   │   ├── settings.py      # Configurações principais
│   │   ├── urls.py          # URLs principais
│   │   └── wsgi.py          # WSGI para produção
│   ├── servicehub/
│   │   └── apps/            # Aplicações Django
│   │       ├── users/       # Gerenciamento de usuários
│   │       ├── clients/     # Gestão de clientes
│   │       ├── quotes/      # Orçamentos e propostas
│   │       ├── services/    # Serviços
│   │       └── analytics/   # Análise de dados
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # Chamadas de API
│   │   ├── store/          # Estado global
│   │   └── types/          # Tipos TypeScript
│   ├── vite.config.ts
│   └── package.json
├── docs/                    # Documentação
├── docker-compose.yml       # Orquestração de containers
└── nginx.conf              # Configuração do Nginx
```

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│                  (Navegador do Usuário)                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Nginx (Reverse Proxy)                  │
│              (Balanceamento de Carga)                    │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Backend │  │ Backend │  │ Backend │
    │ Worker1 │  │ Worker2 │  │ Worker3 │
    └────┬────┘  └────┬────┘  └────┬────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │PostgreSQL│ │ Redis   │  │ Celery  │
    │ Database │ │ Cache   │  │ Worker  │
    └─────────┘  └─────────┘  └─────────┘
```

## Modelos de Dados

### Usuários (Users)

```
User
├── username: CharField
├── email: EmailField (unique)
├── password: CharField (hashed)
├── first_name: CharField
├── last_name: CharField
├── phone: CharField
├── role: CharField (admin, manager, salesperson, technician, client)
├── company_name: CharField
├── document: CharField (CPF/CNPJ)
├── is_active: BooleanField
├── created_at: DateTimeField
└── updated_at: DateTimeField

UserProfile (OneToOne)
├── bio: TextField
├── avatar: ImageField
├── address: CharField
├── city: CharField
├── state: CharField
├── zip_code: CharField
└── preferences: JSONField
```

### Clientes (Clients)

```
Client
├── name: CharField
├── email: EmailField (unique)
├── phone: CharField
├── type: CharField (individual, company)
├── document: CharField (unique)
├── address: CharField
├── city: CharField
├── state: CharField
├── zip_code: CharField
├── company_name: CharField
├── contact_person: CharField
├── notes: TextField
├── status: CharField (active, inactive, blocked)
├── created_by: ForeignKey(User)
├── assigned_to: ForeignKey(User)
├── created_at: DateTimeField
├── updated_at: DateTimeField
└── last_contact: DateTimeField

ClientContact (Many)
├── name: CharField
├── email: EmailField
├── phone: CharField
├── position: CharField
└── is_primary: BooleanField
```

### Orçamentos (Quotes)

```
Quote
├── quote_number: CharField (unique)
├── client: ForeignKey(Client)
├── title: CharField
├── description: TextField
├── subtotal: DecimalField
├── discount: DecimalField
├── tax: DecimalField
├── total: DecimalField
├── status: CharField (draft, sent, viewed, approved, rejected, expired)
├── valid_until: DateField
├── sent_at: DateTimeField
├── viewed_at: DateTimeField
├── approved_at: DateTimeField
├── created_by: ForeignKey(User)
├── assigned_to: ForeignKey(User)
├── created_at: DateTimeField
└── updated_at: DateTimeField

QuoteItem (Many)
├── description: CharField
├── quantity: DecimalField
├── unit_price: DecimalField
├── total: DecimalField
└── order: PositiveIntegerField

Proposal (OneToOne)
├── quote: OneToOneField(Quote)
├── proposal_number: CharField (unique)
├── status: CharField (draft, sent, viewed, accepted, rejected, expired)
├── terms: TextField
├── payment_terms: CharField
├── warranty: CharField
├── sent_at: DateTimeField
├── accepted_at: DateTimeField
├── created_at: DateTimeField
└── updated_at: DateTimeField
```

### Serviços (Services)

```
Service
├── name: CharField (unique)
├── description: TextField
├── category: CharField
├── base_price: DecimalField
├── unit: CharField
├── status: CharField (active, inactive, archived)
├── notes: TextField
├── created_at: DateTimeField
└── updated_at: DateTimeField

ServiceCategory
├── name: CharField (unique)
├── description: TextField
├── icon: CharField
├── created_at: DateTimeField
└── updated_at: DateTimeField

ServiceOrder
├── order_number: CharField (unique)
├── service: ForeignKey(Service)
├── assigned_to: ForeignKey(User)
├── status: CharField (pending, in_progress, completed, cancelled)
├── scheduled_date: DateTimeField
├── completed_date: DateTimeField
├── notes: TextField
├── created_at: DateTimeField
└── updated_at: DateTimeField
```

### Análise (Analytics)

```
SalesMetrics
├── user: ForeignKey(User)
├── total_quotes: IntegerField
├── approved_quotes: IntegerField
├── rejected_quotes: IntegerField
├── total_revenue: DecimalField
├── average_quote_value: DecimalField
├── conversion_rate: DecimalField
├── period_start: DateField
├── period_end: DateField
├── created_at: DateTimeField
└── updated_at: DateTimeField

DailyActivity
├── user: ForeignKey(User)
├── activity_type: CharField
├── description: TextField
├── quote: ForeignKey(Quote, nullable)
├── metadata: JSONField
└── created_at: DateTimeField

Report
├── name: CharField
├── report_type: CharField (sales, revenue, clients, performance)
├── description: TextField
├── data: JSONField
├── period_start: DateField
├── period_end: DateField
├── created_by: ForeignKey(User)
└── created_at: DateTimeField
```

## Fluxo de Autenticação

```
1. Usuário faz login
   POST /api/auth/token/
   {username, password}
   
2. Backend valida credenciais
   
3. Backend retorna tokens
   {access_token, refresh_token}
   
4. Frontend armazena tokens (localStorage/sessionStorage)
   
5. Frontend inclui access_token em requisições
   Authorization: Bearer {access_token}
   
6. Backend valida token em cada requisição
   
7. Se token expirou, frontend usa refresh_token
   POST /api/auth/token/refresh/
   {refresh_token}
   
8. Backend retorna novo access_token
```

## Segurança

### Autenticação
- JWT com access token (5 minutos) e refresh token (1 dia)
- Tokens assinados com SECRET_KEY
- Suporte a token rotation

### Autorização
- Permissões baseadas em roles (admin, manager, salesperson, technician, client)
- Verificação de permissões em cada endpoint
- Isolamento de dados por usuário/empresa

### Proteção
- CORS configurado para domínios específicos
- Rate limiting (100 req/hora anônimo, 1000 req/hora autenticado)
- CSRF protection
- SQL injection prevention (ORM)
- XSS prevention (serializers)
- HTTPS em produção
- Senhas hasheadas com PBKDF2

## Escalabilidade

### Horizontal
- Múltiplos workers Django atrás do Nginx
- Redis para cache compartilhado
- Celery workers para processamento assíncrono
- PostgreSQL com replicação

### Vertical
- Otimização de queries (select_related, prefetch_related)
- Indexação de banco de dados
- Cache de resultados frequentes
- Paginação de resultados

## Deployment

### Desenvolvimento
```bash
docker-compose up -d
```

### Produção
```bash
docker-compose -f docker-compose.prod.yml up -d
```

Considerações:
- Use variáveis de ambiente para secrets
- Configure HTTPS com certificado SSL
- Use CDN para arquivos estáticos
- Configure backups automáticos do banco
- Monitore logs e métricas
- Configure alertas para erros

## Monitoramento

### Logs
- Estruturados em JSON
- Armazenados em `/logs/django.log`
- Rotação automática (10MB, 10 backups)

### Métricas
- Prometheus para coleta
- Grafana para visualização
- Alertas para anomalias

### Health Checks
- Endpoint `/api/schema/` para verificar saúde
- Verificações de banco de dados
- Verificações de cache

## Roadmap

### MVP (Atual)
- ✅ Autenticação e autorização
- ✅ Gestão de clientes
- ✅ Criação de orçamentos
- ✅ Propostas
- ✅ Serviços
- ✅ Análise básica

### Fase 2
- Notificações por email
- Integração com pagamento
- Relatórios avançados
- Agendamento de serviços
- Integração com WhatsApp

### Fase 3
- Mobile app (React Native)
- Sincronização offline
- Inteligência artificial
- Previsão de vendas
- Otimização de rotas

