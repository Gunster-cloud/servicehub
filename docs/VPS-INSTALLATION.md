# Guia de Instalação VPS - ServiceHub

Este guia fornece instruções completas para instalar e configurar o ServiceHub em um servidor VPS (Virtual Private Server) usando AlmaLinux 9 ou Ubuntu 22.04 LTS.

## 📋 Pré-requisitos

### Requisitos do Servidor
- **Sistema Operacional**: AlmaLinux 9, CentOS 9, Ubuntu 22.04 LTS ou similar
- **RAM**: Mínimo 2GB (recomendado 4GB+)
- **CPU**: Mínimo 2 cores
- **Armazenamento**: Mínimo 20GB SSD
- **Rede**: IP público com acesso à internet
- **Domínio**: Domínio configurado apontando para o IP do servidor (opcional para testes)

### Requisitos de Software
- Docker e Docker Compose
- Git
- Certbot (para SSL)
- Fail2ban (para segurança)

## 🚀 Instalação Automática (Recomendado)

### Para AlmaLinux 9

```bash
# Baixar e executar o script de instalação
curl -fsSL https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-almalinux.sh | bash -s "seu-dominio.com" "admin@seu-dominio.com"
```

### Para Ubuntu 22.04 LTS

```bash
# Baixar e executar o script de instalação
curl -fsSL https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-ubuntu.sh | bash -s "seu-dominio.com" "admin@seu-dominio.com"
```

## 🔧 Instalação Manual Passo a Passo

### 1. Preparação do Servidor

#### Conectar ao servidor
```bash
ssh root@seu-ip-do-servidor
# ou
ssh usuario@seu-ip-do-servidor
sudo su
```

#### Atualizar o sistema
```bash
# AlmaLinux/CentOS
dnf update -y

# Ubuntu/Debian
apt update && apt upgrade -y
```

### 2. Instalação de Dependências

#### Instalar pacotes essenciais
```bash
# AlmaLinux/CentOS
dnf install -y curl wget git unzip htop nano firewalld fail2ban

# Ubuntu/Debian
apt install -y curl wget git unzip htop nano ufw fail2ban
```

#### Instalar Docker
```bash
# AlmaLinux/CentOS
dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install -y docker-compose-plugin
```

#### Configurar Docker
```bash
systemctl enable docker
systemctl start docker
usermod -aG docker $USER
```

#### Instalar Node.js (para builds do frontend)
```bash
# AlmaLinux/CentOS
curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -
dnf install -y nodejs

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
```

### 3. Configuração de Segurança

#### Configurar Firewall
```bash
# AlmaLinux/CentOS (firewalld)
systemctl enable firewalld
systemctl start firewalld
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-service=ssh
firewall-cmd --reload

# Ubuntu/Debian (ufw)
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable
```

#### Configurar Fail2ban
```bash
systemctl enable fail2ban
systemctl start fail2ban
```

### 4. Preparação do Projeto

#### Criar usuário para o projeto
```bash
useradd -r -s /bin/bash -d /opt/servicehub servicehub
usermod -aG docker servicehub
mkdir -p /opt/servicehub
mkdir -p /opt/backups
chown -R servicehub:servicehub /opt/servicehub
chown -R servicehub:servicehub /opt/backups
```

#### Clonar o repositório
```bash
cd /opt/servicehub
git clone https://github.com/seu-usuario/servicehub.git .
chown -R servicehub:servicehub /opt/servicehub
```

### 5. Configuração do Ambiente

#### Criar arquivo de configuração
```bash
cd /opt/servicehub
cp env.prod.example .env
nano .env
```

#### Configurar variáveis essenciais no .env
```bash
# Segurança
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,seu-ip-do-servidor

# Banco de dados
DB_NAME=servicehub_prod
DB_USER=servicehub_user
DB_PASSWORD=sua-senha-segura-do-banco

# CORS
CORS_ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Email (configurar com seu provedor)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app

# Serviços externos (opcional)
MERCADOPAGO_ACCESS_TOKEN=seu-token-mercadopago
TWILIO_ACCOUNT_SID=seu-twilio-sid
TWILIO_AUTH_TOKEN=seu-twilio-token
```

