from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.37'
DESCRIPTION = ''
LONG_DESCRIPTION = ''

setup(
    name="tabledai",
    version=VERSION,
    author="Vince Berry",
    author_email="vincent.berry11@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(exclude=['tabledai/create.py']),
    install_requires=['pandas', 'sqlalchemy', 'psycopg2-binary', 'python-dotenv', 'openai', 'chardet'],
    keywords=['python', 'ai', 'ml', 'nlp', 'sql', 'postgres'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)