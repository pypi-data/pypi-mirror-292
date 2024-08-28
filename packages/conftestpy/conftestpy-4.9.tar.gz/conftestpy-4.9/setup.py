import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="conftestpy",
    version="4.9",
    author="teark",
    author_email="913355434@qq.com",
    description="the best conftestpy.py for pytest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/teark/seliky.git",
    packages=setuptools.find_packages(),
    install_requires=[
        'pytest-html==3.1.1',
        'pyecharts',
        'pillow',
        "py",
        'lxml',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
