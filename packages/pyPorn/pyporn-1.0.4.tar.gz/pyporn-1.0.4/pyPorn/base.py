# MIT License

# Copyright (c) 2024 AyiinXd

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import requests
from typing import Union

from .enums import TypeField
from .exception import FieldError, ResponseError
from .types import Response
from .version import __version__


class Base:
    version = __version__
    apiToken: str
    baseUrl: str = "https://ayiinhub.vercel.app/api"
    def __init__(self, apiToken: str, path: Union[str, None] = None):
        self.apiToken = apiToken
        self.path = path if path else "downloads"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apiToken}"
        }

    def post(self, url: str) -> Response:
        req = requests.post(url, headers=self.headers)
        json = req.json()
        response: Response = Response(**json)
        if response.success:
            return response
        else:
            raise ResponseError(response.message)

    def get(self, url: str, type: TypeField):
        req = requests.get(url, headers=self.headers)
        if type.value == "stream":
            return req
        elif type.value == "json":
            json = req.json()
            response: Response = Response(**json)
            if response.success:
                return response
            else:
                raise ResponseError(response.message)
        else:
            raise FieldError(type.value, "is not valid. please use pyPorn.enums.TypeField")

    def validatePath(self, autoClean: bool = False):
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        
        if autoClean:
            for file in os.listdir(self.path):
                try:
                    os.remove(os.path.join(self.path, file))
                except FileNotFoundError:
                    pass
