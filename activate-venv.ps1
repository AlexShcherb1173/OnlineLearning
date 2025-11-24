# activate-venv.ps1
# Универсальная активация виртуального окружения в Windows

$venvPath = "venv\Scripts"

if (Test-Path "$venvPath\Activate.ps1") {
    Write-Host "⚡ Активация venv через PowerShell..."
    . "$venvPath\Activate.ps1"
}
elseif (Test-Path "$venvPath\activate.bat") {
    Write-Host "⚡ Активация venv через CMD..."
    cmd /c "$venvPath\activate.bat"
}
elseif (Test-Path "$venvPath\activate") {
    Write-Host "⚡ Активация venv через Git Bash..."
    bash -c "source $venvPath/activate"
}
else {
    Write-Host "❌ Не удалось найти виртуальное окружение в $venvPath"
}