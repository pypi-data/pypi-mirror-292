from distutils.core import setup
from setuptools import find_packages

VERSION = '2.0.1'

setup(name='wsection', version=VERSION, description='A python package to get properties of W-shaped steel section',
      author='Wenchen Lie', author_email='666@e.gzhu.edu.cn', install_requires=['pandas'], packages=find_packages(),
      package_data={"": ["*.csv", "*.rst"]})