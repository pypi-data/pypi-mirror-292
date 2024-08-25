<p align="center">
    <b>Scrapper Porn API for Python</b>
    <br>
    <a href="https://github.com/AyiinXd/pyPorn">
        Homepage
    </a>
    •
    <a href="https://github.com/AyiinXd/pyPorn/releases">
        Releases
    </a>
    •
    <a href="https://t.me/AyiinChats">
        News
    </a>
</p>

## PyPorn

> Multiple Site Provider and Asynchronous API in Python

``` python
from pyPorn import PyPorn
from pyPorn.enums import Provider
from pyPorn.exception import PyPornError

pyPorn = PyPorn("YOUR_API_TOKEN")

try:
    content = pyPorn.getContent(Provider.XNXX, "video-u10yx0f....")
except PyPornError as e:
    print(e)
    return
else:
    print(content)
```


### Installation

``` bash
pip3 install pyPorn
```


### License

[MIT License](https://github.com/AyiinXd/pyPorn/blob/master/LICENSE)
