


python --version 2>NUL
if errorlevel 1 goto errorNoPython

set cmd="python --version 2>NUL"

FOR /F %%i IN (' %cmd% ') DO SET PY_VERSION=%%i


python -suES %0 %*

:: Once done, exit the batch file -- skips executing errors sections
GOTO:EOF

:errorNoPython
echo.
echo Error^: Python not installed

:: Batch script will skip over zipapp contents
GOTO:EOF
:: Python zipapp contents below
:: ----------------------------
