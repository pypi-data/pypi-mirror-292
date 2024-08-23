from setuptools import setup, find_packages

setup(
    name="git_pip",            # 包名
    version="0.1.0",                      # 版本号
    author="mantou",                   # 作者
    author_email="your.email@example.com",# 作者邮箱
    description="A brief description of the git_pip package",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mantouRobot/git_pip", # GitHub 仓库 URL
    packages=find_packages(),             # 自动发现包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',              # Python 版本要求
    install_requires=[                    # 依赖包列表
        "numpy",
        "requests",
        # 添加其他依赖库
    ],
    entry_points={
        'console_scripts': [
            'git_pip=git_pip.main:main',  # 创建一个名为 git_pip 的命令
        ],
    },
)
