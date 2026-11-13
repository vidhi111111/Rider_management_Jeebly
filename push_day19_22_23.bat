@echo off
echo ========================================================
echo Pushing Day 19-22-23 changes to GitHub
echo ========================================================
cd /d "%~dp0"

echo.
echo [1/3] Amending latest commit message to include 'day 19-22-23'...
git commit --amend -m "day 19-22-23: implement marshmallow schemas, query optimizations, database indexes and full api integration"

echo.
echo [2/3] Latest commit verification:
git log -1 --stat

echo.
echo [3/3] Pushing to GitHub (origin/refactor/modular-architecture)...
git push origin refactor/modular-architecture

echo.
echo ========================================================
echo PUSH COMPLETE!
echo ========================================================
pause
