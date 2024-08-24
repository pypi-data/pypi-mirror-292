from setuptools import setup, find_packages

setup(
    name="fanatics-api",
    version="2.6",
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
    description="Fanatics API Data Fetcher Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)