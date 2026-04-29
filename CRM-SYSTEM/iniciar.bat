@echo off
title CRM Backend - Setup e Inicializacao

echo.
echo  ==========================================
echo     CRM Backend - Setup Automatico
echo  ==========================================
echo.

:: ─── Verifica Python ──────────────────────────────────────────────────────────
echo [1/6] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERRO: Python nao encontrado!
    echo  Baixe em: https://www.python.org/downloads/
    echo  Marque a opcao "Add Python to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYVER=%%i
echo  OK: %PYVER% encontrado.

:: ─── Cria ambiente virtual ────────────────────────────────────────────────────
echo.
echo [2/6] Criando ambiente virtual...
if exist ".venv" (
    echo  OK: Ambiente virtual ja existe.
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo  ERRO: Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo  OK: Ambiente virtual criado.
)

:: ─── Ativa e instala dependencias ─────────────────────────────────────────────
echo.
echo [3/6] Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo  ERRO: Falha ao ativar ambiente virtual.
    pause
    exit /b 1
)
echo  OK: Ambiente virtual ativado.

:: ─── Instala dependencias ─────────────────────────────────────────────────────
echo.
echo [4/6] Instalando dependencias (pode demorar um pouco)...
.venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo  ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)
echo  OK: Dependencias instaladas.

:: ─── Configura .env ───────────────────────────────────────────────────────────
echo.
echo [5/6] Configurando ambiente...
if not exist ".env" (
    copy .env.example .env >nul
    echo  OK: Arquivo .env criado.
) else (
    echo  OK: Arquivo .env ja existe.
)

:: ─── Seed do banco ────────────────────────────────────────────────────────────
echo.
echo [6/6] Configurando banco de dados...
if exist "instance\crm.db" (
    echo  Banco ja existe. Deseja recriar com dados de exemplo?
    echo.
    set /p RESEED="  Digite S para recriar ou ENTER para manter: "
    if /i "%RESEED%"=="S" (
        .venv\Scripts\python.exe seed.py
    ) else (
        echo  OK: Banco mantido.
    )
) else (
    .venv\Scripts\python.exe seed.py
)

:: ─── Inicia o servidor ────────────────────────────────────────────────────────
echo.
echo  ==========================================
echo     Setup concluido! Iniciando servidor...
echo  ==========================================
echo.
echo  Acesse no navegador:
echo  - http://localhost:5000/api/health
echo  - http://localhost:5000/api/clients/
echo  - http://localhost:5000/api/campaigns/
echo.
echo  Pressione Ctrl+C para parar o servidor.
echo.

.venv\Scripts\python.exe run.py

pause
