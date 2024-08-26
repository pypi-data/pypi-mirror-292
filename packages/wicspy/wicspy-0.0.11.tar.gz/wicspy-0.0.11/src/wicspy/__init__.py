"""
Author: wicsp wicspa@gmail.com
Date: 2024-08-26 17:01:30
LastEditors: wicsp wicspa@gmail.com
LastEditTime: 2024-08-26 18:19:56
FilePath: /wicspy/src/wicspy/__init__.py
Description:


Copyright (c) 2024 by wicsp, All Rights Reserved.
"""


def hello() -> str:
    return "Hello from wicsp!"


from .bark import bark
from .timer_tool import timing


__all__ = ["bark", "timing"]
__version__ = "0.0.11"
