# ===========================================
# fill_db.ps1 — run Django management command "fill_db"
# Usage examples:
#   .\fill_db.ps1 default        # standard sample data
#   .\fill_db.ps1 fixtures       # load from fixtures
#   .\fill_db.ps1 random 20      # generate 20 random products
# ===========================================

param(
    [ValidateSet("default", "fixtures", "random")]
    [string]$mode = "default",
    [int]$count = 0
)

# Ensure venv exists
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Virtualenv not found (.venv). Activate or create it and try again." -ForegroundColor Red
    exit 1
}

$python = ".\.venv\Scripts\python.exe"
$manage = "manage.py"

Write-Host "Mode: $mode" -ForegroundColor Cyan

switch ($mode) {
    "fixtures" {
        Write-Host "Loading data from fixtures..." -ForegroundColor Yellow
        & $python $manage fill_db --from-fixtures
    }
    "random" {
        if ($count -le 0) {
            $count = Read-Host "Enter number of random products (e.g. 20)"
        }
        Write-Host "Generating $count random products..." -ForegroundColor Green
        & $python $manage fill_db --count $count
    }
    Default {
        Write-Host "Creating standard sample data..." -ForegroundColor Green
        & $python $manage fill_db --sample
    }
}

Write-Host ""
Write-Host "Done. Check products in admin or on the home page." -ForegroundColor Cyan
