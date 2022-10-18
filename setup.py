import os, sys
import glob
import setuptools

setuptools.setup(
    name='vouk',
    version='1.1.3',
    description='Switch to VOUK Domain',
    author='Tim Golden',
    author_email='tim.golden@global.com',
    install_requires = ['winsys', 'pywin32'],
    packages = ["vouk"],
    entry_points = {
        "console_scripts" : [
            "voukx=vouk.vouk:command_line",
        ]
    }
)
