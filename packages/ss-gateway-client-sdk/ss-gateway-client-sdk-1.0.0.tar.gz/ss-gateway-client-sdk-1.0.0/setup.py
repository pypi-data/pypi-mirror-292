# 引入构建包信息的模块
from distutils.core import setup
import setuptools
with open("README.md", "r",encoding='utf8') as fh:
    long_description = fh.read()

# 定义发布的包文件的信息
setup(
    name = "ss-gateway-client-sdk",
    version = "1.0.0",
    description = "ss gateway from ningbo team,provider many services.include ocr,nlp etc.",
    author = "kongshanxuelin",
    url = "http://www.sumscope.com",
    author_email = "33666490@qq.com",
    packages=setuptools.find_packages(),
    py_modules = ['__init__','gateway_client','socket_client','snowflake_utils']
)