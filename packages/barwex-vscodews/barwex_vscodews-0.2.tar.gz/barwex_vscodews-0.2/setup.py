from setuptools import setup, find_packages

setup(
    name="barwex-vscodews",
    version="0.2",
    author="barwe",
    author_email="barwechin@163.com",
    description="Create desktop shortcuts for vscode workspace",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "barwex-vscodews=barwex_vscodews.main:main",
        ],
    },
)
