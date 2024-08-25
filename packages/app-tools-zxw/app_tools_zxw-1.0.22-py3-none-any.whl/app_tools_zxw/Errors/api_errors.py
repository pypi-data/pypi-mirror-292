"""
# File       : api_errors.py
# Time       ：2024/8/22 09:39
# Author     ：xuewei zhang
# Email      ：shuiheyangguang@gmail.com
# version    ：python 3.12
# Description：
"""
from fastapi import HTTPException


class HTTPError(Exception):
    """自定义异常类"""

    def __init__(self, error_code: int, detail: str, http_status_code: int = 404):
        super().__init__(detail)
        self.error_code = error_code
        self.http_status_code = http_status_code
        self.detail = detail

    def __str__(self):
        return f"[Error [http status:{self.http_status_code}], {self.error_code}]: {self.args[0]}"

    def to_fastapi_http_exception(self):
        return HTTPException(status_code=self.http_status_code, detail=self.detail)
