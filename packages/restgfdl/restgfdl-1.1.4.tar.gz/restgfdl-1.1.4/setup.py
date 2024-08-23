from setuptools import setup, find_packages

VERSION = '1.1.4'

DESCRIPTION = 'Beta Package to implement REST API of Global Datafeeds'
LONG_DESCRIPTION = 'Package to implement REST API of Global Datafeeds. This api will provide  data as Ondemand request ' \
                   ' as well as historical data. '
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='restgfdl',
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6',
    author='Surendran M',
    author_email='surendran.m@globaldatafeeds.in',
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown', 
    readme="README.md",
    
    

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
