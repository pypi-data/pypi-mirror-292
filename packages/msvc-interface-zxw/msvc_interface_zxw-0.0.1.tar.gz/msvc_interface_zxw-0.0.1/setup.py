from setuptools import setup, find_packages

setup(
    name="msvc_interface_zxw",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi>=0.112.2,<0.113',
        'httpx>=0.23.3,<=0.27.0',
    ],
    author="薛伟的小工具",
    author_email="",
    description="bug fix: 微服务-用户权限验证 接口，调试完成，测试通过",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sunshineinwater/",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
