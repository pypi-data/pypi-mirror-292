from setuptools import setup, find_packages

setup(
    name="fanatics-api",
    version="3.0",
    py_modules=["main", "get_proxy", "json_to_excel"],
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
    description="include to csv/excel",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)