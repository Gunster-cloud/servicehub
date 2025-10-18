# ServiceHub - Configuração Avançada

Guia completo para configurar recursos avançados do ServiceHub.

## 🔐 SSL/TLS com Let's Encrypt

### Instalação Automática

```bash
chmod +x scripts/setup-ssl.sh
sudo ./scripts/setup-ssl.sh
```

### Instalação Manual

```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem ./certs/
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem ./certs/
```

### Renovação Automática

```bash
# Testar renovação
sudo certbot renew --dry-run

# Configurar cron para renovação automática
sudo crontab -e
# Adicionar: 0 3 * * * certbot renew --quiet
```

## 📧 Configuração de Email (SMTP)

### Gmail

1. Ativar autenticação de 2 fatores
2. Gerar senha de app: https://myaccount.google.com/apppasswords
3. Configurar variáveis:

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### SendGrid

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.sua-chave-api
```

### Mailgun

```bash
# Instalar Anymail
pip install django-anymail

# Configurar
ANYMAIL_MAILGUN_API_KEY=sua-chave-api
ANYMAIL_MAILGUN_SENDER_DOMAIN=seu-dominio.com
```

### Testar Email

```bash
# Via shell Django
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Assunto',
    'Mensagem',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

## ☁️ AWS S3 para Armazenamento

### Configuração

1. Criar bucket S3 no AWS Console
2. Criar IAM user com permissões S3
3. Configurar variáveis:

```bash
USE_S3=True
AWS_ACCESS_KEY_ID=sua-chave
AWS_SECRET_ACCESS_KEY=sua-chave-secreta
AWS_STORAGE_BUCKET_NAME=seu-bucket
AWS_S3_REGION_NAME=us-east-1
```

### Política IAM

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::seu-bucket",
                "arn:aws:s3:::seu-bucket/*"
            ]
        }
    ]
}
```

### Usar S3 no Código

```python
from django.core.files.storage import default_storage

# Upload
file = request.FILES['file']
path = default_storage.save(f'uploads/{file.name}', file)
url = default_storage.url(path)

# Download
file_url = default_storage.url('path/to/file.pdf')
```

## 📊 Sentry para Monitoramento

### Configuração

1. Criar conta em https://sentry.io
2. Criar projeto Django
3. Copiar DSN
4. Configurar variável:

```bash
SENTRY_DSN=https://seu-dsn@sentry.io/seu-projeto-id
```

### Usar Sentry no Código

```python
import sentry_sdk

# Capturar exceção
try:
    # seu código
except Exception as e:
    sentry_sdk.capture_exception(e)

# Enviar mensagem
sentry_sdk.capture_message('Mensagem importante', level='warning')
```

### Dashboard

Acesse https://sentry.io para ver:
- Erros em tempo real
- Performance
- Releases
- Alertas

## 🔄 CI/CD com GitHub Actions

### Configuração

1. Copiar `.github/workflows/ci-cd.yml` para seu repositório
2. Configurar secrets no GitHub:

```
DEPLOY_HOST=seu-servidor.com
DEPLOY_USER=ubuntu
DEPLOY_KEY=sua-chave-ssh-privada
SLACK_WEBHOOK=seu-webhook-slack (opcional)
```

### Workflow

1. **Push para main/develop** → Testes automáticos
2. **Testes passam** → Build Docker
3. **Push para main** → Deploy automático

### Monitorar

Acesse: https://github.com/seu-usuario/servicehub/actions

## 💾 Backups Automáticos

### Configuração

```bash
chmod +x scripts/backup.sh
chmod +x scripts/setup-cron.sh
sudo ./scripts/setup-cron.sh
```

### Backup Manual

```bash
./scripts/backup.sh
```

### Restaurar Backup

```bash
# Banco de dados
gunzip < backups/database_20240101_020000.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T db psql -U servicehub servicehub

# Media
tar -xzf backups/media_20240101_020000.tar.gz -C backend/

# Redis
docker cp backups/redis_20240101_020000.rdb servicehub-redis:/data/dump.rdb
```

### Upload para S3

```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciais
aws configure

# Configurar variável
AWS_S3_BUCKET=seu-bucket

# Fazer backup
./scripts/backup.sh
```

## 🔍 Monitoramento e Logging

### Logs em Tempo Real

```bash
# Todos os serviços
docker-compose -f docker-compose.prod.yml logs -f

# Serviço específico
docker-compose -f docker-compose.prod.yml logs -f backend

# Últimas 100 linhas
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Verificar Saúde

```bash
# Health check
curl http://seu-dominio.com/health

# Status dos containers
docker-compose -f docker-compose.prod.yml ps

# Uso de recursos
docker stats
```

### Alertas

Configure alertas no Sentry para:
- Erros críticos
- Aumento de taxa de erro
- Performance degradada

## 🚀 Performance

### Cache com Redis

```python
from django.core.cache import cache

# Salvar no cache
cache.set('chave', 'valor', timeout=3600)

# Recuperar do cache
valor = cache.get('chave')

# Deletar do cache
cache.delete('chave')
```

### Otimização de Banco de Dados

```python
# Use select_related para ForeignKey
queryset = Client.objects.select_related('user')

# Use prefetch_related para ManyToMany
queryset = Quote.objects.prefetch_related('items')

# Use only() para selecionar campos
queryset = Client.objects.only('name', 'email')
```

### Compressão Gzip

Já configurado no Nginx. Verifica com:

```bash
curl -I -H "Accept-Encoding: gzip" http://seu-dominio.com
```

## 🔒 Segurança

### Checklist

- [ ] SECRET_KEY alterada
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configurado
- [ ] CORS_ALLOWED_ORIGINS restrito
- [ ] SSL/TLS ativado
- [ ] Senhas fortes (DB, Redis, Admin)
- [ ] Backups automáticos
- [ ] Sentry configurado
- [ ] Logs monitorados
- [ ] Firewall configurado

### Headers de Segurança

Já configurados no Nginx:
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Strict-Transport-Security (HSTS)

### Rate Limiting

Configurado no Nginx:
- API: 10 req/s
- Geral: 30 req/s

## 📚 Referências

- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [Let's Encrypt](https://letsencrypt.org/)
- [Sentry Documentation](https://docs.sentry.io/)
- [AWS S3](https://docs.aws.amazon.com/s3/)

