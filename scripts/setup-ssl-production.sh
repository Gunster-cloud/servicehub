#!/bin/bash

# ServiceHub SSL/TLS Setup Script
# Este script configura SSL/TLS com Let's Encrypt para produção

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}ServiceHub SSL/TLS Configuration${NC}"
echo -e "${BLUE}==========================================${NC}"
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

# Verificar se é root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script deve ser executado como root (sudo)"
   exit 1
fi

# Solicitar informações do usuário
read -p "Digite seu domínio (ex: servicehub.com.br): " DOMAIN
read -p "Digite seu email para notificações: " EMAIL

# Validar entrada
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    print_error "Domínio e email são obrigatórios!"
    exit 1
fi

PROJECT_DIR="/opt/servicehub"

# Verificar se o projeto existe
if [ ! -d "$PROJECT_DIR" ]; then
    print_error "Diretório do projeto não encontrado: $PROJECT_DIR"
    print_error "Execute primeiro o script de deploy!"
    exit 1
fi

print_status "Configurando SSL para domínio: $DOMAIN"
print_status "Email de notificação: $EMAIL"

# Instalar Certbot se não estiver instalado
print_status "Verificando Certbot..."
if ! command -v certbot &> /dev/null; then
    print_status "Instalando Certbot..."
    
    # Detectar distribuição
    if [ -f /etc/redhat-release ]; then
        # AlmaLinux/CentOS/RHEL
        dnf install -y certbot python3-certbot-nginx
    elif [ -f /etc/debian_version ]; then
        # Ubuntu/Debian
        apt update
        apt install -y certbot python3-certbot-nginx
    else
        print_error "Distribuição não suportada!"
        exit 1
    fi
else
    print_status "Certbot já está instalado"
fi

# Parar temporariamente o nginx se estiver rodando
print_status "Parando serviços temporariamente..."
cd $PROJECT_DIR
if docker compose -f docker-compose.prod.yml ps | grep -q "nginx.*Up"; then
    docker compose -f docker-compose.prod.yml stop nginx
fi

# Verificar se o domínio aponta para este servidor
print_status "Verificando DNS..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    print_warning "ATENÇÃO: O domínio $DOMAIN não aponta para este servidor!"
    print_warning "IP do servidor: $SERVER_IP"
    print_warning "IP do domínio: $DOMAIN_IP"
    read -p "Deseja continuar mesmo assim? (y/N): " CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        print_error "Configuração cancelada"
        exit 1
    fi
fi

# Gerar certificado SSL
print_status "Gerando certificado SSL para $DOMAIN..."
certbot certonly --standalone \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --expand

if [ $? -eq 0 ]; then
    print_status "Certificado SSL gerado com sucesso!"
else
    print_error "Falha ao gerar certificado SSL"
    exit 1
fi

# Criar diretório SSL no projeto
print_status "Configurando certificados no projeto..."
mkdir -p $PROJECT_DIR/ssl

# Copiar certificados
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $PROJECT_DIR/ssl/cert.pem
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $PROJECT_DIR/ssl/key.pem

# Definir permissões corretas
chown -R servicehub:servicehub $PROJECT_DIR/ssl
chmod 600 $PROJECT_DIR/ssl/key.pem
chmod 644 $PROJECT_DIR/ssl/cert.pem

# Atualizar configuração do nginx
print_status "Atualizando configuração do Nginx..."
if [ -f "$PROJECT_DIR/nginx.prod.conf" ]; then
    # Fazer backup da configuração atual
    cp $PROJECT_DIR/nginx.prod.conf $PROJECT_DIR/nginx.prod.conf.bak
    
    # Atualizar configuração
    sed -i "s/server_name _;/server_name $DOMAIN www.$DOMAIN;/g" $PROJECT_DIR/nginx.prod.conf
    
    print_status "Configuração do Nginx atualizada"
