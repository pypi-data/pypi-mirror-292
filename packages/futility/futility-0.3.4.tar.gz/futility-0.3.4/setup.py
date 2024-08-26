from setuptools import setup, find_packages


setup(
    name='futility',
    version='0.3.4',
    packages=find_packages(),
    scripts=['fim_scripts/fim.py'],
    entry_points={
        'console_scripts': [
            'fim=fim_scripts.fim:main',
        ],
    },

    package_data={
        'fim_scripts': ['default.cfg', '**/*'],
        'futility': ['**/*.py', '**/*.xml', '**/*.fz']
    },

    install_requires=[
        'numpy',
        'matplotlib',
        'pathlib',
        'astropy',
        'argparse',
        'configparser',
    ],
    author='Benny Border',
    author_email='borderbenja@gmail.com',
    description='various utilities for unpacking and analyzing .fits files',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/borderbenja05/futility',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
