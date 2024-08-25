from setuptools import setup, find_packages
import os,codecs


here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()
    
    
VERSION = '1.0.4'
DESCRIPTION = 'Currency Converter Rate'

# Setting up
setup(
    name="currency-converter-rate",
    version=VERSION,
    author="Muhammad Sameer",
    author_email="muhammadsameer.css@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests','cachetools'],

    keywords=['python', 'conversion', 'currency conversion','rate','curency rate package'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    url="https://github.com/SameerShiekh77/Currency-Conversion-Python-Package",
    python_requires='>=3.6',
)
