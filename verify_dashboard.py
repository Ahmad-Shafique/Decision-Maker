import requests
import time
import subprocess
import sys
import threading

def run_server():
    subprocess.run([sys.executable, "src/interfaces/api.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def verify():
    # Start server in background
    proc = subprocess.Popen([sys.executable, "src/interfaces/api.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Waiting for server...")
    time.sleep(5) # Give it time to start
    
    try:
        # Check root redirect
        print("Checking root redirect...")
        resp = requests.get("http://127.0.0.1:2947/", allow_redirects=False)
        if resp.status_code in [307, 301, 302]:
            print(f"Root redirect OK: {resp.status_code} -> {resp.headers['location']}")
        else:
            print(f"Root check failed: {resp.status_code}")

        # Check index.html
        print("Checking index.html...")
        resp = requests.get("http://127.0.0.1:2947/static/index.html")
        if resp.status_code == 200 and "<title>Principles-Based Decision System</title>" in resp.text:
            print("Dashboard served successfully!")
        else:
            print(f"Dashboard check failed: {resp.status_code}")
            
    except Exception as e:
        print(f"Verification failed: {e}")
    finally:
        proc.terminate()
        # force kill if needed
        proc.kill()

if __name__ == "__main__":
    verify()
