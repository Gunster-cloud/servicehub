#!/bin/bash

# ServiceHub SSL/TLS Setup Script
# Este script configura SSL/TLS com Let's Encrypt

set -e

echo "=========================================="
echo "ServiceHub SSL/TLS Configuration"
echo "=========================================="

# Verificar se é root
if [[ $EUID -ne 0 ]]; then
   echo "Este script deve ser executado como root"
   exit 1
fi

# Solicitar domínio
read -p "Digite seu domínio (ex: servicehub.com.br): " DOMAIN
read -p "Digite seu email para notificações: " EMAIL

echo ""
echo "Instalando Certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

echo ""
echo "Gerando certificado SSL para $DOMAIN..."
certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

echo ""
echo "Copiando certificados..."
mkdir -p /home/ubuntu/servicehub/certs
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /home/ubuntu/servicehub/certs/
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /home/ubuntu/servicehub/certs/

echo ""
echo "Configurando renovação automática..."
certbot renew --dry-run

echo ""
echo "Atualizando nginx.prod.conf..."
# Criar backup
cp /home/ubuntu/servicehub/nginx.prod.conf /home/ubuntu/servicehub/nginx.prod.conf.bak

# Atualizar configuração
sed -i "s/server_name _;/server_name $DOMAIN www.$DOMAIN;/g" /home/ubuntu/servicehub/nginx.prod.conf
sed -i "s|# ssl_certificate /etc/letsencrypt|ssl_certificate /etc/letsencrypt|g" /home/ubuntu/servicehub/nginx.prod.conf
sed -i "s|# ssl_certificate_key /etc/letsencrypt|ssl_certificate_key /etc/letsencrypt|g" /home/ubuntu/servicehub/nginx.prod.conf

echo ""
echo "Reiniciando Nginx..."
docker-compose -f docker-compose.prod.yml restart nginx

echo ""
echo "=========================================="
echo "✅ SSL/TLS configurado com sucesso!"
echo "=========================================="
echo ""
echo "Seu site está disponível em:"
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"
echo ""
echo "Certificado válido até:"
certbot certificates -d $DOMAIN | grep "Expiry Date"
echo ""

