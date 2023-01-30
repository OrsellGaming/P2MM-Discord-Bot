@echo off

:: Makes sure python modules are installed using pip
python3 -m pip install -r "src/requirements.txt"
cls

:: Start up the P2MM Discord Bot
python3 "src/p2mmbot-main.py"

:: Pause script end for user input
echo "P2MM Discord Bot has been shutdown..."
pause