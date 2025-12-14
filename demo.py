import subprocess
import time
import random
import signal
import os

apps = ["Google Chrome", "GoLand"]
stay_time = 30

caffeinate_proc = subprocess.Popen(["caffeinate", "-dimsu"])

try:
    while True:
        app = random.choice(apps)
        subprocess.run([
            "osascript", "-e", f'tell application "{app}" to activate'
        ])
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 激活 {app}")
        time.sleep(stay_time)
except KeyboardInterrupt:
    # 退出时关闭 caffeinate
    caffeinate_proc.send_signal(signal.SIGTERM)