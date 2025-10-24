# ServiceHub - CRM para Prestadores de Serviços

Uma plataforma moderna e escalável para gestão de clientes, orçamentos, propostas e acompanhamento de vendas para prestadores de serviços em geral.

## 🏗️ Arquitetura

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT (djangorestframework-simplejwt)
- **Validação**: Serializers DRF + Pydantic
- **Cache**: Redis (opcional)
- **Celery**: Processamento assíncrono de tarefas

### Frontend
- **Framework**: React 19 + Vite
- **UI Components**: Material-UI (MUI) + Emotion
- **State Management**: TanStack Query + Context API
- **Styling**: Material-UI + CSS
- **Formulários**: React Hook Form + Zod

### Infraestrutura
- **Containerização**: Docker + Docker Compose
- **API Gateway**: Nginx
- **Logging**: Structured logging com JSON
- **Monitoring**: Prometheus + Grafana (opcional)

## 🚀 Início Rápido

### Pré-requisitos
- Docker Desktop instalado e rodando
- Node.js 18+ (para desenvolvimento local)
- Python 3.11+ (para desenvolvimento local)

### Setup Automático

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Setup Manual

1. **Clone o repositório:**
```bash
git clone <repo-url>
cd servicehub
```

2. **Configure as variáveis de ambiente:**
```bash
cp env.example .env
```

3. **Inicie os serviços:**
```bash
docker compose up -d
```

4. **Instale dependências do frontend (desenvolvimento):**
```bash
cd frontend
npm install
```

### Acessos
- **API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Nginx**: http://localhost:8080
- **Admin Django**: http://localhost:8000/admin/

## 📁 Estrutura do Projeto

```
servicehub/
├── backend/
│   ├── config/                 # Configurações Django
│   ├── servicehub/apps/
│   │   ├── users/             # Gerenciamento de usuários
│   │   ├── clients/           # Gestão de clientes
│   │   ├── quotes/            # Orçamentos e propostas
│   │   ├── services/          # Serviços oferecidos
│   │   └── analytics/         # Análise de dados
│   ├── utils/                 # Funções utilitárias
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # Componentes reutilizáveis
│   │   ├── pages/            # Páginas da aplicação
│   │   ├── hooks/            # Custom hooks
│   │   ├── services/         # Chamadas de API
│   │   ├── contexts/         # Context e estado global
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
   docker compose up -d
   ```

   > **Dica:** o Redis agora é publicado em uma porta aleatória por padrão para evitar conflitos
7
   > com instalações locais e o Nginx usa as portas 8080/8443 por padrão para não disputar as
   > portas 80/443 do host. Execute `docker compose port redis 6379` para descobrir a porta ou
7
   > defina variáveis como `REDIS_HOST_PORT`, `POSTGRES_HOST_PORT`, `BACKEND_HOST_PORT`,
   > `FRONTEND_HOST_PORT`, `NGINX_HTTP_PORT` ou `NGINX_HTTPS_PORT` em um arquivo `.env` na raiz
   > do projeto **antes** de executar o Docker Compose. Os serviços serão expostos usando esses
   > valores.

7
4. **Execute as migrações**
   ```bash
   docker compose exec backend python manage.py migrate
   ```

5. **Crie um superusuário**
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

6. **Acesse a aplicação**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - Nginx (proxy unificado): http://localhost:8080

## 🌐 Deploy em VPS

Para instalar o ServiceHub em um servidor VPS (AlmaLinux 9, Ubuntu 22.04 LTS):

### Instalação Automática
```bash
# AlmaLinux 9
curl -fsSL https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-almalinux.sh | bash -s "seu-dominio.com" "admin@seu-dominio.com"

# Ubuntu 22.04 LTS
curl -fsSL https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-ubuntu.sh | bash -s "seu-dominio.com" "admin@seu-dominio.com"
```

### Configuração SSL
```bash
# Após a instalação, configure SSL com Let's Encrypt
wget https://raw.githubusercontent.com/seu-usuario/servicehub/main/scripts/setup-ssl-production.sh
chmod +x setup-ssl-production.sh
./setup-ssl-production.sh
```

### Requisitos do Servidor
- **Sistema**: AlmaLinux 9, Ubuntu 22.04 LTS ou similar
- **RAM**: Mínimo 2GB (recomendado 4GB+)
- **CPU**: Mínimo 2 cores
- **Armazenamento**: Mínimo 20GB SSD
- **Domínio**: Configurado apontando para o IP do servidor

Para instruções detalhadas, consulte:
- [Guia Completo de VPS](docs/VPS-INSTALLATION.md)
- [Guia Rápido de VPS](docs/VPS-QUICK-START.md)

## 📚 Documentação

- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)
- [VPS Installation Guide](docs/VPS-INSTALLATION.md) - Guia completo para instalação em VPS
- [VPS Quick Start](docs/VPS-QUICK-START.md) - Guia rápido para VPS

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

