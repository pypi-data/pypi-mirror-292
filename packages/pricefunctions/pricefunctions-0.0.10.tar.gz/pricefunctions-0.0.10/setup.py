from setuptools import find_packages, setup

with open('app/Readme.md','r') as f:
    long_description = f.read()
    
setup(
    name = 'pricefunctions',
    version='0.0.10',
    description='tool that converts OHLC price tables to candles',
    package_dir={'':'app'},
    packages = find_packages(where='app'),
    long_description = long_description,
    long_description_content_type='text/markdown',
    author = 'RichCoastTrading',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent'
        ],
    install_requires = ['pandas >= 2.2.2'],
    extra_requires = {'dev':['twine >= 5.1.1']},
    )
    
    