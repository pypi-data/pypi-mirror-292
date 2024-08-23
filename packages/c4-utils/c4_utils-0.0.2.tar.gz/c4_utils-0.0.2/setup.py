from setuptools import setup

setup(
    name='c4-utils',
    description='c4.utils',
    author='QA Automation',
    version='0.0.2',
    packages=['c4.utils'],
    install_requires=['mss==3.0.1; python_version<"3.5"',
                      'mss==6.1.0; python_version>="3.5"'],
    classifiers=['Programming Language :: Python :: 3'],
)
