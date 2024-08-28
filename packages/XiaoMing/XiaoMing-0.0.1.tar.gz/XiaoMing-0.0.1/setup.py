import setuptools #导入setuptools打包工具

setuptools.setup(
    install_requires=['shutils'],
    name="XiaoMing", # 用自己的名替换其中的YOUR_USERNAME_
    version="0.0.1",    #包版本号，便于维护版本
    author="XiaoMing5442",    #作者，可以写自己的姓名
    author_email="XiaoMing5442@outlook.com",    #作者联系方式，可写自己的邮箱地址
    description="一个自己的库",#包的简述
    long_description="一个自己的库",    #包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/XiaoMing5442/XiaoMing",    #自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.10',    #对python的最低版本要求
)
