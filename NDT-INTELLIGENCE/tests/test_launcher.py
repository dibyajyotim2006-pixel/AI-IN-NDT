import os
import sys
import time
import socket
import urllib.request
import subprocess
import pytest
from launcher import find_free_port, acquire_single_instance_mutex, release_single_instance_mutex, terminate_process_tree, wait_for_server

def test_find_free_port():
    port = find_free_port()
    assert isinstance(port, int)
    assert 1024 <= port <= 65535

def test_single_instance_mutex():
    mutex = acquire_single_instance_mutex()
    assert mutex is not None
    release_single_instance_mutex(mutex)

def test_streamlit_worker_lifecycle():
    port = find_free_port()
    cmd = [sys.executable, "launcher.py", "--streamlit-worker", "--port", str(port)]
    proc = subprocess.Popen(cmd)
    
    try:
        healthy = wait_for_server(port, timeout_sec=30)
        assert healthy is True, f"Streamlit worker failed to become healthy on port {port}"
        
        # Test HTTP response
        url = f"http://127.0.0.1:{port}/_stcore/health"
        with urllib.request.urlopen(url, timeout=3.0) as resp:
            assert resp.status == 200
    finally:
        terminate_process_tree(proc)
        proc.wait(timeout=5)
        assert proc.poll() is not None
