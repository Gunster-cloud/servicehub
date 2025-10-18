# ServiceHub - CRM para Prestadores de Serviços

Uma plataforma moderna e escalável para gestão de clientes, orçamentos, propostas e acompanhamento de vendas para prestadores de serviços em geral.

## 🏗️ Arquitetura

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT (djangorestframework-simplejwt)
- **Validação**: Serializers DRF + Pydantic
- **Cache**: Redis (opcional)
- **Celery**: Processamento assíncrono de tarefas

### Frontend
- **Framework**: React 19 + Vite
- **UI Components**: Shadcn/ui + Radix UI
- **State Management**: TanStack Query + Context API
- **Styling**: Tailwind CSS
- **Formulários**: React Hook Form + Zod

### Infraestrutura
- **Containerização**: Docker + Docker Compose
- **API Gateway**: Nginx
- **Logging**: Structured logging com JSON
- **Monitoring**: Prometheus + Grafana (opcional)

## 📁 Estrutura do Projeto

```
servicehub/
├── backend/
│   ├── config/                 # Configurações Django
│   ├── apps/
│   │   ├── users/             # Gerenciamento de usuários
│   │   ├── clients/           # Gestão de clientes
│   │   ├── quotes/            # Orçamentos e propostas
│   │   ├── services/          # Serviços oferecidos
│   │   └── analytics/         # Análise de dados
│   ├── utils/                 # Funções utilitárias
│   ├── migrations/            # Migrações do banco
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # Componentes reutilizáveis
│   │   ├── pages/            # Páginas da aplicação
│   │   ├── hooks/            # Custom hooks
│   │   ├── services/         # Chamadas de API
│   │   ├── store/            # Context e estado global
│   │   ├── types/            # Tipos TypeScript
│   │   └── main.tsx
│   ├── public/
│   ├── vite.config.ts
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── API.md                # Documentação da API
│   ├── ARCHITECTURE.md       # Detalhes da arquitetura
│   └── SETUP.md             # Guia de configuração
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Pré-requisitos
- Docker e Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Instalação

1. **Clone o repositório**
   ```bash
   git clone <repo-url>
   cd servicehub
   ```

2. **Configure as variáveis de ambiente**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Inicie os serviços com Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Execute as migrações**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Crie um superusuário**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Acesse a aplicação**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin

## 📚 Documentação

- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)

## 🔐 Segurança

- Autenticação JWT com refresh tokens
- CORS configurado
- Rate limiting nas APIs
- Validação de entrada com Serializers
- HTTPS em produção

## 📊 Features

- ✅ Autenticação e autorização
- ✅ Gestão de clientes
- ✅ Criação de orçamentos
- ✅ Geração de propostas
- ✅ Acompanhamento de vendas
- ✅ Análise de dados
- ✅ Relatórios customizáveis
- ✅ Integração com terceiros

## 📝 License

MIT

