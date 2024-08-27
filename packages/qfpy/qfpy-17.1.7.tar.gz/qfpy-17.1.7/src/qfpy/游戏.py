"""
class 识别区域类

def 切换到mumu()

def 点击(
    坐标: pag.Point,
    点击前延时: float = 0,
    点击后延时: float = 0,
    点击次数: int = 1,
    移动时间: float = 0.8,
)

def 获取图片坐标(
    图片路径: str, 识别区域: 识别区域类 = None, 图片相似度: float = 0.85
) -> pag.Point | None

def 等待图片出现(
    图片路径: str,
    识别区域: 识别区域类 = None,
    图片相似度: float = 0.85,
    超时时间: float = 5,
) -> tuple[bool, pag.Point]

def 点击图片(
    图片路径: str,
    点击前延时: float = 0,
    点击后延时: float = 0,
    识别区域: 识别区域类 = None,
    移动时间: float = 0.8,
    图片相似度: float = 0.85,
    超时时间: float = 5,
) -> pag.Point | None
"""

import random
from dataclasses import astuple, dataclass
from pathlib import Path

import pyautogui as pag
import win32api
import win32con
import win32gui
from PIL import Image

from qfpy.log import logger
from qfpy.图片 import 获取窗口截图


@dataclass
class 识别区域类:
    左: int
    上: int
    宽: int
    高: int


mumu_hwnd = win32gui.FindWindow("Qt5156QWindowIcon", "MuMu模拟器12")
mumuplayer_hwnd = win32gui.FindWindowEx(mumu_hwnd, 0, "Qt5156QWindowIcon", "MuMuPlayer")


def 切换到mumu():
    win32gui.SetForegroundWindow(mumu_hwnd)
    # 缩小：SW_RESTORE
    # 放大：SW_MAXIMIZE
    win32gui.ShowWindow(mumu_hwnd, win32con.SW_MAXIMIZE)
    pag.sleep(0.5)


def 点击_前台版(
    坐标: pag.Point,
    点击前延时: float = random.uniform(0.3, 0.6),
    点击后延时: float = 0,
    点击次数: int = 1,
    移动时间: float = 0.8,
):
    x, y = 坐标

    pag.moveTo(x, y, 移动时间)

    pag.sleep(点击前延时)

    多次点击间隔 = random.uniform(0.1, 0.2)
    pag.click(x, y, 点击次数, 多次点击间隔)

    pag.sleep(点击后延时)


def 点击_后台版(
    坐标: pag.Point, 点击前延时: float = random.uniform(0.5, 0.8), 点击后延时: float = random.uniform(0.5, 0.8)
):
    x, y = 坐标
    x, y = int(x) - 85, int(y) - 55  # 不知道为什么，存在偏差，需要减去偏移量
    position = win32api.MAKELONG(x, y)  # x,y为点击点相对于该窗口的坐标

    pag.sleep(点击前延时)

    win32api.SendMessage(
        mumuplayer_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, position
    )  # 向窗口发送模拟鼠标点击
    pag.sleep(random.uniform(0.25, 0.35))
    win32api.SendMessage(
        mumuplayer_hwnd, win32con.WM_LBUTTONUP, 0, position
    )  # 模拟释放鼠标左键

    pag.sleep(点击后延时)

点击 = 点击_后台版


def 点击链(坐标元组: tuple[pag.Point], 点击前延时: float = random.uniform(0.5, 0.8), 点击后延时: float = random.uniform(0.5, 0.8)):
    for 坐标 in 坐标元组:
        点击(坐标, 点击前延时, 点击后延时)


def 获取图片坐标(
    图片路径: str,
    识别区域: 识别区域类 = 识别区域类(0, 40, 1920, 983),
    图片相似度: float = 0.85,
) -> pag.Point | None:
    """获取图片坐标"""
    try:
        图片 = Image.open(图片路径)
        mumu截图 = 获取窗口截图(mumu_hwnd)
        识别区域 = astuple(识别区域) if 识别区域 else None
        pag.locateCenterOnScreen
        box = pag.locate(图片, mumu截图, confidence=图片相似度, region=识别区域)
        坐标 = pag.center(box) if box else None
        图片.close()
        return 坐标
    except pag.ImageNotFoundException:
        return None


def 等待图片出现(
    图片路径: str,
    识别区域: 识别区域类 = None,
    图片相似度: float = 0.85,
    超时时间: float = 5,
) -> tuple[bool, pag.Point]:
    """
    图片出现后返回 (True, 坐标)；否则返回 (False, None)
    """
    while True:
        if 超时时间 <= 0:
            logger.error("超时：" + Path(图片路径).stem)
            return (False, None)

        xy = 获取图片坐标(图片路径, 识别区域, 图片相似度)
        if xy:
            return (True, xy)

        pag.sleep(0.3)
        超时时间 -= 0.3


def 点击图片(
    图片路径: str,
    点击前延时: float = random.uniform(0.5, 0.8),
    点击后延时: float = random.uniform(0.5, 0.8),
    识别区域: 识别区域类 = None,
    移动时间: float = 0.8,
    图片相似度: float = 0.85,
    超时时间: float = 5,
) -> pag.Point | None:
    """点击图片

    默认一直等待图片出现，5 秒超时

    成功点击图片，返回坐标；失败返回 None
    """
    flag, xy = 等待图片出现(图片路径, 识别区域, 图片相似度, 超时时间)
    if not flag:
        return None

    # 随机偏移坐标
    xy = (
        xy[0] + random.randint(-5, 5),
        xy[1] + random.randint(-5, 5),
    )

    点击(xy, 点击前延时=点击前延时, 点击后延时=点击后延时)
    logger.info(f"{Path(图片路径).stem} {xy}")
    return xy

def 移动鼠标(坐标: pag.Point):
    wparam = 0
    x, y = 坐标
    x, y = int(x) - 85, int(y) - 55  # 不知道为什么，存在偏差，需要减去偏移量
    lparam = y << 16 | x
    win32api.SendMessage(mumuplayer_hwnd, win32con.WM_MOUSEMOVE, wparam, lparam)


if __name__ == "__main__":
    # 切换到mumu()
    pass
