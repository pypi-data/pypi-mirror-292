import os

from mtmlib import mtutils
from mtmlib.env import in_jupyter_notebook
from mtmlib.mtutils import bash


def init_env():
    """
    根据环境进行必要的初始化
    """
    if in_jupyter_notebook():
        virtual_env = os.environ.get("VIRTUAL_ENV")
        print("当前虚拟环境名称 ", virtual_env)
        bash("pip install ipykernel")
        mtutils.install_packages_if_missing(["ipykernel"])
        # 提示，在colab 可以创建自定义的虚拟环境， 在 Colab 的 "Runtime" > "Change runtime type" 中选择 mtmtrain_env 作为内核。
        # bash("python -m ipykernel install --user --name=mtmtrain_env")
