import os
import re

from setuptools import find_packages, setup

__name__ = "protium"

# 读取版本号
version = {}
with open(os.path.join("protium", "version.py")) as fp:
    exec(fp.read(), version)


# 从 requirements.txt 文件中读取依赖项
def parse_requirements(filename):
    dependencies = []
    with open(filename, "r") as f:
        for line in f:
            # 去掉空行和注释
            if line.strip() and not line.startswith("#"):
                # 去掉 "protium" 依赖
                if "protium" not in line:
                    # 提取包名（忽略版本号或范围）
                    package_name = re.split(r"[<>=]", line.strip())[0].strip()
                    dependencies.append(package_name)
    return dependencies


setup(
    name=__name__,
    version=version["__version__"],
    author="Haohui",
    author_email="harveyquery@gmail.com",
    description="A simple example package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mile-Away/PROTIUM",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "ptm=protium.cli:cli",
        ],
    },
)