### 6. Configuração de SSL/TLS

#### Instalar Certbot
```bash
# AlmaLinux/CentOS
dnf install -y certbot python3-certbot-nginx

# Ubuntu/Debian
apt install -y certbot python3-certbot-nginx
```

#### Gerar certificado SSL
```bash
# Parar temporariamente o nginx se estiver rodando
docker compose -f docker-compose.prod.yml down

# Gerar certificado
certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com --email admin@seu-dominio.com --agree-tos --non-interactive

# Copiar certificados para o projeto
mkdir -p /opt/servicehub/ssl
cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /opt/servicehub/ssl/cert.pem
cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /opt/servicehub/ssl/key.pem
chown -R servicehub:servicehub /opt/servicehub/ssl
```

### 7. Deploy da Aplicação

#### Construir e iniciar os serviços
```bash
cd /opt/servicehub
docker compose -f docker-compose.prod.yml up -d --build
```

#### Verificar status dos containers
```bash
docker compose -f docker-compose.prod.yml ps
```

#### Executar migrações do banco
```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

#### Criar superusuário
```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### 8. Configuração de Serviços do Sistema

#### Criar serviço systemd
```bash
cat > /etc/systemd/system/servicehub.service << 'EOF'
[Unit]
Description=ServiceHub Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/servicehub
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
User=servicehub
Group=servicehub

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable servicehub
```

### 9. Configuração de Backup

#### Criar script de backup
```bash
cat > /usr/local/bin/servicehub-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
PROJECT_DIR="/opt/servicehub"
DATE=$(date +%Y%m%d_%H%M%S)

cd $PROJECT_DIR

# Backup do banco de dados
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U servicehub_user servicehub_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Backup dos arquivos de mídia
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $PROJECT_DIR media/

# Remover backups antigos (manter últimos 30 dias)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup concluído: $DATE"
EOF

chmod +x /usr/local/bin/servicehub-backup
```

#### Configurar backup automático
```bash
echo "0 2 * * * /usr/local/bin/servicehub-backup" | crontab -u servicehub -
```

### 10. Configuração de Monitoramento

#### Criar script de monitoramento
```bash
cat > /usr/local/bin/servicehub-monitor << 'EOF'
#!/bin/bash
PROJECT_DIR="/opt/servicehub"
LOG_FILE="/var/log/servicehub/monitor.log"

cd $PROJECT_DIR

# Verificar se os containers estão rodando
if ! docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "$(date): Containers do ServiceHub estão parados. Reiniciando..." >> $LOG_FILE
    docker compose -f docker-compose.prod.yml restart
fi

# Verificar uso de disco
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Uso de disco alto: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Verificar uso de memória
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "$(date): Uso de memória alto: ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x /usr/local/bin/servicehub-monitor
mkdir -p /var/log/servicehub
chown -R servicehub:servicehub /var/log/servicehub
```

#### Configurar monitoramento automático
```bash
echo "*/5 * * * * /usr/local/bin/servicehub-monitor" | crontab -u servicehub -
```

### 11. Configuração de Logs

#### Configurar rotação de logs
```bash
cat > /etc/logrotate.d/servicehub << 'EOF'
/var/log/servicehub/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 servicehub servicehub
    postrotate
        docker compose -f /opt/servicehub/docker-compose.prod.yml restart nginx
    endscript
}
EOF
```

## 🔍 Verificação da Instalação

### Verificar serviços
```bash
# Status do serviço systemd
systemctl status servicehub

# Status dos containers
docker compose -f /opt/servicehub/docker-compose.prod.yml ps

# Logs da aplicação
docker compose -f /opt/servicehub/docker-compose.prod.yml logs -f
```

