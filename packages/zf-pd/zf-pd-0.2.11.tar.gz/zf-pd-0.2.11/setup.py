from os import path as os_path
from subprocess import run as os_run

from loguru import logger
from setuptools import find_packages, setup

PACKAGE_NAME = "zf-pd"
AUTHOR_NAME = "Zeff Muks"
AUTHOR_EMAIL = "zeffmuks@gmail.com"

logger.debug(f"Building {PACKAGE_NAME} documentation")
os_run(["python", "docs.py"], capture_output=True, text=True)


def read_version():
    version_file = os_path.join(os_path.dirname(__file__), "pd", "version.py")
    with open(version_file) as file:
        exec(file.read())
    version = locals()["__version__"]
    logger.debug(f"Building {PACKAGE_NAME} v{version}")
    return version


def read_readme():
    data = ""
    with open("README.md", "r") as f:
        data = f.read()

    logo_open = data.find('<p align="center">')
    logo_close = data.find("</p>")

    logo_html = data[logo_open : logo_close + 4]

    url_start = logo_html.find('src="')
    url_end = logo_html.find('" alt=')
    url = logo_html[url_start + 5 : url_end]

    alt_start = logo_html.find('alt="')
    alt_end = logo_html.find('"/>', alt_start)
    alt = logo_html[alt_start + 5 : alt_end]

    return data[:logo_open] + f"![{alt}]({url})" + data[logo_close:]


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name=PACKAGE_NAME,
    version=read_version(),
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    description="pd supercharges your development workflows",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    package_data={
        "pd.config": ["templates/*"],
        "pd.init": [
            "templates/*",
        ],
        "pd.nginx": ["templates/*"],
    },
    install_requires=get_requirements(),
    packages=find_packages(include=["pd", "pd.*"], exclude=["venv", "venv.*"]),
    entry_points={"console_scripts": ["pd=pd.__main__:main"]},
)
