import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_process()

    def restart_process(self):
        if self.process:
            self.process.kill()
        print("🔁 Reiniciando app...\n")
        self.process = subprocess.Popen(["python", "menu.py"])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.restart_process()

if __name__ == "__menu__":
    observer = Observer()
    handler = ReloadHandler()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()