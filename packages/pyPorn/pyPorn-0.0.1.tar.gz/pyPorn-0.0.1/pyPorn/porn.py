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

import aiofiles
import httpx
from typing import Union

from .base import Base
from .enums import Provider, TypeField
from .exception import PyPornError
from .types import Video, Videos


class PyPorn(Base):
    """PyPorn Client, the main means for interacting with API AyiinHub.

    Parameters:
        apiToken (``str``):
            API token for Authorization Users, e.g.: "AxD_ABCDEF1234ghIklzyx57W2v1u123ew11".
            Get the *API Token* in `https://pornauth.vercel.app/`.

        path (``str``, *optional*):
            Path For Download Content.
            Defaults to "downloads".
    """
    def __init__(
        self,
        apiToken: str,
        path: Union[str, None] = None
    ):
        super().__init__(
            apiToken=apiToken,
            path=path
        )

    async def getContent(self, provider: Provider, id: str) -> Video:
        """Get the Video by id.

        Parameters:
            provider (:obj:`~porn.enums.Provider`):
                Provider of the WebSite.

        Example:
            .. code-block:: python

                from porn import Porn

                porn = Porn(apiToken="YOUR_API_TOKEN")

                content = await porn.getContent(provider=Provider.XNXX, id="videoIdByProvider")
                print(content)
        """
        req = await self.post(f'{self.baseUrl}/{provider.value}/detail?id={id}')
        if not req.success:
            raise PyPornError(req.result)
        return Video(**req.result)

    async def searchVideo(self, provider: Provider, query: str, page: int = 0):
        """Search the Video by query.

        Parameters:
            provider (:obj:`~porn.enums.Provider`):
                Provider of the WebSite.

            query (``str``):
                Query for Search the Video.

            page (``int``, *optional*):
                Page Number for Search the Video in page.

        Example:
            .. code-block:: python

                from porn import Porn

                porn = Porn(apiToken="YOUR_API_TOKEN")

                # Without page
                contents = await porn.searchVideo(provider=Provider.XVIDEOS, query="korean girl")
                print(contents)

                # With page
                contents = await porn.searchVideo(provider=Provider.XVIDEOS, query="korean girl", page=1)
                print(contents)
        """
        req = await self.post(f'{self.baseUrl}/{provider.value}/search?key={query}&page={page}')
        if not req.success:
            raise PyPornError(req.message)
        return Videos(videos=req.result["data"])

    async def downloadContent(self, url: str, fileName: str):
        response = await self.get(url=url, type=TypeField.STREAM)
        if not isinstance(response, httpx._models.Response):
            raise PyPornError("The response is not a Httpx Response.")
        if response.status_code == 200:
            async with aiofiles.open(f'{self.path}/{fileName}.mp4', 'wb') as file:
                chunk = response.content
                await file.write(chunk)

            return f"{self.path}/{fileName}.mp4"
        else:
            raise PyPornError(f"Failed to download. Status Code: {response.status_code}")
