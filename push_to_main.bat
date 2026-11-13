@echo off
echo ========================================================
echo Pushing changes directly to main branch on GitHub
echo ========================================================
cd /d "%~dp0"

git push origin refactor/modular-architecture:main

echo.
echo ========================================================
echo PUSH TO MAIN COMPLETE!
echo ========================================================
pause
