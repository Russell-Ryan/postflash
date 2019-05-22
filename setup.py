from setuptools import setup,find_packages,Extension
import numpy.distutils.misc_util
import os
import postflash

setup(
    name=postflash.__code__,
    version=postflash.__version__,
    author=postflash.__author__,
    description=postflash.__description__,
    entry_points={'console_scripts':['postflash=postflash.postflash:main']},
    packages=find_packages(),
   # install_requires=['tkinter','argparse'],
    classifiers=[
        "Development Status :: 1 - Planning",
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy'],
    package_data={'postflash':['postflash/postflash.csv']})
