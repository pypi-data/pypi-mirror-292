from setuptools import setup, find_packages

setup(
    name='MCSContent',
    version='0.2',
    packages=find_packages(),
    install_requires=[
    ],
    author='Ray',
    author_email='fengrui@fengrui.asia',
    description='This is a module used to simplify what is returned by the MCStutas module',
    long_description=open('README.rst').read(),
    url='https://fengrui.link',
    license='LICENSE',
    py_modules=['content'],
)
