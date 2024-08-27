from setuptools import setup, find_packages
from vkmusix import __version__

setup(
    name="vkmusix",
    version=__version__,
    description="Библиотека для взаимодействия с VK Music. Документация: vkmusix.ru/docs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="thswq",
    author_email="admin@vkmusix.ru",
    url="https://github.com/to4no4sv/vkmusix",
    packages=find_packages(),
    install_requires=[
        "pytz == 2024.1",
        "httpx == 0.27.0",
        "aiofiles == 24.1.0",
        "selenium == 4.23.1",
        "webdriver_manager == 4.0.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
