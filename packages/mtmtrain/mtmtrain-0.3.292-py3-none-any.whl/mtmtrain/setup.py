import subprocess

from setuptools import Command, setup


class PostInstallCommand(Command):
    """Post-installation for installation mode."""

    description = "Run custom post-installation tasks"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Running post-install tasks...")
        # 在这里执行自定义的 Python 函数
        subprocess.call(["python", "scripts/post_install.py"])


setup(
    name="mtmtrain",
    version="0.3.290",
    packages=["mtmtrain"],
    cmdclass={
        "install": PostInstallCommand,
    },
)
