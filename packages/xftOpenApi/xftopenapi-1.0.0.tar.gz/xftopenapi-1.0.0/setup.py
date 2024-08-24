import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xftOpenApi",
    version="1.0.0",
    author="木子李",
    author_email="1537080775@qq.com",
    description="薪福通API接口SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/Muzi-Li-Chine/xftOpenApi.git",
    packages=setuptools.find_packages(),
    python_requires='>=3.6, <4',
    install_requires=[
        "gmssl>=3.2.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)