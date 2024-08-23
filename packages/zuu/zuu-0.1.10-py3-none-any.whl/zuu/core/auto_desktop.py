from time import sleep
import pyautogui
import pygetwindow as gw
import re


def type(
    *texts: str,
    is_path: bool = False,
    is_eval: bool = False,
    interval: int = 0,
    delay: int = 0,
    window: str = None,
):
    """
    Types the provided texts into a specified window or the active window.

    Parameters:
    - texts: The text strings to be typed.
    - is_path: If True, treat the texts as file paths and read content from them.
    - is_eval: If True, evaluate the text as a Python expression (e.g., slicing).
    - interval: The interval between each key press.
    - delay: Delay before starting to type.
    - window: The name or title regex of the window to focus on.
    """

    # Read and evaluate text from files if is_path is True
    if is_path:
        evaluated_texts = []
        for path in texts:
            if is_path:
                with open(path, "r") as file:
                    text = file.read()
            if is_eval:
                text = eval(text)
            evaluated_texts.append(text)
        texts = evaluated_texts
    else:
        # Evaluate text as expressions if is_eval is True
        if is_eval:
            texts = [eval(text) for text in texts]

    # Combine all text inputs into a single string
    full_text = "".join(texts)

    # Find the target window if specified
    target_window = None
    if window:
        # Use regex to match window title
        regex = re.compile(window)
        for win in gw.getAllWindows():
            if regex.search(win.title):
                target_window = win
                break

    # Focus on the target window if specified
    if target_window:
        while not target_window.isActive:
            sleep(1)
            target_window.activate()
    else:
        # Use the active window if no specific window is targeted
        target_window = gw.getActiveWindow()

    # Apply the delay before typing
    if delay:
        sleep(delay)

    # Type the text
    pyautogui.typewrite(full_text, interval=interval)
