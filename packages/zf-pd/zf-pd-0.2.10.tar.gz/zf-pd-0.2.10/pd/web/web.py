from click import group, option
from loguru import logger
from subprocess import Popen, PIPE

from .browser import get_page_source
from .utils import get_host


@group(name='web', help="Advanced web utilities")
def web():
    pass


@web.command(help="View a web page")
@option('-l', '--link', type=str, required=True, prompt=True,
        help="Link to the web page")
def view(link: str):
    logger.debug("web view")
    source = get_page_source(link)
    print(source)


@web.command(help="Renders a web page (Ctrl + C to exit)")
@option('-l', '--link', type=str, required=True, prompt=True,
        help="Link to the web page")
def render(link: str):
    logger.debug("web open")
    source = get_page_source(link)
    out_file = f"{get_host(link)}.html"
    with open(out_file, "w") as f:
        f.write(source)
    command = f"lynx {out_file}"
    p = Popen(command, shell=True)
    p.wait()
