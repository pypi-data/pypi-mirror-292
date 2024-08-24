# Import setuptools

try:
    from setuptools import setup, find_packages
    _has_setuptools = True
except ImportError:
    from distutils.core import setup
    
# Setup parameters

DISTNAME = "infoFunWP"
VERSION = "0.1.1"
AUTHOR = "Jan Verwaeren"
AUTHOR_EMAIL ="Jan.Verwaeren@UGent.be"

DESC = "Wrapper around built in IO functions for reading text files - for teaching purposes"
with open("README.md", "r") as f:
    LONG_DESC = f.read()
LONG_DESC_TYPE = "text/markdown"

URL = "https://github.com/jverwaer/infoFun"
LICENSE = 'GNU'
INSTALL_REQUIRES = []

#PACKAGES=["rhsegmentor"]
PACKAGES = find_packages(include=['infoFunWP'])
CLASSIFIERS = [
              "Development Status :: 4 - Beta",
              "Programming Language :: Python :: 3",
              "Programming Language :: Python :: 3 :: Only",
              "Programming Language :: Python :: 3.9",
              "License :: OSI Approved :: GNU General Public License (GPL)",
              "Intended Audience :: Science/Research",
              "Operating System :: Microsoft :: Windows",
              "Operating System :: Unix",
              "Operating System :: MacOS",
]

# Setup

if __name__ == "__main__":
    
    setup(name=DISTNAME,
          version=VERSION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          description=DESC,
          long_description=LONG_DESC,
          long_description_content_type=LONG_DESC_TYPE,
          license=LICENSE,
          packages=PACKAGES,
          url=URL,
          download_url=URL,
          install_requires=INSTALL_REQUIRES,
          classifiers=CLASSIFIERS,
          include_package_data=True
         )