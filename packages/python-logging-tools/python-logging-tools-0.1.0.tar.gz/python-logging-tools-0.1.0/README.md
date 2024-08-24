![PyPI - Version](https://img.shields.io/pypi/v/python-logging-tools)
![GitHub Workflow Status](https://github.com/MGS-Daniil/python-logging-tools/actions/workflows/python-app.yml/badge.svg)
![GitHub Repo stars](https://img.shields.io/github/stars/MGS-Daniil/python-logging-tools)
# python logging tools
python package for modern logging

# installation
```commandline
pip install python-logging-tools
```

> [!WANING]  
> the project will be updated soon, but is not recommended for use now!

## usage:

```python
from colorama import Fore
import logging
import pylogging_tools

log = pylogging_tools.LoggingTools("Test pylog-tools", logging.INFO)
log.debug("debug")
log.warning("warning", color=Fore.BLUE)
```
output:
`[INFO]> [Name] - message`

## package:
- [x] this package simplifies logging in python
logging tools package
- [x] logging to file
- [x] logging levels are supported
- [X] colors are supported (not tested yet)
- [X] log formatting is supported 
- [ ] hide defualt logger
