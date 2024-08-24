import re
import threading
import time
import os
import signal


def kill_window_after_timeout(window: str, timeout: int):
    """
    Generates a thread that waits for a specified timeout and then kills the given window.

    Args:
        window (gw.Window): The window to be killed.
        timeout (int): The time in seconds to wait before killing the window.
    """
    def target():
        import pygetwindow as gw
        time.sleep(timeout)
        if "*" not in window:
            windows = gw.getWindowsWithTitle(window)
        else:
            windows = gw.getAllWindows()
            windows = [w for w in windows if w.title and re.match(re.escape(window), w.title)]

        for w in windows:
            w.close()
        print(f"killing window: {window} after {timeout} seconds")

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()


def kill_process_after_timeout(pid: int, timeout: int):
    """
    Generates a thread that waits for a specified timeout and then kills the process with the given PID.

    Args:
        pid (int): The process ID to be killed.
        timeout (int): The time in seconds to wait before killing the process.
    """
    def target():
        time.sleep(timeout)
        os.kill(pid, signal.SIGTERM)
        print(f"killing pid: {pid} after {timeout} seconds")

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

def kill_proc_after_timeout(proc : str, timeout : int):
    """
    Generates a thread that waits for a specified timeout and then kills the process with the given PID.
    """
    import psutil
    def target():
        time.sleep(timeout)
        for p in psutil.process_iter():
            if p.name() == proc:
                p.kill()
            elif "*" in proc and re.match(re.escape(proc).replace("\\*", ".*"), p.name()):
                p.kill()

        print(f"killing process: {proc} after {timeout} seconds")

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()