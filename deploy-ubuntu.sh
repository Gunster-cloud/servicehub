#!/usr/bin/env bash
set -euo pipefail

# Parâmetros (posicionais)
DOMAIN="${1:-}"
ADMIN_EMAIL="${2:-}"
REPO_URL="${3:-https://github.com/seu-usuario/servicehub.git}"
INSTALL_DIR="/opt/servicehub"
NEWUSER="deploy"
COMPOSE_PROJECT="servicehub"

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute este script como root (sudo)."
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive

echo "==> 1) Atualizando sistema e instalando dependências básicas..."
apt update && apt upgrade -y
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release \
  software-properties-common git ufw wget unzip

echo "==> 2) Criando usuário não-root '$NEWUSER' (se não existir)..."
if id -u "$NEWUSER" >/dev/null 2>&1; then
  echo "Usuário $NEWUSER já existe. Pulando criação."
else
  adduser --disabled-password --gecos "" "$NEWUSER"
  usermod -aG sudo "$NEWUSER"
  echo "Usuário $NEWUSER criado e adicionado ao grupo sudo."
fi

echo "==> 3) Instalando Docker (oficial) e plugin docker compose..."
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  apt update
  apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  systemctl enable --now docker
  usermod -aG docker "$NEWUSER" || true
else
  echo "Docker já instalado. Pulando."
fi

echo "==> 4) Instalando Nginx, Certbot e fail2ban..."
apt install -y nginx certbot python3-certbot-nginx fail2ban
systemctl enable --now nginx
systemctl enable --now fail2ban

echo "==> 5) Configurando UFW (SSH, HTTP, HTTPS)..."
ufw allow OpenSSH
ufw allow 'Nginx Full' || true
ufw --force enable

echo "==> 6) Clonando ou atualizando o repositório em $INSTALL_DIR..."
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "Repositório já existe em $INSTALL_DIR — atualizando..."
  git -C "$INSTALL_DIR" fetch --all --prune
  git -C "$INSTALL_DIR" reset --hard origin/main || git -C "$INSTALL_DIR" pull || true
else
  git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
  chown -R "$NEWUSER":"$NEWUSER" "$INSTALL_DIR"
fi

# Detecta docker compose file path (raiz)
COMPOSE_FILES=("$INSTALL_DIR/docker-compose.yml" "$INSTALL_DIR/docker-compose.yaml")
COMPOSE_FILE=""
for f in "${COMPOSE_FILES[@]}"; do
  if [ -f "$f" ]; then
    COMPOSE_FILE="$f"
    break
  fi
done

if [ -z "$COMPOSE_FILE" ]; then
  echo "Aviso: docker-compose.yml não encontrado em $INSTALL_DIR. Verifique o repositório."
else
  echo "==> 7) Subindo containers com Docker Compose..."
  (cd "$INSTALL_DIR" && docker compose up -d --remove-orphans)

  echo "==> 8) Executando migrações Django (se o serviço 'backend' existir)..."
  # tenta executar migrate com retries (aguarda DB subir)
  if (cd "$INSTALL_DIR" && docker compose ps | grep -q 'backend'); then
    ATTEMPTS=0
    until [ "$ATTEMPTS" -ge 12 ]; do
      if (cd "$INSTALL_DIR" && docker compose exec -T backend python manage.py migrate) ; then
        echo "Migrações aplicadas com sucesso."
        break
      fi
      ATTEMPTS=$((ATTEMPTS+1))
      echo "Tentativa $ATTEMPTS/12: backend ainda não pronto. Aguardando 5s..."
      sleep 5
    done
    if [ "$ATTEMPTS" -ge 12 ]; then
      echo "Migrações falharam após várias tentativas. Verifique 'docker compose logs backend'."
    fi
  else
    echo "Serviço 'backend' não detectado no docker-compose. Pulei migrações."
  fi
fi

if [ -n "$DOMAIN" ]; then
  echo "==> 9) Tentando emitir certificado Let's Encrypt para $DOMAIN..."
  if command -v certbot >/dev/null 2>&1; then
    if [ -n "$ADMIN_EMAIL" ]; then
      certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$ADMIN_EMAIL" || \
        echo "Certbot falhou — verifique DNS, Nginx config e logs."
    else
      certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email || \
        echo "Certbot falhou — verifique DNS, Nginx config e logs."
    fi
    systemctl reload nginx || true
  else
    echo "Certbot não encontrado. Pulei tentativa de emitir certificado."
  fi
