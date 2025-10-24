#!/bin/bash

echo "========================================"
echo "ServiceHub - Setup Script"
echo "========================================"
echo

echo "[1/4] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker não está instalado!"
    echo "Por favor, instale o Docker."
    exit 1
fi
echo "Docker OK!"

echo
echo "[2/4] Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERRO: Node.js não está instalado!"
    echo "Por favor, instale o Node.js 18+."
    exit 1
fi
echo "Node.js OK!"

echo
echo "[3/4] Instalando dependências do frontend..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar dependências do frontend!"
    exit 1
fi
cd ..
echo "Frontend OK!"

echo
echo "[4/4] Iniciando serviços Docker..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao iniciar serviços Docker!"
    exit 1
fi

echo
echo "========================================"
echo "Setup concluído com sucesso!"
echo "========================================"
echo
echo "Serviços disponíveis:"
echo "- API: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- Nginx: http://localhost:8080"
echo "- Admin Django: http://localhost:8000/admin/"
echo
echo "Para verificar o status dos serviços:"
echo "docker compose ps"
echo
