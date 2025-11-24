@echo off
REM ---------- Настройка ----------
REM Папки или файлы для проверки
set FILES=blog catalog config users


REM ---------- Форматирование ----------
echo Running black...
black %FILES%

echo Running isort...
rem isort %FILES%

REM ---------- Статический анализ ----------
echo Running flake8...
flake8 %FILES%

echo Running mypy...
rem mypy %FILES%

echo Done.
pause