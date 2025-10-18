# ServiceHub Deployment Guide

Guia completo para fazer deploy do ServiceHub em produção.

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git
- Um servidor com pelo menos 2GB de RAM
- Domínio configurado (opcional, mas recomendado)

## 🚀 Deployment em Produção

### 1. Clonar o Repositório

```bash
git clone https://github.com/Gunster-cloud/servicehub.git
cd servicehub
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.prod.example .env.prod

# Editar com suas configurações
nano .env.prod
```

**Variáveis Importantes:**

- `SECRET_KEY` - Chave secreta do Django (gere uma nova)
- `DB_PASSWORD` - Senha do PostgreSQL
- `REDIS_PASSWORD` - Senha do Redis
- `ALLOWED_HOSTS` - Domínios permitidos
- `CORS_ALLOWED_ORIGINS` - Origens CORS permitidas
- `EMAIL_HOST_PASSWORD` - Senha do email (se usar SMTP)

### 3. Gerar Secret Key

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Build das Imagens Docker

```bash
make build
# ou
docker-compose -f docker-compose.prod.yml build
```

### 5. Iniciar os Serviços

```bash
make up
# ou
docker-compose -f docker-compose.prod.yml up -d
```

### 6. Verificar Status

```bash
make ps
# ou
docker-compose -f docker-compose.prod.yml ps
```

### 7. Acessar a Aplicação

- **Frontend**: http://seu-dominio.com
- **Backend API**: http://seu-dominio.com/api/v1
- **Admin Django**: http://seu-dominio.com/admin

## 🔐 Configuração de SSL/TLS

### Com Let's Encrypt

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com

# Copiar certificados para o servidor
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ./certs/
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ./certs/
```

### Configurar no Nginx

Descomente e configure a seção SSL em `nginx.prod.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
}
```

## 📊 Monitoramento

### Logs

```bash
# Todos os logs
make logs

# Logs específicos
make logs-backend
make logs-frontend
```

### Health Check

```bash
make health
# ou
curl http://seu-dominio.com/health
```

### Métricas

```bash
# Ver status dos containers
make ps

# Ver uso de recursos
docker stats
```

## 🔄 Backup e Restore

### Backup do Banco de Dados

```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U servicehub servicehub > backup.sql
```

### Restore do Banco de Dados

```bash
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U servicehub servicehub
```

### Backup de Volumes

```bash
docker run --rm -v servicehub_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

## 🛠️ Manutenção

### Atualizar Código

```bash
git pull origin main
make build
make up
```

### Executar Migrações

```bash
make migrate
```

### Criar Superuser

```bash
make createsuperuser
```

### Limpar Cache

```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py clear_cache
```

### Reiniciar Serviços

```bash
make restart
# ou reiniciar um serviço específico
docker-compose -f docker-compose.prod.yml restart backend
```

## 🚨 Troubleshooting

### Banco de Dados não conecta

```bash
# Verificar logs
make logs-backend

# Verificar se o banco está rodando
make ps

# Reiniciar banco de dados
docker-compose -f docker-compose.prod.yml restart db
```

### Frontend não carrega

```bash
# Verificar logs
make logs-frontend

# Verificar se o frontend está rodando
curl http://localhost:3000

# Limpar cache do navegador (Ctrl+Shift+Delete)
```

### Erro 502 Bad Gateway

```bash
# Verificar se o backend está rodando
make logs-backend

# Reiniciar backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Espaço em disco cheio

```bash
# Limpar imagens e containers não usados
docker system prune -a

# Limpar volumes não usados
docker volume prune
```

## 📈 Scaling

### Aumentar Workers do Gunicorn

Edite `docker-compose.prod.yml`:

```yaml
command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 8
```

### Aumentar Replicas do Celery

```bash
docker-compose -f docker-compose.prod.yml up -d --scale celery=3
```

## 🔒 Segurança

### Checklist de Segurança

- [ ] Alterar `SECRET_KEY` para uma chave forte
- [ ] Alterar senhas padrão (DB, Redis, admin)
- [ ] Configurar SSL/TLS
- [ ] Ativar HTTPS redirect
- [ ] Configurar CORS corretamente
- [ ] Usar variáveis de ambiente para secrets
- [ ] Fazer backup regular do banco de dados
- [ ] Monitorar logs de erro
- [ ] Manter dependências atualizadas
- [ ] Configurar firewall

## 📞 Suporte

Para problemas ou dúvidas:

1. Verificar logs: `make logs`
2. Consultar documentação: `docs/`
3. Abrir issue no GitHub
4. Contactar suporte

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Nginx Documentation](https://nginx.org/en/docs/)

