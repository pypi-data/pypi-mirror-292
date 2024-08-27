 ```commandline
 ██████╗ █████╗  ██████╗██╗  ██╗██████╗   
██╔════╝██╔══██╗██╔════╝██║  ██║██╔══██╗  
██║     ███████║██║     ███████║██████╔╝  
██║     ██╔══██║██║     ██╔══██║██╔══██╗  
╚██████╗██║  ██║╚██████╗██║  ██║██║  ██║  
 ╚═════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝  
```

# cachr: superfast, composable caching for Python
|         |                                                                                                                                                                                                                               |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Package | [![PyPI Latest Release](https://img.shields.io/pypi/v/cachr.svg)](https://pypi.org/project/cachr/) [![PyPI Downloads](https://img.shields.io/pypi/dm/cachr.svg?label=PyPI%20downloads)](https://pypistats.org/packages/cachr) |
| Meta    | ![GitHub License](https://img.shields.io/github/license/mike-huls/cachr)                                                                                                                                                      |

**cachr** is a Python package that provides superfast, composable caches designed to 
optimize your applications in an easy and intuitive way.
It aims to be the go-to package to use and build caches that make your applications 
superfast, memory-efficient and user-friendly.
```shell
pip install cachr
```

## Table of Contents
- [Main Features](#main-features)
- [Usage Example](#usage-example)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [License](#license)
- [Documentation](#documentation)
- [Development](#development)
- [Contributing to bloomlib](#contributing-to-bloomlib)

## Main Features
- 🐍 Pure Python
- 🖌 Easily extendable
- 👨‍🎨 User-friendly

## Usage Example

```python
import time
from cachr import LRUCache


# 1. Decorate your function
@LRUCache(capacity=2)
def add(i, y):
    time.sleep(1)
    print("adding..")
    return i + y


print(add(1, 2))    # <-- takes a second to calculate
print(add(1, 2))    # <-- takes value from cache immediately 
print(add(1, 2))    # <-- takes value from cache immediately 
```


## Installation
```sh
pip install cachr
```
The source code is currently hosted on GitHub at:
https://github.com/mike-huls/cachr

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/cachr).

## Dependencies
Bloomlib has no Python dependencies

## License
[MIT](LICENSE.txt)

## Documentation
🔨 Under construction

## Development
Find the changelog and list of upcoming features [here](doc/CHANGELOG.md).
<br>
**Contributions** are always welcome; feel free to submit bug reports, bug fixes, feature requests, documentation improvements or enhancements!

<hr>

[Go to Top](#table-of-contents)