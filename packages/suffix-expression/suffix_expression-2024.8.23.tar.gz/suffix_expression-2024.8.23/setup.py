import setuptools
with open('README.md','r',encoding='utf-8') as f:
    long_des = f.read()
setuptools.setup(
    name='suffix_expression',
    version='2024.8.23',
    author='Lighting Long',
    author_email='17818883308@139.com',
    description='后缀表达式处理库',
    long_description=long_des,
    url='https://github.com/longliangzhe/suffix_expression',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8'
)