from setuptools import setup, find_packages

setup(
    name="app_sdk_zxw",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'httpx==0.27.0',
        'fastapi==0.112.1',
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
