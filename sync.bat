@echo off
:restart
echo "begin to push"
git push
if %errorlevel% != 0(
    goto restart
)