### Testar conectividade
```bash
# Testar API
curl -k https://seu-dominio.com/api/schema/

# Testar frontend
curl -k https://seu-dominio.com/

# Verificar SSL
openssl s_client -connect seu-dominio.com:443 -servername seu-dominio.com
```

## 🛠️ Comandos Úteis

### Gerenciamento da Aplicação
```bash
# Iniciar aplicação
systemctl start servicehub

# Parar aplicação
systemctl stop servicehub

# Reiniciar aplicação
systemctl restart servicehub

# Status da aplicação
systemctl status servicehub
```

### Gerenciamento de Containers
```bash
# Ver logs em tempo real
docker compose -f /opt/servicehub/docker-compose.prod.yml logs -f

# Reiniciar um serviço específico
docker compose -f /opt/servicehub/docker-compose.prod.yml restart backend

# Executar comandos Django
docker compose -f /opt/servicehub/docker-compose.prod.yml exec backend python manage.py shell
```

### Backup e Restore
```bash
# Backup manual
/usr/local/bin/servicehub-backup

# Restore do banco (exemplo)
docker compose -f /opt/servicehub/docker-compose.prod.yml exec -T postgres psql -U servicehub_user servicehub_prod < /opt/backups/db_backup_YYYYMMDD_HHMMSS.sql
```

## 🔧 Manutenção

### Atualizações
```bash
cd /opt/servicehub
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Renovação de SSL
```bash
# Testar renovação
certbot renew --dry-run

# Renovar certificados
certbot renew

# Copiar novos certificados
cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /opt/servicehub/ssl/cert.pem
cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /opt/servicehub/ssl/key.pem
docker compose -f /opt/servicehub/docker-compose.prod.yml restart nginx
```

### Limpeza de Sistema
```bash
# Limpar containers não utilizados
docker system prune -f

# Limpar volumes não utilizados
docker volume prune -f

# Limpar imagens não utilizadas
docker image prune -f
```

## 🚨 Solução de Problemas

### Problemas Comuns

#### Container não inicia
```bash
# Verificar logs
docker compose -f /opt/servicehub/docker-compose.prod.yml logs nome-do-container

# Verificar configuração
docker compose -f /opt/servicehub/docker-compose.prod.yml config
```

#### Problemas de SSL
```bash
# Verificar certificados
certbot certificates

# Testar renovação
certbot renew --dry-run
```

#### Problemas de banco de dados
```bash
# Verificar conexão
docker compose -f /opt/servicehub/docker-compose.prod.yml exec backend python manage.py dbshell

# Executar migrações
docker compose -f /opt/servicehub/docker-compose.prod.yml exec backend python manage.py migrate
```

### Logs Importantes
```bash
# Logs da aplicação
tail -f /var/log/servicehub/monitor.log

# Logs do sistema
journalctl -u servicehub -f

# Logs do Docker
docker logs servicehub_backend_prod
```

## 📞 Suporte

Para problemas específicos ou dúvidas sobre a instalação:

1. Verifique os logs da aplicação
2. Consulte a documentação da API em `docs/API.md`
3. Verifique as configurações de arquitetura em `docs/ARCHITECTURE.md`
4. Abra uma issue no repositório do projeto

## 🔒 Considerações de Segurança

### Configurações Adicionais Recomendadas

#### Configurar SSH
```bash
# Editar configuração SSH
nano /etc/ssh/sshd_config

# Desabilitar login root
PermitRootLogin no

# Usar apenas chaves SSH
PasswordAuthentication no

# Reiniciar SSH
systemctl restart sshd
```

#### Configurar Fail2ban personalizado
```bash
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
EOF

systemctl restart fail2ban
```

#### Configurar atualizações automáticas
```bash
# AlmaLinux/CentOS
dnf install -y dnf-automatic
systemctl enable dnf-automatic.timer

# Ubuntu/Debian
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

**Nota**: Este guia assume que você tem conhecimento básico de administração de servidores Linux. Sempre faça backup dos dados antes de realizar alterações importantes no sistema.
