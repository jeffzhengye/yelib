# yelib

collect and write lots of utils for NLP and computer vision. 

# install from github

* pip install git+https://github.com/jeffzhengye/yelib.git

# install from source

* git clone https://github.com/jeffzhengye/yelib.git
* cd yelib
* pip install -e .  # 或者以可编辑模式安装（开发模式）

# build whl

## 首先安装构建工具

* pip install build

## 构建源码分发包和轮子包

* python -m build

## 然后安装构建好的包

* pip install dist/yelib-0.1.1-py3-none-any.whl
