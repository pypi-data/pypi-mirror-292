from setuptools import setup, find_packages

VERSION = '1.0.2'
DESCRIPTION = 'A Python module to simply extract metadata (title, description, image, favicon) of a webpage'

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='pywebinfo',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Kaustubh Prabhu',
    url='https://github.com/kaustubhrprabhu/pywebinfo',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4'
    ],
    keywords=['python', 'webpage', 'website', 'metadata']
)