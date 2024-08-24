import logging
import pyscreeze


def boxcenter(box):
    """
    Calculate the center coordinates of the given box.

    Parameters:
        box : tuple or Box
            The input box for which to calculate the center coordinates.

    Returns:
        Point
            The center coordinates of the box as a Point object.
    """
    if isinstance(box, tuple):
        return pyscreeze.center(box)
    return pyscreeze.Point(box.left + box.width / 2, box.top + box.height / 2)


class commonImports:
    from pyscreeze import (  # noqa: E402
        center as center,
        locateAll as locateAll,
        locateAllOnScreen as locateAllOnScreen,
        locateCenterOnScreen as locateCenterOnScreen,
        locateOnScreen as locateOnScreen,
        locateOnWindow as locateOnWindow,
        pixel as pixel,
        pixelMatchesColor as pixelMatchesColor,
        screenshot as screenshot,
    )


def enable_fullscreenshot_win32():
    from pyscreeze import _screenshot_win32

    def _screenshot_win32_full(imageFilename=None, region=None, allScreens=True):
        return _screenshot_win32(imageFilename, region, allScreens)

    pyscreeze._screenshot_win32 = _screenshot_win32_full
    logging.info("overwritten pyscreeze._screenshot_win32")
