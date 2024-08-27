"""
def rename_file(old_path: str | Path, new_name: str) -> Path
"""

from pathlib import Path

from qfpy.character import extract_valid_char, to_simplified_chinese
from qfpy.log import logger


def 重命名(旧路径: str | Path, 新名字: str) -> Path:
    """
    描述：重命名文件

    返回：新文件路径

    文件名冲突处理：添加后缀 _新
    """
    if isinstance(旧路径, str):
        旧路径 = Path(旧路径)

    新路径 = 旧路径.parent / 新名字

    while True:
        if 新路径.exists():
            新路径 = 旧路径.with_stem(旧路径.stem + "_新")

        if not 新路径.exists():
            旧路径.rename(新路径)
            break

    return 新路径

def 文件名标准化(旧路径: Path) -> Path:
    """
    标准化过程
    1. 保留中文、英文、数字、减号、下划线、点
    2. 繁转简

    如果成功标准化，执行重命名
    """
    旧名字 = 旧路径.name
    # 提取有效字符
    新名字 = extract_valid_char(旧名字)
    # 汉字化简
    新名字 = to_simplified_chinese(新名字)
    if 旧名字 == 新名字:
        return 旧路径
    # 重命名
    新路径 = 重命名(旧路径, 新名字)
    logger.info(f"重命名 {旧名字} -> {新名字}")
    return 新路径