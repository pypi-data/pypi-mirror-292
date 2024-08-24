from setuptools import setup, find_packages
import os

if os.path.exists('requirements.txt'):
    with open('requirements.txt') as f:
        required = f.read().splitlines()
else:
    required = []

setup(
    name='hsuBug',
    version='0.1.0',
    description='一個自定義的抓取網頁資料的套件',
    author='LucasHsu',
    packages=find_packages(),
    install_requires=required,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)