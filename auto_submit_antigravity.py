"""
Auto-clicker for Antigravity's "Allow running this command?" dialog.
Detects the Antigravity window automatically at startup — no hardcoded titles.

Requirements:
    pip install pyautogui pillow opencv-python pywin32
"""

import time, sys, os, subprocess

def install_deps():
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "pyautogui", "pillow", "opencv-python", "pywin32"])

try:
    import pyautogui
    from PIL import ImageGrab
    import win32gui
except ImportError:
    print("Installing dependencies...")
    install_deps()
    import pyautogui
    from PIL import ImageGrab
    import win32gui

pyautogui.FAILSAFE = True

POLL_INTERVAL  = 1.5
TEMPLATE_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "submit_btn.png")
DIALOG_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dialog_header.png")
CONFIDENCE     = 0.70

# ── Detected at startup — no hardcoded titles ─────────────────────────────────
TARGET_HWND    = None   # the actual window handle we lock onto

def pick_target_window():
    """
    Lists all visible windows and asks the user to pick Antigravity.
    Stores the HWND so title changes never matter — we track the window itself.
    """
    global TARGET_HWND

    windows = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).strip()
            if title:
                windows.append((hwnd, title))
    win32gui.EnumWindows(cb, None)

    # Try auto-detecting Antigravity by executable name
    try:
        import win32process, psutil
        ag_windows = []
        for hwnd, title in windows:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                if "antigravity" in proc.name().lower() or "electron" in proc.name().lower():
                    ag_windows.append((hwnd, title, proc.name()))
            except Exception:
                continue

        if len(ag_windows) == 1:
            TARGET_HWND = ag_windows[0][0]
            print(f"  [✓] Auto-detected: '{ag_windows[0][1]}' (pid exe: {ag_windows[0][2]})")
            return
        elif len(ag_windows) > 1:
            print("\n  Multiple Electron windows found:")
            for i, (hwnd, title, exe) in enumerate(ag_windows):
                print(f"    {i+1}. {title} ({exe})")
            choice = int(input("  Pick the Antigravity window number: ")) - 1
            TARGET_HWND = ag_windows[choice][0]
            return
    except ImportError:
        pass  # psutil not installed — fall through to manual pick

    # Manual fallback — show all windows
    print("\n  Could not auto-detect. Pick Antigravity from the list:")
    for i, (hwnd, title) in enumerate(windows[:30]):   # cap at 30
        print(f"    {i+1:2}. {title}")
    choice = int(input("\n  Enter the number of the Antigravity window: ")) - 1
    TARGET_HWND = windows[choice][0]
    print(f"  [✓] Locked onto: '{windows[choice][1]}'")


def antigravity_is_open():
    """Check the locked HWND still exists."""
    return win32gui.IsWindow(TARGET_HWND)

def antigravity_is_focused():
    """Check the locked HWND is the foreground window."""
    return win32gui.GetForegroundWindow() == TARGET_HWND

# ─────────────────────────────────────────────────────────────────────────────

def image_visible(template_path):
    try:
        loc = pyautogui.locateOnScreen(template_path, confidence=CONFIDENCE)
        return loc is not None
    except pyautogui.ImageNotFoundException:
        return False
    except Exception:
        return False

def dialog_is_open():
    return image_visible(DIALOG_FILE)

def find_and_click_submit():
    try:
        loc = pyautogui.locateOnScreen(TEMPLATE_FILE, confidence=CONFIDENCE)
        if loc:
            cx, cy = pyautogui.center(loc)
            print(f"[✓] Submit found at ({cx}, {cy}) — clicking!")
            pyautogui.click(cx, cy)
            return True
    except pyautogui.ImageNotFoundException:
        pass
    except Exception as e:
        print(f"  [!] {e}")
    return False

def capture_image(label, save_path):
    print(f"\n[Setup] Capturing: {label}")
    print("  Make the Antigravity permission dialog visible on screen.")
    input("  Press ENTER when ready...")
    print(f"  Move mouse to TOP-LEFT of the {label} (5s)...")
    for i in range(5, 0, -1):
        print(f"    {i}...", end="\r", flush=True); time.sleep(1)
    x1, y1 = pyautogui.position()
    print(f"\n  Top-left: ({x1}, {y1})")
    print(f"  Move mouse to BOTTOM-RIGHT of the {label} (5s)...")
    for i in range(5, 0, -1):
        print(f"    {i}...", end="\r", flush=True); time.sleep(1)
    x2, y2 = pyautogui.position()
    print(f"  Bottom-right: ({x2}, {y2})")
    bbox = (min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2))
    img  = ImageGrab.grab(bbox=bbox)
    img.save(save_path)
    print(f"  [✓] Saved: {save_path} ({img.width}x{img.height}px)\n")

def main():
    # Step 1 — lock onto the Antigravity window by HWND
    print("=" * 54)
    print("  Antigravity Auto-Submit  |  CTRL+C to stop")
    print("=" * 54)
    print("\n[Setup] Detecting Antigravity window...")
    try:
        import psutil
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"],
                              stdout=subprocess.DEVNULL)
    pick_target_window()

    # Step 2 — capture templates if missing
    if not os.path.exists(DIALOG_FILE):
        capture_image("dialog header 'Allow running this command?'", DIALOG_FILE)
    if not os.path.exists(TEMPLATE_FILE):
        capture_image("Submit button", TEMPLATE_FILE)

    print("\n  ✅ Only clicks when permission dialog is open")
    print("  ✅ Pauses when Antigravity is not focused")
    print("  ✅ Auto-stops when Antigravity is closed")
    print("  ✅ Tracks window by handle — title changes don't matter\n")

    clicks = 0
    while True:
        try:
            if not antigravity_is_open():
                print("\n[✓] Antigravity closed — stopping.")
                break

            if not antigravity_is_focused():
                print("  [paused — Antigravity not focused]  ", end="\r")
                time.sleep(POLL_INTERVAL)
                continue

            if not dialog_is_open():
                print("  [watching for dialog...]            ", end="\r")
                time.sleep(POLL_INTERVAL)
                continue

            if find_and_click_submit():
                clicks += 1
                print(f"  Total clicks: {clicks}")
                time.sleep(2)
            else:
                time.sleep(POLL_INTERVAL)

        except pyautogui.FailSafeException:
            print("\n[!] Failsafe. Stopped.")
            break
        except KeyboardInterrupt:
            print(f"\n[!] Stopped. Total clicks: {clicks}")
            break

if __name__ == "__main__":
    main()
