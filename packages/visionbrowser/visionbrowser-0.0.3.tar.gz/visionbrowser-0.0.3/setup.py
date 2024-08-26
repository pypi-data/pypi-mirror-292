import codecs
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.3'
DESCRIPTION = 'Async API wrapper for Vision Browser'
LONG_DESCRIPTION = 'An asynchronous API wrapper for browser.vision, built to be reliable, simple and versatile.'

# Setting up
setup(
    name="visionbrowser",
    version=VERSION,
    author="europecdc",
    author_email="europecdc@hotmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['aiohttp', 'aiosignal', 'attrs', 'frozenlist', 'idna', 'multidict', 'yarl'],
    keywords=['python', 'undetected-browser', 'browser', 'vision', 'visionbrowser', 'api', 'wrapper'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