else
    print_warning "Arquivo nginx.prod.conf não encontrado"
fi

# Configurar renovação automática
print_status "Configurando renovação automática..."
cat > /usr/local/bin/servicehub-ssl-renew << 'EOF'
#!/bin/bash
PROJECT_DIR="/opt/servicehub"
LOG_FILE="/var/log/servicehub/ssl-renew.log"

echo "$(date): Verificando renovação de certificados SSL..." >> $LOG_FILE

# Renovar certificados se necessário
certbot renew --quiet

if [ $? -eq 0 ]; then
    echo "$(date): Certificados verificados/renovados com sucesso" >> $LOG_FILE
    
    # Copiar novos certificados se renovados
    DOMAIN=$(certbot certificates | grep "Certificate Name" | head -1 | awk '{print $3}')
    if [ ! -z "$DOMAIN" ]; then
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem $PROJECT_DIR/ssl/cert.pem
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem $PROJECT_DIR/ssl/key.pem
        chown -R servicehub:servicehub $PROJECT_DIR/ssl
        chmod 600 $PROJECT_DIR/ssl/key.pem
        chmod 644 $PROJECT_DIR/ssl/cert.pem
        
        # Reiniciar nginx
        cd $PROJECT_DIR
        docker compose -f docker-compose.prod.yml restart nginx
        echo "$(date): Nginx reiniciado após renovação" >> $LOG_FILE
    fi
else
    echo "$(date): Erro na renovação de certificados" >> $LOG_FILE
fi
EOF

chmod +x /usr/local/bin/servicehub-ssl-renew

# Configurar cron job para renovação
print_status "Configurando renovação automática no cron..."
echo "0 12 * * * /usr/local/bin/servicehub-ssl-renew" | crontab -u servicehub -

# Testar renovação
print_status "Testando renovação automática..."
certbot renew --dry-run

if [ $? -eq 0 ]; then
    print_status "Teste de renovação bem-sucedido!"
else
    print_warning "Teste de renovação falhou - verifique a configuração"
fi

# Reiniciar serviços
print_status "Reiniciando serviços..."
cd $PROJECT_DIR
docker compose -f docker-compose.prod.yml up -d

# Aguardar serviços iniciarem
sleep 10

# Verificar se os serviços estão rodando
print_status "Verificando status dos serviços..."
if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "Serviços iniciados com sucesso!"
else
    print_warning "Alguns serviços podem não ter iniciado corretamente"
fi

# Testar SSL
print_status "Testando configuração SSL..."
sleep 5

# Verificar se o certificado está funcionando
if curl -s -I https://$DOMAIN | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
    print_status "SSL configurado e funcionando!"
else
    print_warning "SSL pode não estar funcionando corretamente - verifique manualmente"
fi

# Mostrar informações do certificado
print_status "Informações do certificado:"
certbot certificates -d $DOMAIN

echo
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}✅ SSL/TLS configurado com sucesso!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo
echo -e "${BLUE}Seu site está disponível em:${NC}"
echo -e "  ${GREEN}https://$DOMAIN${NC}"
echo -e "  ${GREEN}https://www.$DOMAIN${NC}"
echo
echo -e "${BLUE}Certificado válido até:${NC}"
certbot certificates -d $DOMAIN | grep "Expiry Date" | awk '{print $3, $4, $5}'
echo
echo -e "${BLUE}Comandos úteis:${NC}"
echo "- Verificar certificados: certbot certificates"
echo "- Renovar manualmente: certbot renew"
echo "- Testar renovação: certbot renew --dry-run"
echo "- Logs de renovação: tail -f /var/log/servicehub/ssl-renew.log"
echo
echo -e "${YELLOW}IMPORTANTE:${NC}"
echo "- Os certificados serão renovados automaticamente"
echo "- Monitore os logs em /var/log/servicehub/ssl-renew.log"
echo "- Em caso de problemas, verifique o DNS do domínio"
