from setuptools import setup, find_packages

setup(
    name='yelib',
    packages=find_packages(),
    version='0.1.0',
    install_requires=[  # 添加了依赖的 package
        'numpy'
    ]
)
