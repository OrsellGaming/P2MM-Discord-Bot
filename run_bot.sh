# Makes sure python modules are installed using pip
python3 -m pip install -r requirements.txt
# Enable tmux (must be installed) to allow safe remote disconnect
# Use "tmux attach" to return to the python session
tmux -2 -c -u
clear
# Start up the P2MM Discord Bot
python3 p2mmbot-main.py
# Close the tmux terminal whenever the Discord Bot shuts down
tmux C-b+x
# Pause script end for user input
echo "P2MM Discord Bot has been shutdown..."
read -p "Press [Enter] key to exit..."