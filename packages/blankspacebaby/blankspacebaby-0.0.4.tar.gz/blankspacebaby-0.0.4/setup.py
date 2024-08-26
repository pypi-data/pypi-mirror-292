from setuptools import setup, find_packages

setup(
    name='blankspacebaby',
    version='0.0.4',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'blankspacebaby=blankspacebaby.cli:typeset_text',
        ],
    },
    author='Hong-Sheng Lai',
    author_email='jl900613@gmail.com',
    description='How to Typeset Chinese and English Text',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hongsheng-lai/BlankSpaceBaby/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)