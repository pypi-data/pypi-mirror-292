from setuptools import setup, find_packages

setup(
    name="fanatics-api",
    version="2.8",
    py_modules=["main", "get_proxy"],
    entry_points={
        "console_scripts": [
            "fanatics-api=main:main",
        ],
    },
    install_requires=[
        "requests",
    ],
    author="Ruibin Zhang",
    author_email="ruibin.zhang021@icloud.com",
    description="Get more ip from xiecaiyun.com(8)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)