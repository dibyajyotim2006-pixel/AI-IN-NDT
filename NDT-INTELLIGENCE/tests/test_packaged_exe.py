import os
import sys
import time
import socket
import urllib.request
import subprocess
import pytest
import psutil

EXE_PATH = os.path.abspath(os.path.join("dist", "NDT Intelligence", "NDT Intelligence.exe"))

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        return s.getsockname()[1]

def terminate_process_tree(proc):
    if proc is None:
        return
    try:
        parent = psutil.Process(proc.pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except Exception:
                pass
        parent.terminate()
        _, still_alive = psutil.wait_procs(children + [parent], timeout=3)
        for p in still_alive:
            try:
                p.kill()
            except Exception:
                pass
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

def test_packaged_executable_exists():
    assert os.path.exists(EXE_PATH), f"Packaged executable not found at {EXE_PATH}"
    size_mb = os.path.getsize(EXE_PATH) / (1024 * 1024)
    print(f"Packaged executable size: {size_mb:.2f} MB")
    assert size_mb > 10.0

def test_packaged_executable_worker_boot():
    port = find_free_port()
    cmd = [EXE_PATH, "--streamlit-worker", "--port", str(port)]
    
    proc = subprocess.Popen(cmd)
    try:
        # Poll health endpoint
        healthy = False
        health_url = f"http://127.0.0.1:{port}/_stcore/health"
        for _ in range(40):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen(health_url, timeout=1.0) as resp:
                    if resp.status == 200:
                        healthy = True
                        break
            except Exception:
                pass
        
        assert healthy is True, f"Packaged executable failed to respond on port {port}"
        
        # Verify root index serves Streamlit UI
        root_url = f"http://127.0.0.1:{port}/"
        with urllib.request.urlopen(root_url, timeout=3.0) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            assert "Streamlit" in content or "NDT" in content
            
    finally:
        terminate_process_tree(proc)
        proc.wait(timeout=5)
        assert proc.poll() is not None

def test_user_data_directory_created():
    local_app_data = os.environ.get("LOCALAPPDATA")
    app_data_dir = os.path.join(local_app_data, "NDT Intelligence")
    assert os.path.isdir(app_data_dir)
    assert os.path.isdir(os.path.join(app_data_dir, "db"))
    assert os.path.isdir(os.path.join(app_data_dir, "logs"))
