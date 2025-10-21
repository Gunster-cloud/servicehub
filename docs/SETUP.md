# Guia de Configuração - ServiceHub

## Pré-requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)
- PostgreSQL 15+ (para desenvolvimento local)
- Node.js 18+ (para frontend)

## Instalação com Docker Compose

### 1. Clone o repositório

```bash
git clone <repo-url>
cd servicehub
```

### 2. Configure as variáveis de ambiente

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend (quando disponível)
cp frontend/.env.example frontend/.env
```

### 3. Inicie os serviços

```bash
docker compose up -d
```

Este comando irá:
- Criar e iniciar o PostgreSQL
- Criar e iniciar o Redis
- Criar e iniciar o Django Backend
- Criar e iniciar o Celery Worker
- Criar e iniciar o Nginx

> **Dica:** se alguma porta (5432 para o PostgreSQL, 6379 para o Redis, 8000 para o backend,
> 3000 para o frontend ou 80/443 para o Nginx) já estiver em uso na sua máquina, crie um
> arquivo `.env` na raiz do projeto e defina as variáveis abaixo com as portas desejadas:
>
> ```env
> POSTGRES_HOST_PORT=55432
> REDIS_HOST_PORT=56379
> BACKEND_HOST_PORT=58000
> FRONTEND_HOST_PORT=53000
> NGINX_HTTP_PORT=50080
> NGINX_HTTPS_PORT=50443
> ```
>
> O Docker Compose utilizará esses valores automaticamente graças ao novo mapeamento de
> portas parametrizável.

### 4. Verifique o status dos serviços

```bash
docker compose ps
```

### 5. Acesse a aplicação

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/api/docs/
- **Admin Django**: http://localhost:8000/admin/
- **Frontend**: http://localhost:3000 (quando disponível)

## Desenvolvimento Local (sem Docker)

### 1. Configure o ambiente Python

```bash
cd backend

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configure o banco de dados

```bash
# Crie o banco de dados PostgreSQL
createdb servicehub

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser
```

### 3. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

O servidor estará disponível em http://localhost:8000

## Migrações do Banco de Dados

### Criar uma nova migração

```bash
python manage.py makemigrations
```

### Aplicar migrações

```bash
python manage.py migrate
```

### Ver status das migrações

```bash
python manage.py showmigrations
```

## Gerenciamento de Usuários

### Criar superusuário (Admin)

```bash
python manage.py createsuperuser
```

### Criar usuário via shell

```bash
python manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_user(
    username='usuario',
    email='usuario@example.com',
    password='senha123',
    first_name='João',
    last_name='Silva',
    role='salesperson'
)
```

## Testes

### Executar todos os testes

```bash
pytest
```

### Executar testes de um app específico

```bash
pytest servicehub/apps/users/tests/
```

### Executar com cobertura

```bash
pytest --cov=servicehub
```

## Linting e Formatação

### Formatar código com Black

```bash
black .
```

### Verificar estilo com Flake8

```bash
flake8 servicehub
```

### Ordenar imports com isort

```bash
isort servicehub
```

## Variáveis de Ambiente

### Backend (.env)

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=servicehub
DB_USER=servicehub
DB_PASSWORD=servicehub
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET=your-jwt-secret-here

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## Logs

Os logs estão localizados em:

```bash
# Docker
docker compose logs -f backend

# Local
tail -f logs/django.log
```

## Troubleshooting

### Erro de conexão com banco de dados

```bash
# Verifique se o PostgreSQL está rodando
psql -U servicehub -d servicehub -h localhost

# Recrie o banco
dropdb servicehub
createdb servicehub
python manage.py migrate
```

### Erro de migração

```bash
# Verifique o status
python manage.py showmigrations

# Desfaça uma migração específica
python manage.py migrate app_name 0001

# Recriar as migrações
rm servicehub/apps/*/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

### Porta já em uso

```bash
# Encontre o processo usando a porta
lsof -i :8000

# Mate o processo
kill -9 <PID>

# Ou use uma porta diferente
python manage.py runserver 8001
```

## Produção

### Configurações importantes

1. **Defina DEBUG=False**
2. **Mude o SECRET_KEY**
3. **Configure ALLOWED_HOSTS**
4. **Use HTTPS**
5. **Configure CORS apropriadamente**
6. **Use um banco de dados externo**
7. **Configure variáveis de ambiente seguras**

### Deploy com Docker

```bash
# Build da imagem
docker build -t servicehub:latest ./backend

# Push para registry
docker push servicehub:latest

# Deploy em produção
docker compose -f docker-compose.prod.yml up -d
```

## Recursos Adicionais

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

