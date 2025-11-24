Write-Host "🚀 Проверка статуса Redis..." -ForegroundColor Cyan

# Проверяем, занят ли порт 6379 (Redis)
$redisProcess = Get-NetTCPConnection -LocalPort 6379 -ErrorAction SilentlyContinue

if ($redisProcess) {
    Write-Host "✅ Redis уже запущен (порт 6379 занят)." -ForegroundColor Green
}
else {
    Write-Host "⚙️  Redis не найден. Пытаемся запустить..." -ForegroundColor Yellow

    # 1️⃣ Попытка запустить Memurai (Windows Redis-совместимый сервер)
    $memuraiPath = "C:\Program Files\Memurai\memurai.exe"
    if (Test-Path $memuraiPath) {
        Write-Host "➡ Запуск Memurai..." -ForegroundColor Yellow
        Start-Process -FilePath $memuraiPath -ArgumentList "--service-start"
    }
    else {
        # 2️⃣ Попытка запустить Redis через Docker
        $dockerRunning = (docker ps --filter "name=redis" --format "{{.Names}}" 2>$null)
        if ($dockerRunning) {
            Write-Host "✅ Redis Docker контейнер уже запущен." -ForegroundColor Green
        }
        else {
            Write-Host "➡ Запускаем Redis через Docker..." -ForegroundColor Yellow
            docker run -d --name redis -p 6379:6379 redis | Out-Null
        }

        # 3️⃣ Если нет Docker — пробуем redis-server.exe вручную
        $redisExe = "C:\redis\redis-server.exe"
        if (Test-Path $redisExe) {
            Write-Host "➡ Запускаем Redis (portable версия)..." -ForegroundColor Yellow
            Start-Process -FilePath $redisExe -WindowStyle Hidden
        }
    }

    # Подождём немного, чтобы Redis успел подняться
    Start-Sleep -Seconds 3

    # Проверим повторно
    $check = Get-NetTCPConnection -LocalPort 6379 -ErrorAction SilentlyContinue
    if ($check) {
        Write-Host "✅ Redis успешно запущен и готов к работе." -ForegroundColor Green
    }
    else {
        Write-Host "❌ Не удалось запустить Redis. Проверь установку." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "💡 Подсказка:" -ForegroundColor Cyan
Write-Host "Redis доступен на redis://127.0.0.1:6379" -ForegroundColor Cyan
Write-Host "Проверка из Django: from django.core.cache import cache; cache.set('x',1); cache.get('x')" -ForegroundColor DarkGray
Write-Host ""