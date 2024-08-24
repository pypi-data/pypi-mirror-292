from setuptools import setup, find_packages

setup(
    name='mastermonitor',
    version='0.0.0',
    packages=find_packages(),
    author='Sergey Hovhannisyan',
    description='Python monitoring package utalizing managed terminal system.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='Apache License 2.0',
    url='https://github.com/sergey-hovhannisyan/mastermonitor',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)