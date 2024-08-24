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

from typing import List


class Assets:
    def __init__(self, **kwargs):
        self.embed: str = kwargs.get("embed", "")
        self.thumbnail: str = kwargs.get("thumbnail", "")
        self.bigimg: str = kwargs.get("bigimg", "")
        self.video: str = kwargs.get("video", "")

    def parser(self):
        return {
            "_": self.__class__.__name__,
            "embed": self.embed,
            "thumbnail": self.thumbnail,
            "bigimg": self.bigimg,
            "video": self.video
        }


class Data:
    def __init__(self, **kwargs):
        self.title: str = kwargs.get("title", "")
        self.id: str = kwargs.get("id", "")
        self.image: str = kwargs.get("image", "")
        self.duration: str = kwargs.get("duration", "")
        self.views: str = kwargs.get("views", "")
        self.rating: str = kwargs.get("rating", "")
        self.uploaded: str = kwargs.get("uploaded", "")
        self.upvoted: str = kwargs.get("upvoted", "")
        self.downvoted: str = kwargs.get("downvoted", "")
        self.models: List[str] = kwargs.get("models", [])
        self.tags: List[str] = kwargs.get("tags", [])

    def parser(self):
        return {
            "_": self.__class__.__name__,
            "title": self.title,
            "id": self.id,
            "image": self.image,
            "duration": self.duration,
            "views": self.views,
            "rating": self.rating,
            "uploaded": self.uploaded,
            "upvoted": self.upvoted,
            "downvoted": self.downvoted,
            "models": self.models,
            "tags": self.tags
        }


class Video:
    def __init__(self, **kwargs):
        self.data: Data = Data(**kwargs.get("data"))
        self.assets: Assets = Assets(**kwargs.get("assets"))
        self.source: str = kwargs.get("source", "")

    def parser(self):
        return {
            "_": self.__class__.__name__,
            "data": self.data.parser(),
            "assets": self.assets.parser()
        }


class TypeVideos:
    def __init__(self, **kwargs):
        self.link: str = kwargs.get("link", "")
        self.id: str = kwargs.get("id", "")
        self.title: str = kwargs.get("title", "")
        self.image: str = kwargs.get("image", "")
        self.duration: str = kwargs.get("duration", "")
        self.rating: str = kwargs.get("rating", "")
        self.video: str = kwargs.get("video", "")

    def parser(self):
        return {
            "_": self.__class__.__name__,
            "link": self.link,
            "id": self.id,
            "title": self.title,
            "image": self.image,
            "duration": self.duration,
            "rating": self.rating,
            "video": self.video
        }


class Videos:
    def __init__(self, videos: List[TypeVideos]):
        self.videos: List[TypeVideos] = []
        for video in videos:
            self.videos.append(TypeVideos(**video))

    def parser(self):
        return {
            "_": self.__class__.__name__,
            "videos": [video.parser() for video in self.videos]
        }