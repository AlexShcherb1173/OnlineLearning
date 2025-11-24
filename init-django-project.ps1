param(
  [Parameter(Mandatory=$true)]
  [string]$ProjectName
)

$ErrorActionPreference = 'Stop'
#$PSStyle.OutputRendering = 'PlainText'

function Write-Info($msg){ Write-Host "[*] $msg" -ForegroundColor Cyan }
function Write-Ok($msg){ Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Err($msg){ Write-Host "[ERROR] $msg" -ForegroundColor Red }

# ---------- Pre-flight ----------
Write-Info "Checking Python in PATH..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Err "Python not found. Install Python 3.12+ and re-run."
  exit 1
}

# ---------- VENV ----------
Write-Info "Creating virtual environment .venv ..."
python -m venv .venv
. ".\.venv\Scripts\Activate.ps1"
Write-Ok "venv activated"

# upgrade pip
python -m pip install --upgrade pip setuptools wheel

# ---------- Packages ----------
Write-Info "Installing core packages (Django, DRF, psycopg2-binary, Pillow, dotenv, linters)..."
pip install `
  django `
  djangorestframework `
  psycopg2-binary `
  pillow `
  python-dotenv `
  black `
  flake8 `
  mypy `
  isort

# ---------- Django project ----------
Write-Info "Creating Django project: $ProjectName ..."
django-admin startproject $ProjectName .

# optional app
try { python manage.py startapp core | Out-Null } catch {}

# ---------- .env & .env_example ----------
Write-Info "Creating .env and .env_example ..."
@"
# === Django ===
DJANGO_SECRET_KEY=change-me-super-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# === Postgres ===
POSTGRES_DB=${ProjectName}_db
POSTGRES_USER=${ProjectName}_user
POSTGRES_PASSWORD=change-me-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# === SMTP ===
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USER=no-reply@example.com
SMTP_PASSWORD=change-me-smtp
"@ | Set-Content -NoNewline -Encoding UTF8 ".env"

Copy-Item ".env" ".env_example" -Force

# ---------- .gitignore ----------
Write-Info "Writing .gitignore ..."
@"
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so

# Virtual env
.venv/
venv/

# Django
*.log
*.sqlite3
media/
staticfiles/

# IDE
.idea/
.vscode/

# Env files
.env
.env.*.local

# OS
Thumbs.db
.DS_Store
"@ | Set-Content -Encoding UTF8 ".gitignore"

# ---------- Linters config ----------
Write-Info "Writing linters config ..."
@"
[tool.black]
line-length = 88
target-version = ["py312","py313"]

[tool.isort]
profile = "black"
"@ | Set-Content -Encoding UTF8 "pyproject.toml"

@"
[flake8]
max-line-length = 88
extend-ignore = E203,W503
exclude = .venv,venv,build,dist,migrations
"@ | Set-Content -Encoding UTF8 ".flake8"

@"
[mypy]
python_version = 3.13
ignore_missing_imports = True
disallow_untyped_defs = True
warn_unused_ignores = True
exclude = ^(.venv|venv|migrations)/
"@ | Set-Content -Encoding UTF8 "mypy.ini"

# ---------- README ----------
Write-Info "Writing README.md ..."
@"
# $ProjectName

Bootstrapped with PowerShell on Windows.

## Quickstart
1. `.\.venv\Scripts\Activate.ps1`
2. `python manage.py migrate`
3. `python manage.py runserver`

## Environment
See `.env_example` and create your `.env`.

## Linting
- `black .`
- `isort .`
- `flake8`
- `mypy .`
"@ | Set-Content -Encoding UTF8 "README.md"

# ---------- Patch settings.py ----------
Write-Info "Patching $ProjectName\settings.py for .env, Postgres, DRF, SMTP ..."
$sp = Join-Path -Path $PWD -ChildPath "$ProjectName\settings.py"
$content = Get-Content $sp -Raw

# 1) imports + dotenv
$content = $content -replace 'from\s+pathlib\s+import\s+Path\s*', @'
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
'@

# 2) SECRET_KEY / DEBUG / ALLOWED_HOSTS
$content = $content -replace 'SECRET_KEY\s*=.*', 'SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-me")'
$content = $content -replace 'DEBUG\s*=.*', 'DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"'
$content = $content -replace 'ALLOWED_HOSTS\s*=.*', 'ALLOWED_HOSTS = [h for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h]'

# 3) add DRF to INSTALLED_APPS
$content = $content -replace 'INSTALLED_APPS\s*=\s*\[', "INSTALLED_APPS = [`n    'rest_framework',"

# 4) DATABASES -> PostgreSQL (используем безопасную замену через MatchEvaluator)
$dbBlock = @"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', '${ProjectName}_db'),
        'USER': os.getenv('POSTGRES_USER', '${ProjectName}_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'change-me-password'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}
"@
$content = [regex]::Replace(
    $content,
    'DATABASES\s*=\s*\{[\s\S]*?\}',
    { param($m) $dbBlock }
)

# 5) SMTP блок — добавляем только если его ещё нет
if ($content -notmatch 'EMAIL_BACKEND\s*=') {
$smtp = @'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('SMTP_HOST', 'smtp.example.com')
EMAIL_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_USE_TLS = os.getenv('SMTP_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('SMTP_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD', '')
'@
    $content += "`r`n" + $smtp
}

Set-Content -Path $sp -Value $content -Encoding UTF8

# ---------- requirements ----------
Write-Info "Freezing requirements.txt ..."
pip freeze | Set-Content -Encoding UTF8 "requirements.txt"

# ---------- migrate ----------
Write-Info "Running initial migrations ..."
python manage.py migrate

# ---------- git init ----------
if (Get-Command git -ErrorAction SilentlyContinue) {
  Write-Info "Initializing git repository ..."
  git init | Out-Null
  git add . | Out-Null
  git commit -m "Initial Django bootstrap: $ProjectName (venv, linters, Postgres, SMTP, DRF, .env, README)" | Out-Null
}

Write-Host ""
Write-Ok "Project `"$ProjectName`" is ready."
Write-Host "- Activate venv:  .\.venv\Scripts\Activate.ps1"
Write-Host "- Run server:     python manage.py runserver"
Write-Host "- Open in PyCharm: File > Open... (select folder) and pick .venv as interpreter."