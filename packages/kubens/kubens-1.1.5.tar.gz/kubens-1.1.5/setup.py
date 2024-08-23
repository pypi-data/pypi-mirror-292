#!/usr/bin/env python

import os
import shutil
from setuptools import setup, Command
import sys
import pprint

__version__ = '1.1.5'

class Doc(Command):
    description = "Custom doc command that converts README.md to the reStructured text file README.txt"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        print("Python path:")
        pprint.pprint(sys.path)
        try:
            import pypandoc
        except ImportError:
            print("pypandoc module not found, please install it using 'pip install pypandoc'")
            sys.exit(1)
        
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        try:
            description = pypandoc.convert_file('README.md', 'rst')
            with open('README.txt', 'w+') as f:
                f.write(description)
        except Exception as e:
            print("Error converting README.md to README.txt:", e)
            sys.exit(1)

class Clean(Command):
    description = "Custom clean command that forcefully removes dist/build directories"
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        shutil.rmtree("./build", ignore_errors=True)
        shutil.rmtree("./dist", ignore_errors=True)
        shutil.rmtree("./kubens.egg-info", ignore_errors=True)
        try:
            os.remove("./MANIFEST")
        except OSError:
            pass

setup(
    name='kubens',
    version=__version__,
    author='roubles',
    author_email='rouble@gmail.com',
    url='https://github.com/roubles/kubens',
    download_url='https://github.com/roubles/kubens/tarball/' + __version__,
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='terminal kubectl namespace selector',
    long_description=open('README.txt').read(),
    long_description_content_type='text/x-rst',
    packages=['kubens'],
    install_requires=['pick==2.3.2'],
    entry_points={
        'console_scripts': [
            'kubens=kubens.kubens:crux',
        ],
    },
    cmdclass={'doc': Doc, 'clean': Clean},
)
