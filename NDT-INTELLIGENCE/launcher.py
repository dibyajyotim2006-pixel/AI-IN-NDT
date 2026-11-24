"""
NDT Intelligence - Desktop Application Launcher
Manages single-instance mutex, dynamic port allocation,
background Streamlit worker process, and native PyWebView Edge Chromium window.
"""
import os
import sys
import time
import socket
import logging
import argparse
import ctypes
import subprocess
import urllib.request
import psutil

# Ensure paths helper is accessible
from paths import resource_path, get_log_path, user_data_dir

# Set up logging to %LOCALAPPDATA%\NDT Intelligence\logs\app.log
log_file = get_log_path()
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(process)d) %(message)s",
    encoding="utf-8"
)

MUTEX_NAME = "Local\\NDT_Intelligence_Desktop_App_Mutex"

def run_streamlit_worker(port: int):
    """
    Subprocess entry point to run the Streamlit server directly.
    Bypasses PyWebView to prevent recursive window spawning.
    """
    logging.info(f"Starting Streamlit worker on 127.0.0.1:{port}...")
    try:
        import streamlit.config as _config
        from streamlit.web import bootstrap
        app_path = resource_path("app.py")
        _config._main_script_path = os.path.abspath(app_path)
        
        flag_options = {
            "global.developmentMode": False,
            "server.port": port,
            "server.headless": True,
            "server.address": "127.0.0.1",
            "browser.gatherUsageStats": False,
            "server.fileWatcherType": "none",
        }
        bootstrap.load_config_options(flag_options=flag_options)
        
        cli_args = [
            "--global.developmentMode=false",
            f"--server.port={port}",
            "--server.headless=true",
            "--server.address=127.0.0.1",
            "--browser.gatherUsageStats=false",
            "--server.fileWatcherType=none",
        ]
        bootstrap.run(app_path, False, cli_args, flag_options)
    except Exception as e:
        logging.exception(f"Fatal error in Streamlit worker: {e}")
        sys.exit(1)


def acquire_single_instance_mutex():
    """
    Ensures only one instance of the desktop application runs at a time.
    """
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    ERROR_ALREADY_EXISTS = 183
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        ctypes.windll.user32.MessageBoxW(
            0,
            "NDT Intelligence is already running.\n\nPlease check your system taskbar.",
            "NDT Intelligence",
            0x40  # MB_ICONINFORMATION
        )
        sys.exit(0)
    return mutex


def release_single_instance_mutex(mutex):
    if mutex:
        try:
            ctypes.windll.kernel32.CloseHandle(mutex)
        except Exception:
            pass


def find_free_port() -> int:
    """Finds an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def wait_for_server(port: int, timeout_sec: int = 45) -> bool:
    """Polls the Streamlit health endpoint until responsive."""
    url = f"http://127.0.0.1:{port}/_stcore/health"
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    logging.info(f"Streamlit server is healthy on port {port}.")
                    return True
        except Exception:
            pass
        time.sleep(0.3)
    logging.error(f"Streamlit server failed to respond within {timeout_sec}s.")
    return False


def terminate_process_tree(proc):
    """Cleanly terminates the child process and all of its descendants."""
    if proc is None:
        return
    logging.info(f"Terminating process tree for PID {proc.pid}...")
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
    except Exception as e:
        logging.warning(f"Error terminating process tree: {e}")
        try:
            proc.kill()
        except Exception:
            pass


def main():
    import multiprocessing
    multiprocessing.freeze_support()

    parser = argparse.ArgumentParser(description="NDT Intelligence Desktop Launcher")
    parser.add_argument("--streamlit-worker", action="store_true", help="Internal flag to run Streamlit worker")
    parser.add_argument("--port", type=int, default=8501, help="Port for Streamlit worker")
    args, unknown = parser.parse_known_args()

    # Worker process branch
    if args.streamlit_worker:
        run_streamlit_worker(args.port)
        return

    # Main GUI desktop branch
    mutex = acquire_single_instance_mutex()
    logging.info("=" * 60)
    logging.info("NDT Intelligence Desktop App Launching")
    logging.info(f"Frozen: {getattr(sys, 'frozen', False)}")
    logging.info(f"Executable: {sys.executable}")
    logging.info(f"User Data Dir: {user_data_dir()}")

    port = find_free_port()
    logging.info(f"Allocated local port: {port}")

    # Launch worker in background with stdout/stderr redirected to log file
    with open(log_file, "a", encoding="utf-8") as f_log:
        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "--streamlit-worker", "--port", str(port)]
        else:
            cmd = [sys.executable, os.path.abspath(__file__), "--streamlit-worker", "--port", str(port)]

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        worker_proc = subprocess.Popen(
            cmd,
            stdout=f_log,
            stderr=f_log,
            creationflags=creation_flags
        )

    logging.info(f"Spawned Streamlit worker process PID: {worker_proc.pid}")

    # Wait for server readiness
    healthy = wait_for_server(port, timeout_sec=45)
    if not healthy:
        terminate_process_tree(worker_proc)
        release_single_instance_mutex(mutex)
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Failed to initialize the local analytics engine within 45 seconds.\n\nPlease check logs at:\n{log_file}",
            "NDT Intelligence - Startup Error",
            0x10  # MB_ICONERROR
        )
        sys.exit(1)

    # Launch PyWebView native Edge Chromium window
    try:
        import webview

        app_url = f"http://127.0.0.1:{port}"
        logging.info(f"Opening PyWebView window for {app_url}...")

        window = webview.create_window(
            title="NDT Intelligence — AI Concrete Strength Assessment",
            url=app_url,
            width=1280,
            height=840,
            min_size=(1024, 680),
            background_color="#0F172A",
            text_select=True,
            confirm_close=False
        )

        webview.start(gui="edgechromium", debug=False)
        logging.info("PyWebView window closed by user.")
    except Exception as e:
        logging.exception(f"PyWebView error: {e}")
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Error opening desktop window: {e}\n\nPlease check logs at:\n{log_file}",
            "NDT Intelligence Error",
            0x10
        )
    finally:
        # Clean up child processes and mutex
        terminate_process_tree(worker_proc)
        release_single_instance_mutex(mutex)
        logging.info("NDT Intelligence session ended cleanly.")


if __name__ == "__main__":
    main()