else
  echo "Nenhum domínio informado — pulei tentativa de emitir TLS."
fi

echo "==> 10) Permissões e resumo final..."
chown -R "$NEWUSER":"$NEWUSER" "$INSTALL_DIR" || true

echo
echo "Instalação concluída."
echo "Diretório de instalação: $INSTALL_DIR"
echo "Usuário criado/uso: $NEWUSER"
if [ -n "$DOMAIN" ]; then
  echo "Se o certificado foi emitido, o site está protegido por TLS."
else
  echo "Execute o script novamente com um domínio para emitir TLS via Let's Encrypt."
fi
echo "Verifique os logs dos serviços com: (cd $INSTALL_DIR && docker compose logs -f)"
    print_warning "- External services API keys"
fi

# Install Certbot
print_status "Instalando Certbot..."
apt install -y certbot python3-certbot-nginx

# Set up SSL certificates
print_status "Configurando SSL..."
if [ "$DOMAIN" != "your-domain.com" ]; then
    mkdir -p /etc/nginx/ssl
    # Generate self-signed certificate for initial setup
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/key.pem \
        -out /etc/nginx/ssl/cert.pem \
        -subj "/C=BR/ST=SP/L=SaoPaulo/O=ServiceHub/CN=$DOMAIN"
    
    print_status "Certificado SSL temporário criado"
    print_warning "Para produção, configure Let's Encrypt:"
    print_warning "certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive"
fi

# Set up log rotation
print_status "Configurando rotação de logs..."
cat > /etc/logrotate.d/servicehub << EOF
/var/log/servicehub/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 servicehub servicehub
    postrotate
        docker compose -f $PROJECT_DIR/docker-compose.prod.yml restart nginx
    endscript
}
EOF

# Set up backup script
print_status "Criando script de backup..."
cat > /usr/local/bin/servicehub-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
PROJECT_DIR="/opt/servicehub"
DATE=$(date +%Y%m%d_%H%M%S)

cd $PROJECT_DIR

# Create database backup
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U servicehub_user servicehub_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Create media backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz -C $PROJECT_DIR media/

# Remove old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/servicehub-backup

# Set up cron job for backups
print_status "Configurando backup automático..."
echo "0 2 * * * /usr/local/bin/servicehub-backup" | crontab -u servicehub -

# Set up systemd service
print_status "Criando serviço systemd..."
cat > /etc/systemd/system/servicehub.service << EOF
[Unit]
Description=ServiceHub Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
User=servicehub
Group=servicehub

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable servicehub

# Create monitoring script
print_status "Criando script de monitoramento..."
cat > /usr/local/bin/servicehub-monitor << 'EOF'
#!/bin/bash
PROJECT_DIR="/opt/servicehub"
LOG_FILE="/var/log/servicehub/monitor.log"

cd $PROJECT_DIR

# Check if containers are running
if ! docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "$(date): ServiceHub containers are down. Restarting..." >> $LOG_FILE
    docker compose -f docker-compose.prod.yml restart
fi

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage is high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "$(date): Memory usage is high: ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x /usr/local/bin/servicehub-monitor

# Set up monitoring cron job
echo "*/5 * * * * /usr/local/bin/servicehub-monitor" | crontab -u servicehub -

# Configure automatic security updates
print_status "Configurando atualizações automáticas de segurança..."
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

print_status "Deploy concluído com sucesso!"
echo
echo -e "${GREEN}Próximos passos:${NC}"
echo "1. Configure o arquivo .env em $PROJECT_DIR"
echo "2. Clone o repositório em $PROJECT_DIR"
echo "3. Execute: cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml up -d"
echo "4. Configure SSL com Let's Encrypt se necessário"
echo
echo -e "${BLUE}Comandos úteis:${NC}"
echo "- Iniciar: systemctl start servicehub"
echo "- Parar: systemctl stop servicehub"
echo "- Status: systemctl status servicehub"
echo "- Logs: docker compose -f $PROJECT_DIR/docker-compose.prod.yml logs -f"
echo "- Backup: /usr/local/bin/servicehub-backup"
echo
echo -e "${YELLOW}IMPORTANTE:${NC}"
echo "- Configure o arquivo .env com suas credenciais"
echo "- Configure o DNS do seu domínio para apontar para este servidor"
echo "- Configure SSL com Let's Encrypt para produção"
