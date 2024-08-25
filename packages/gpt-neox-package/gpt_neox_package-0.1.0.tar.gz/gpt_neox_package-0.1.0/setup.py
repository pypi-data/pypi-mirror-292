from setuptools import setup, find_packages

setup(
    name='gpt_neox_package',
    version='0.1.0',
    description='Custom extension for the transformers library including GPTNeoX models',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[],  # No mandatory dependencies
    extras_require={
        'transformers': ['transformers>=4.0.0'],
        'dev': ['pytest>=5.0'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

