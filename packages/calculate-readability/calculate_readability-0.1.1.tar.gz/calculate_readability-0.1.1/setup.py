from setuptools import setup
from setuptools import find_packages

with open('README.md', 'r') as f:
    readme = f.read()

setup(
    name="calculate-readability",
    version="0.1.1",
    py_modules=["calculate_readability"],
    install_requires=["divide-char-type", "count-syllable"],
    setup_requires=["divide-char-type", "count-syllable"],

    # metadata to display on PyPI
    author="Shinya Akagi",
    description="Calculate readability by using variable replacement model",
    long_description=readme,
    long_description_content_type='text/markdown',
    url="https://github.com/ShinyaAkagiI/calculate_readability", 
    license="PSF",
)
