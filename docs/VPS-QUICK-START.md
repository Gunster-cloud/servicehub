# Guia Rápido de Instalação VPS - ServiceHub

## 🚀 Instalação Automática

### Para AlmaLinux 9
```bash
curl -fsSL https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-almalinux.sh | bash -s "seu-dominio.com" "admin@seu-dominio.com"
```

### Para Ubuntu 22.04 LTS
```bash
curl -fsSL https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-ubuntu.sh | bash -s "seu-dominio.com" "admin@seu-dominio.com"
```

## 📋 Pré-requisitos

- **Servidor**: AlmaLinux 9, Ubuntu 22.04 LTS ou similar
- **Recursos**: Mínimo 2GB RAM, 2 cores CPU, 20GB SSD
- **Domínio**: Configurado apontando para o IP do servidor
- **Acesso**: Root ou sudo no servidor

## 🔧 Instalação Manual

### 1. Conectar ao servidor
```bash
ssh root@seu-ip-do-servidor
```

### 2. Baixar scripts
```bash
wget https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-almalinux.sh
# ou para Ubuntu:
wget https://raw.githubusercontent.com/seu-usuario/servicehub/main/deploy-ubuntu.sh
```

### 3. Executar instalação
```bash
# AlmaLinux
chmod +x deploy-almalinux.sh
./deploy-almalinux.sh "seu-dominio.com" "admin@seu-dominio.com"

# Ubuntu
chmod +x deploy-ubuntu.sh
./deploy-ubuntu.sh "seu-dominio.com" "admin@seu-dominio.com"
```

### 4. Configurar projeto
```bash
cd /opt/servicehub
git clone https://github.com/seu-usuario/servicehub.git .
cp env.prod.example .env
nano .env  # Configure as variáveis necessárias
```

### 5. Configurar SSL (Opcional)
```bash
wget https://raw.githubusercontent.com/seu-usuario/servicehub/main/scripts/setup-ssl-production.sh
chmod +x setup-ssl-production.sh
./setup-ssl-production.sh
```

### 6. Iniciar aplicação
```bash
docker compose -f docker-compose.prod.yml up -d
```

## ⚙️ Configuração do .env

Configure as seguintes variáveis no arquivo `.env`:

```bash
# Segurança
SECRET_KEY=sua-chave-secreta-muito-segura
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,seu-ip

# Banco de dados
DB_PASSWORD=sua-senha-segura-do-banco

# Email
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

## 🛠️ Comandos Úteis

### Gerenciamento da aplicação
```bash
# Iniciar
systemctl start servicehub

# Parar
systemctl stop servicehub

# Status
systemctl status servicehub

# Logs
docker compose -f /opt/servicehub/docker-compose.prod.yml logs -f
```

### Backup
```bash
# Backup manual
/usr/local/bin/servicehub-backup

# Verificar backups
ls -la /opt/backups/
```

### SSL
```bash
# Verificar certificados
certbot certificates

# Renovar manualmente
certbot renew

# Testar renovação
certbot renew --dry-run
```

## 🔍 Verificação

### Testar aplicação
```bash
# API
curl -k https://seu-dominio.com/api/schema/

# Frontend
curl -k https://seu-dominio.com/

# SSL
openssl s_client -connect seu-dominio.com:443
```

### Verificar serviços
```bash
# Status dos containers
docker compose -f /opt/servicehub/docker-compose.prod.yml ps

# Logs do sistema
journalctl -u servicehub -f

# Monitoramento
tail -f /var/log/servicehub/monitor.log
```

## 🚨 Solução de Problemas

### Container não inicia
```bash
# Verificar logs
docker compose -f /opt/servicehub/docker-compose.prod.yml logs nome-do-container

# Verificar configuração
docker compose -f /opt/servicehub/docker-compose.prod.yml config
```

### Problemas de SSL
```bash
# Verificar certificados
certbot certificates

# Verificar DNS
dig seu-dominio.com
```

### Problemas de banco
```bash
# Conectar ao banco
docker compose -f /opt/servicehub/docker-compose.prod.yml exec backend python manage.py dbshell

# Executar migrações
docker compose -f /opt/servicehub/docker-compose.prod.yml exec backend python manage.py migrate
```

## 📞 Suporte

Para problemas específicos:

1. Verifique os logs da aplicação
2. Consulte a documentação completa em `docs/VPS-INSTALLATION.md`
3. Verifique a documentação da API em `docs/API.md`
4. Abra uma issue no repositório do projeto

## 🔒 Segurança

### Configurações recomendadas

#### SSH
```bash
# Desabilitar login root
echo "PermitRootLogin no" >> /etc/ssh/sshd_config
systemctl restart sshd
```

#### Firewall
```bash
# AlmaLinux/CentOS
firewall-cmd --permanent --remove-service=ssh
firewall-cmd --permanent --add-rich-rule="rule family='ipv4' source address='SEU-IP' service name='ssh' accept"
firewall-cmd --reload

# Ubuntu/Debian
ufw deny ssh
ufw allow from SEU-IP to any port 22
```

#### Atualizações automáticas
```bash
# AlmaLinux/CentOS
dnf install -y dnf-automatic
systemctl enable dnf-automatic.timer

# Ubuntu/Debian
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

---

**Nota**: Este é um guia rápido. Para instruções detalhadas, consulte `docs/VPS-INSTALLATION.md`.
