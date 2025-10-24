#!/bin/bash

# ServiceHub Deploy Script for Ubuntu 22.04 LTS
# This script sets up and deploys ServiceHub on a fresh Ubuntu 22.04 LTS VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}
PROJECT_DIR="/opt/servicehub"
BACKUP_DIR="/opt/backups"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ServiceHub Deploy Script - Ubuntu 22.04${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script deve ser executado como root (sudo)"
   exit 1
fi

# Update system
print_status "Atualizando sistema..."
apt update && apt upgrade -y

# Install required packages
print_status "Instalando dependências..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    htop \
    nano \
    ufw \
    fail2ban \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
print_status "Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    apt install -y docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker instalado com sucesso!"
else
    print_warning "Docker já está instalado"
fi

# Install Node.js (for frontend builds)
print_status "Instalando Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
    print_status "Node.js instalado com sucesso!"
else
    print_warning "Node.js já está instalado"
fi

# Configure firewall
print_status "Configurando firewall..."
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# Configure fail2ban
print_status "Configurando fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Create project directory
print_status "Criando diretórios do projeto..."
mkdir -p $PROJECT_DIR
mkdir -p $BACKUP_DIR
mkdir -p /var/log/servicehub

# Create servicehub user
print_status "Criando usuário servicehub..."
if ! id "servicehub" &>/dev/null; then
    useradd -r -s /bin/bash -d $PROJECT_DIR servicehub
    usermod -aG docker servicehub
    chown -R servicehub:servicehub $PROJECT_DIR
    chown -R servicehub:servicehub $BACKUP_DIR
fi

# Clone repository (if not already present)
if [ ! -d "$PROJECT_DIR/.git" ]; then
    print_status "Clonando repositório..."
    cd $PROJECT_DIR
    # You'll need to replace this with your actual repository URL
    # git clone https://github.com/yourusername/servicehub.git .
    print_warning "Por favor, clone o repositório manualmente em $PROJECT_DIR"
fi

# Set up environment file
print_status "Configurando arquivo de ambiente..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp $PROJECT_DIR/env.prod.example $PROJECT_DIR/.env
    print_warning "Arquivo .env criado. Por favor, configure as variáveis necessárias:"
    print_warning "- SECRET_KEY"
    print_warning "- ALLOWED_HOSTS"
    print_warning "- DB_PASSWORD"
    print_warning "- Email settings"
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
