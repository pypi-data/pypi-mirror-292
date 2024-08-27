from setuptools import setup
from setuptools_rust import Binding, RustExtension

with open("README.md") as f:
    long_description = f.read()

__version__ = "0.0.2"

setup(
    name="lesscode_encryption",
    description="lesscode_encryption是基于Rust语言开发的加密算法库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/navysummer/lesscode_encryption",
    rust_extensions=[RustExtension("lesscode_encryption", binding=Binding.PyO3)],
    packages=[],
    rust_extension_includes=["lesscode_encryption"],
    zip_safe=False,
)

"""
1、打包流程
打包过程中也可以多增加一些额外的操作，减少上传中的错误

# 先升级打包工具
pip install --upgrade setuptools wheel twine

# 打包
python setup.py sdist bdist_wheel

# 检查
twine check dist/*

# 上传pypi
twine upload dist/*

# 安装最新的版本测试
pip install -U lesscode_encryption -i https://pypi.org/simple
"""
