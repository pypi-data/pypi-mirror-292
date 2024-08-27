from setuptools import setup, find_packages

setup(
    name='sampy_cli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            'sampy_cli=src.cli:main',
        ],
    },
    author='Leo Hofer',
    author_email='contact@leohofer.dev',
    description='A simple CLI tool for sampling and plotting (weight) samples.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lumagician/sampy',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
