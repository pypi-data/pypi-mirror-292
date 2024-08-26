from setuptools import setup, find_packages

VERSION = '1.0.0'
DESCRIPTION = 'A fcntl solution for Windows Operating System'
LONG_DESCRIPTION = """A fcntl solution for windows Operating System that I made because I was frustrated with MoudleNotFound Errors
This is a copy of fcntl for python just that is Windows Operating System only compatiable that I made so windows Operating System users do not 
suffer from not having Macs (Mac and macOS are trademarks of Apple Inc., registered in the U.S. and other countries and regions.)
because many modules require fcntl and simply do not care that 72% of computer users are using Windows Operating System


HOW TO USE IT 

You may want to use it but it is supposed to be for other modules but you can still use it if you prefer to.


HOW TO USE FOR LIBRARY DEVELOPERS

Winfcntl has the same function names and everything is the same. 
All you need to do is check if the system is 'posix' or 'nt' (developers know what this is so if it looks wrong to you then it 
isn't for you) and import fcntl if posix and import winfcntl if nt and use the same function names, inputs (such as hello(a, b))

THANK YOU TO OUR CONTRIBUTERS
Kiamehr Eskandari

"""


setup(

    name = "winfcntl",
    version=VERSION,
    author="Kiamehr Eskandari",
    author_email="kiamehr13922014@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['fcntl', 'windows', 'module', 'package', 'library'],
    classifiers= [
        "Development Status :: 3 - Alpha", 
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "License :: Free To Use But Restricted",
        "Natural Language :: English",


    ],

)