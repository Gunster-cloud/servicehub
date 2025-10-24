@echo off
echo ========================================
echo ServiceHub - Setup Script
echo ========================================
echo.

echo [1/4] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Docker não está instalado ou não está rodando!
    echo Por favor, instale o Docker Desktop e inicie-o.
    pause
    exit /b 1
)
echo Docker OK!

echo.
echo [2/4] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Node.js não está instalado!
    echo Por favor, instale o Node.js 18+.
    pause
    exit /b 1
)
echo Node.js OK!

echo.
echo [3/4] Instalando dependências do frontend...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependências do frontend!
    pause
    exit /b 1
)
cd ..
echo Frontend OK!

echo.
echo [4/4] Iniciando serviços Docker...
docker compose up -d
if %errorlevel% neq 0 (
    echo ERRO: Falha ao iniciar serviços Docker!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup concluído com sucesso!
echo ========================================
echo.
echo Serviços disponíveis:
echo - API: http://localhost:8000
echo - Frontend: http://localhost:3000
echo - Nginx: http://localhost:8080
echo - Admin Django: http://localhost:8000/admin/
echo.
echo Para verificar o status dos serviços:
echo docker compose ps
echo.
pause
