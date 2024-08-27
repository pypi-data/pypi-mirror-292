# PyWebInfo

![Static Badge](https://img.shields.io/badge/python-3.10-blue?style=flat-square)
![PyPI - Version](https://img.shields.io/pypi/v/pywebinfo?link=https%3A%2F%2Fpypi.org%2Fproject%2Fpywebinfo%2F)



**pywebinfo** is a simple and easy-to-use Python module to extract metadata from a web page, ideal for the cards/previews of webpages within web applications.


## Installation

Currently pywebinfo supports Python 3.10 and onwards; Python 2 is not supported (not recommended). To install the current release:

```bash
pip install pywebinfo
```


## Usage

Minimal Example:

```python
from pywebinfo import PyWebInfo

pwi = PyWebInfo("https://www.python.org/")

# Title of the webpage | None
print(pwi.title)

# Description of the webpage | None
print(pwi.description)

# URL of webpage image | None
print(pwi.image)

# favicon of the webpage | None
print(pwi.favicon)

# URL
print(pwi.url)
```


## License

[MIT](LICENSE) © [Kaustubh Prabhu](https://github.com/kaustubhrprabhu)
