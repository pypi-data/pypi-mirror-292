"""
def remove_images(path: Path)
"""

from pathlib import Path

import pymupdf


def remove_images(path: Path | str):
    """
    删除PDF中的图片

    保存为：xxx_去图.pdf
    """
    if isinstance(path, str):
        path = Path(path)

    doc = pymupdf.Document(path)
    for page in doc:
        images = page.get_images()
        for img in images:
            doc._deleteObject(img[0])

    doc.save(path.with_stem(path.stem + "_去图"))