import os
import signal
import psutil
import pyautogui
import time
import win32gui
import win32con
import win32api

def close_browser(app_name):
    """Close the specified browser."""
    for proc in psutil.process_iter():
        try:
            if proc.name() in ['chrome.exe', 'firefox.exe', 'msedge.exe']:  # Add other browsers if needed
                if app_name.lower() in proc.name().lower():
                    proc.terminate()  # Terminate the process
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def close_edge():
    """Close Microsoft Edge browser."""
    return close_browser('msedge')

def close_current_tab():
    """Close the currently active browser tab using keyboard shortcut."""
    try:
        # Simulate Ctrl+W keyboard shortcut
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)  # Small delay to ensure the command is processed
        return True
    except Exception as e:
        print(f"Error closing tab: {str(e)}")
        return False

def minimize_window():
    """Minimize the currently active window using Win32 API."""
    try:
        # Get handle of the foreground window
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            # Post minimize message to the window
            win32api.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
            time.sleep(0.1)  # Small delay to let the minimize take effect
            return True
        return False
    except Exception as e:
        print(f"Error minimizing window: {str(e)}")
        return False 