from setuptools import setup

setup(
    name='isolate',
    version='0.0.1',
    description='A Python package to interface with `isolate` sandboxes',
    long_description='A Python package to interface with `isolate` sandboxes',
    url='https://github.com/chowder/python-isolate',
    author='Andrew Chow',
    author_email='andrew@cho.io',
    license='MIT',
    packages=['isolate'],
    platforms=['posix'],
    python_requires=">=3.6"
)
