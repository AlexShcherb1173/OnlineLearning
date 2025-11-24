param(
  # Можно передать путь к python.exe из venv, если хочешь
  [string]$PythonExe = ".venv\Scripts\python.exe"
)

Write-Host "🔧 Назначаем авторов постам без автора..." -ForegroundColor Cyan

# Выбираем интерпретатор: python из .venv, иначе системный python
if (Test-Path $PythonExe) {
  $py = $PythonExe
} else {
  Write-Host "⚠️  .venv не найден, использую системный python" -ForegroundColor Yellow
  $py = "python"
}

# Код, который выполним внутри Django shell
$code = @'
from django.contrib.auth import get_user_model
from django.apps import apps

# Проверка, что app "blog" установлен и миграции применены
if not apps.is_installed("blog"):
    print("❌ Приложение 'blog' не установлено (нет в INSTALLED_APPS).")
else:
    try:
        from blog.models import Post
    except Exception as e:
        print(f"❌ Невозможно импортировать blog.models.Post: {e}")
    else:
        User = get_user_model()
        u = User.objects.filter(is_staff=True).first() or User.objects.first()
        if not u:
            print("❌ Нет ни одного пользователя в базе — некого назначать автором.")
        else:
            updated = Post.objects.filter(author__isnull=True).update(author=u)
            print(f"✅ Назначено авторов для {updated} пост(ов). Автор: {u.email or u.username}")
'@

# Запуск manage.py shell с нашим кодом
& $py ".\manage.py" shell -c $code