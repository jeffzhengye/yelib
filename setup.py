from setuptools import setup, find_packages

setup(
    name='yelib',
    packages=find_packages(),
    version='0.1.1',
    install_requires=[  # 添加了依赖的 package
        'numpy'
    ],
    entry_points={
        "console_scripts": [
            "yelib = yelib.__main__:entry_point",
            "gelib = yelib.__main__:main",
        ]
    },
)
