from setuptools import setup, find_packages

setup(
    name='gpt_neox_package',
    version='0.1.1',
    description='Custom extension for the transformers library including GPTNeoX models',
    author='Ivan',
    author_email='ivan.okunevich@gmail.com',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
)

