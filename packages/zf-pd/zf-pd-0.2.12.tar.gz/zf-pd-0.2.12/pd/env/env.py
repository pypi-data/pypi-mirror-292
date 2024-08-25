from os import path as os_path
from subprocess import run as os_run

from click import argument
from click import group
from click import option
from loguru import logger


@group(name='env', help="Manage environments")
def env():
    pass


@env.command(help="Show an environment")
@option('-n', '--name', type=str, required=True, prompt=True,
        help='Name of the environment e.g. zsh, vim, git')
def show(name):
    logger.debug("env view")

    env_name = {
        'zsh': 'zshrc',
        'vim': 'vimrc',
        'git': 'gitconfig',
        'tmux': 'tmux.conf',
    }
    if name not in env_name:
        logger.error(f"Unknown environment {name}")
        return

    env_path = os_path.expanduser(f"~/.{env_name[name]}")
    logger.debug(f"env_path: {env_path}")

    if not os_path.exists(env_path):
        logger.error(f"Environment {name} not found")
        return

    with open(env_path, 'r') as f:
        print(f.read())
    return


@env.command(help="Activate an environment")
@argument('lang', type=str, required=True)
@argument('tool', type=str, required=True)
def up(lang: str, tool: str):
    logger.debug("env up")

    command = ""
    match lang:
        case 'py':
            match tool:
                case 'venv':
                    command = "source venv/bin/activate"
                case 'conda':
                    command = "conda activate"
                case _:
                    logger.error(f"Unknown tool {tool}")
        case _:
            logger.error(f"Unknown language {lang}")

    logger.debug(f"Run: {command}")
    os_run(command, shell=True)
    return


@env.command(help="Deactivate an environment")
@argument('lang', type=str, required=True)
@argument('tool', type=str, required=True)
def down(lang: str, tool: str):
    logger.debug("env down")

    command = ""
    match lang:
        case 'py':
            match tool:
                case 'venv':
                    command = "deactivate"
                case 'conda':
                    command = "conda deactivate"
                case _:
                    logger.error(f"Unknown tool {tool}")
        case _:
            logger.error(f"Unknown language {lang}")

    logger.debug(f"Run: {command}")
    os_run(command, shell=True)
    return


@env.command(help="Sync an environment")
@option('-n', '--name', type=str, required=True, prompt=True,
        help='Name of the environment e.g. zsh, vim, git')
def sync(name):
    logger.debug("env sync")
    return
