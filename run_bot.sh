#!/bin/bash

# Makes sure python modules are installed using pip
python3 -m pip install -r requirements.txt
clear

# Start up the P2MM Discord Bot
python3 p2mmbot-main.py

# Pause script end for user input
echo "P2MM Discord Bot has been shutdown..."
read -p "Press [Enter] key to exit..."