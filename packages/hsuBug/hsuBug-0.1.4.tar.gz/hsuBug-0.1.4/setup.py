import pathlib
from setuptools import setup, find_packages
 
HERE = pathlib.Path(__file__).parent.resolve()
 
PACKAGE_NAME = "hsuBug"
AUTHOR = "LucasHsu"
AUTHOR_EMAIL = "lucashsu95@gmail.com"
URL = "https://github.com/lucashsu95/hsuBug"
DOWNLOAD_URL = "https://pypi.org/project/hsuBug/"
 
LICENSE = "MIT"
VERSION = "0.1.4"
DESCRIPTION = "BeautifulSoup + requests + tqdm + pandas的一個庫"
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf8")
LONG_DESC_TYPE = "text/markdown"
 
requirements = (HERE / "requirements.txt").read_text(encoding="utf8")
INSTALL_REQUIRES = [s.strip() for s in requirements.split("\n")]
 
CLASSIFIERS = [f"Programming Language :: Python :: 3.{str(v)}" for v in range(7, 12)]
PYTHON_REQUIRES = ">=3.7"
 
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    classifiers=CLASSIFIERS,
)