import numpy as np
import win32con
import win32gui
import win32ui
from PIL import Image
from ppocronnx.predict_system import TextSystem

文本系统 = TextSystem()


def 识别单行文本(图片: Image) -> str:
    ndarray = np.asarray(图片)
    文本, 可信度 = 文本系统.ocr_single_line(ndarray)
    return 文本

def 获取窗口截图(hwnd: int) -> Image:
    w = 1920
    h = 1080

    # 返回句柄窗口的设备环境、覆盖整个窗口，包括非客户区，标题栏，菜单，边框
    hwndDC = win32gui.GetWindowDC(hwnd)
    # 创建设备描述表
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # 创建内存设备描述表
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)

    # 截图至内存设备描述表
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (10, 10), win32con.SRCCOPY)

    # 获取位图信息
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    # bmp 转 Image
    im = Image.frombuffer(
        "RGB", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]), bmpstr, "raw", "BGRX", 0, 1
    )

    # 内存释放
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return im


if __name__ == "__main__":
    pass
