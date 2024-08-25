from setuptools import setup, find_packages

setup(
    name="app_tools_zxw",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        'httpx',
        'fastapi',
        'sqlalchemy',
        'jose',
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
