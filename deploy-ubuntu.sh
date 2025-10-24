#!/bin/bash
set -euo pipefail

# Simple VPS deploy script for Ubuntu 20.04/22.04
# Usage: ./deploy-ubuntu.sh [--user USER] [--ssh-key "PUBKEY"] [--domain DOMAIN]

print_usage() {
  cat <<EOF
Usage: $0 [--user USER] [--ssh-key "PUBKEY"] [--domain DOMAIN] [--help]
If an option is omitted the script will prompt interactively.
EOF
}

# parse optional args
USER_ARG=""
SSH_KEY_ARG=""
DOMAIN_ARG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user) USER_ARG="$2"; shift 2;;
    --ssh-key) SSH_KEY_ARG="$2"; shift 2;;
    --domain) DOMAIN_ARG="$2"; shift 2;;
    -h|--help) print_usage; exit 0;;
    *) echo "Unknown arg: $1"; print_usage; exit 2;;
  esac
done

if [ "$(id -u)" -ne 0 ]; then
  echo "Execute este script como root ou via sudo."
  exit 1
fi

# Interactive prompts (use provided args as defaults)
read -rp "Nome do novo usuário (ex: deploy) [${USER_ARG:-deploy}]: " NEWUSER
NEWUSER=${NEWUSER:-${USER_ARG:-deploy}}

if [ -n "$SSH_KEY_ARG" ]; then
  SSH_KEY="$SSH_KEY_ARG"
else
  read -rp "Chave pública SSH para o usuário (cole ou deixe em branco para pular): " SSH_KEY
fi

if [ -n "$DOMAIN_ARG" ]; then
  DOMAIN="$DOMAIN_ARG"
else
  read -rp "Domínio para TLS (ex: example.com) — deixe em branco para pular: " DOMAIN
fi

export DEBIAN_FRONTEND=noninteractive

echo "1) Atualizando sistema e instalando dependências..."
apt update && apt upgrade -y
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release \
    software-properties-common ufw git wget unzip

echo "2) Criando usuário '$NEWUSER'..."
if id -u "$NEWUSER" >/dev/null 2>&1; then
  echo "Usuário já existe, pulando criação."
else
  adduser --gecos "" "$NEWUSER"
  usermod -aG sudo "$NEWUSER"
fi

if [ -n "${SSH_KEY:-}" ]; then
  su - "$NEWUSER" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
  echo "$SSH_KEY" > /home/"$NEWUSER"/.ssh/authorized_keys
  chown "$NEWUSER":"$NEWUSER" /home/"$NEWUSER"/.ssh/authorized_keys
  chmod 600 /home/"$NEWUSER"/.ssh/authorized_keys
  echo "Chave SSH instalada para $NEWUSER."
fi

echo "3) Configurando UFW (SSH, HTTP, HTTPS)..."
ufw allow OpenSSH || true
# try to allow Nginx profile; if profile missing, open common ports
if ufw app list 2>/dev/null | grep -q "Nginx Full"; then
  ufw allow 'Nginx Full' || true
else
  ufw allow 80/tcp || true
  ufw allow 443/tcp || true
fi
ufw --force enable

echo "4) Instalando Docker..."
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  apt update
  apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  systemctl enable --now docker
  usermod -aG docker "$NEWUSER" || true
else
  echo "Docker já instalado, pulando."
fi

echo "5) Instalando Nginx, Certbot e fail2ban..."
apt install -y nginx certbot python3-certbot-nginx fail2ban
systemctl enable --now nginx
systemctl enable --now fail2ban

if [ -n "${DOMAIN:-}" ]; then
  echo "Tentando obter certificado TLS para $DOMAIN..."
  # Certbot requires domain DNS pointing to this server and Nginx running.
  if systemctl is-active --quiet nginx; then
    if certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m admin@"$DOMAIN"; then
      echo "Certificado emitido para $DOMAIN."
    else
      echo "Certbot falhou — verifique DNS e logs. Você pode rodar certbot manualmente."
    fi
  else
    echo "Nginx não está ativo. Certbot precisa do Nginx rodando para o modo --nginx."
  fi
fi

echo "6) Limpeza e resumo..."
apt autoremove -y

echo
echo "Instalação concluída."
echo "Usuário criado: $NEWUSER"
echo "Lembre-se: faça login com 'ssh $NEWUSER@<IP>' e, se necessário, reinicie para aplicar grupos."
echo "Docker disponível (usuário $NEWUSER adicionado ao grupo 'docker')."
if [ -n "${DOMAIN:-}" ]; then
  echo "Se o certificado foi emitido, Nginx já foi configurado para usar TLS."
else
  echo "Execute o script novamente com --domain your-domain.com para emitir TLS via Let's Encrypt."
fi

exit 0
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
