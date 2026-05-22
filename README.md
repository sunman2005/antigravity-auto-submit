# Antigravity Auto-Submit

Automatically clicks the **Submit** button on Antigravity's
"Allow running this command?" permission dialog, so you don't have to.

---

## Requirements

- Windows PC
- Python 3.9 or newer → https://www.python.org/downloads/
  - ✅ During install, check **"Add Python to PATH"**

---

## One-Time Setup

### 1. Install Python dependencies
Open **Command Prompt** and run:
```
pip install pyautogui pillow opencv-python pywin32 psutil
```

### 2. Put the script in a folder
- `auto_submit_antigravity.py`
- *(Template images will be created automatically on first run)*

---

## First Run — Window Detection & Template Capture

1. **Open Antigravity first** so it's visible on screen.

2. Run the script:
   ```
   python auto_submit_antigravity.py
   ```

3. It will **auto-detect the Antigravity window** by its process name.
   - If found automatically, it confirms: `[✓] Auto-detected: 'window title' (Antigravity.exe)`
   - If multiple Electron windows are open, it shows a numbered list — pick the right one.

4. It will then ask you to capture **2 templates** (one-time only):

   **Template 1 — Dialog header**
   - Make the "Allow running this command?" dialog visible in Antigravity
   - Press ENTER, then move mouse to the **top-left** of the text "Allow running this command?" — wait 5 seconds
   - Move mouse to the **bottom-right** of the question mark — wait 5 seconds
   - ✅ `dialog_header.png` saved

   **Template 2 — Submit button**
   - Move mouse to the **top-left** of the blue Submit button — wait 5 seconds
   - Move mouse to the **bottom-right** of the Submit button — wait 5 seconds
   - ✅ `submit_btn.png` saved

> **Important:** The two corners must be at **different positions** — you are drawing a rectangle around the element. Make the selection generously — include a little padding around the text/button.

---

## Normal Use (After First Run)

Just run the script with Antigravity already open:
```
python auto_submit_antigravity.py
```

The script will:
- Auto-detect the Antigravity window by process (not window title)
- Only click Submit when the permission dialog is actually visible
- Pause automatically when you switch to another app
- Resume when you switch back to Antigravity
- Stop automatically when Antigravity is closed

---

## How to Stop

- Press **CTRL + C** in the terminal, **or**
- Move your mouse to the **very top-left corner** of your screen

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Re-install Python and check "Add to PATH" |
| `pip` not found | Run `python -m pip install ...` instead |
| Script crashes on template capture | Make sure you move to two **different** corner positions |
| Button not being clicked | Delete `submit_btn.png` and `dialog_header.png` and recapture |
| Says "not focused" even when Antigravity is open | Make sure Antigravity is the active foreground window |
| Multiple Electron windows listed | Pick the one titled with your project name |
| Script crashes immediately | Run Command Prompt as Administrator |
