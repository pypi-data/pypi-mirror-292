import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="research_utils_pkg",  # 项目名称，保证它的唯一性，不要跟pypi上已存在的包名冲突即可
    version="0.0.1",  # 程序版本
    py_modules=['time_utils'],  # 需要上传的模块名称，这样可以让这些模块直接import导入
    author="leoye",  # 项目作者
    author_email="876720687@qq.com",  # 作者邮件
    description="useful tools I used in coding.",  # 项目的一句话描述
    long_description=long_description,  # 加长版描述
    long_description_content_type="text/markdown",  # 描述使用Markdown
    url="https://github.com/876720687/research_utils_pkg",  # 项目地址
    packages=setuptools.find_packages(),  # 无需修改
    classifiers=[
        "Programming Language :: Python :: 3",  # 使用Python3
        "License :: OSI Approved :: Apache Software License",  # 开源协议
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',    #对python的最低版本要求
)