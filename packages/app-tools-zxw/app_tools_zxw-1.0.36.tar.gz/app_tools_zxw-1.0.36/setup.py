from setuptools import setup, find_packages

setup(
    name="app_tools_zxw",
    version="1.0.36",
    packages=find_packages(),
    install_requires=[
        'pycryptodome>=3.20.0,<3.21.0',
        'fastapi>=0.112.2,<0.113',
        'jose>=1.0.0,<1.1.0',
        'aiohttp>=3.10.5,<3.11.0',
        'httpx>=0.23.3,<0.24.0',
        'alipay-sdk-python==3.7.249',
        'qrcode>=7.4.2,<7.5.0',
        'cryptography>=43.0.0,<44.0.0',
    ],
    author="xue wei zhang",
    author_email="",
    description="薛伟的小工具。",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunshineinwater/",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
