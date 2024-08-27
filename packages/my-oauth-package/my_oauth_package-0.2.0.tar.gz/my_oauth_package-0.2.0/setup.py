from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='my_oauth_package',
    version='0.2.0',
    author='Romit',
    author_email='romitaherkar@gmail.com',
    description='A package for handling Xecurify authentication',
    long_description=long_description,
    long_description_content_type='text/markdown',

    #url='https://github.com/yourusername/my_auth_package',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    install_requires=[
        'cryptography',
        'pyjwt',
        'django',
    ],
)
