import subprocess
import time

while True:
    print("Starting bot.py")
    process = subprocess.Popen(["python", "bot.py"])
    process.wait()
    time.sleep(5)  # Wait for 5 seconds before restarting the bot
