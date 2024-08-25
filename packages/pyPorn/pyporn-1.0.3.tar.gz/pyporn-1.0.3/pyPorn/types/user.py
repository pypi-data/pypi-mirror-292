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

from datetime import datetime


class User:
    def __init__(self, **kwargs):
        self.userId: str = kwargs.get("userId", "")
        self.userName: str = kwargs.get("userName", "")
        self.accessToken: str = kwargs.get("accessToken", "")
        self.token: str = kwargs.get("token", "")
        self.lastUsed: str = kwargs.get("lastUsed", "")
        self.requested: int = kwargs.get("requested", 0)
        self.createdAt: str = kwargs.get("createdAt", "")
        self.updatedAt: str = kwargs.get("updatedAt", "")

    def parser(self):
        return {
            "_": self.__class__.__name__,
            "userId": self.userId,
            "userName": self.userName,
            "accessToken": self.accessToken,
            "token": self.token,
            "lastUsed": self.lastUsed,
            "requested": self.requested,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt
        }
