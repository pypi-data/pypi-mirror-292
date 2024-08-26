from setuptools import setup, find_packages

setup(
    name="app_tools_zxw",
    version="1.0.25",
    packages=find_packages(),
    install_requires=[
        'pycryptodome',
        'fastapi',
        'jose',
        'aiohttp==3.10.5',
        'httpx>=0.23.3',
        'alipay-sdk-python==3.7.249',
        'qrcode'
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
