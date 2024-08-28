"""
# File       : api_errors.py
# Time       ：2024/8/22 09:39
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import HTTPException


class HTTPException_AppToolsSZXW(HTTPException):
    """自定义异常类"""

    def __init__(self, error_code: int,
                 detail: str,
                 http_status_code: int = 404):
        super().__init__(http_status_code,
                         detail={"error_code": error_code,
                                 "detail": detail})
