
from setuptools import setup, find_packages

setup(
    name='mr_openai_module',
    version='0.1.0',
    description='A module for interacting with OpenAI using prompt.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mahul Rana',
    author_email='mahulrana007@gmail.com',
    packages=find_packages(),
    install_requires=[
        'openai ==0.28'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
