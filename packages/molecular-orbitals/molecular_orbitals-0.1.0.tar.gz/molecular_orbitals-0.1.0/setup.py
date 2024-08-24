from setuptools import setup, find_packages

setup(
    name='molecular_orbitals',
    version='0.1.0',
    description='A Python library for modeling molecular orbitals and chemical reactions using quantum chemistry methods.',
    author='Daniil Krizhanovskyi',
    author_email='daniil.krizhanovskyi@hotmail.com',
    url='https://github.com/dkrizhanovskyi/molecular_orbitals',
    packages=find_packages(),  
    install_requires=[
        'numpy',
        'matplotlib',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'molecular_orbitals=molecular_orbitals.cli:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
