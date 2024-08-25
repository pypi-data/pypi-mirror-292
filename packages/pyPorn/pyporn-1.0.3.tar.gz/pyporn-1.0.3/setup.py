#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import re

from setuptools import setup, find_packages


with open("pyPorn/version.py", encoding="utf-8") as f:
    version = re.findall(r"__version__ = \"(.+)\"", f.read())[0]

with open("README.md", encoding="utf-8") as f:
    readme = f.read()


setup(
    name="pyPorn",
    version=version,
    description="Multiple Site Provider and Asynchronous API in Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/AyiinXd/pyPorn",
    download_url="https://github.com/AyiinXd/pyPorn/releases/latest",
    author="AyiinXd",
    author_email="ayiin@gotgel.org",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="api scrapper library python pornhub",
    project_urls={
        "Tracker": "https://github.com/AyiinXd/pyPorn/issues",
        "Community": "https://t.me/AyiinProjects",
        "Source": "https://github.com/AyiinXd/pyPorn"
    },
    python_requires="~=3.7",
    package_data={
        "pyPorn": ["py.typed"],
    },
    packages=find_packages(exclude=["tests*"]),
    zip_safe=False,
    install_requires=["requests"],
)
