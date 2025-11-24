# =====================================================
# migrate_all.ps1 — выполняет все основные команды Django миграций
# Автор: AlexShcherbyna / SkyStore
# =====================================================

Write-Host ""
Write-Host "🚀 [1/4] Активируем виртуальное окружение..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "🧩 [2/4] Проверяем модели и создаём новые миграции..." -ForegroundColor Yellow
python manage.py makemigrations

Write-Host ""
Write-Host "🔄 [3/4] Применяем все миграции к базе данных..." -ForegroundColor Green
python manage.py migrate

Write-Host ""
Write-Host "🧹 [4/4] Проверяем текущее состояние миграций..." -ForegroundColor Magenta
python manage.py showmigrations

Write-Host ""
Write-Host "✅ Все миграции успешно применены!" -ForegroundColor Cyan
Pause