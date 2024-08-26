from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.8.5'
DESCRIPTION = 'Library for handling session metrics on TT'
LONG_DESCRIPTION = 'Library for handling session metrics on TT'

# Setting up
setup(
    name="tiktok_session_lite_sdk",
    version=VERSION,
    author="chickenfox23",
    author_email="chickenfox23@byt.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=[]
   )
