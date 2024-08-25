# pd (Product Development and Deployment)

[![PyPI version](https://badge.fury.io/py/zf-pd.svg)](https://badge.fury.io/py/zf-pd)

<p align="center">
  <img src="https://zf-static.s3.us-west-1.amazonaws.com/pd-logo128.png" alt="PD"/>
</p>


`pd` is a command-line tool that helps you with various development and deployment tasks.

|     | Feature                         | Description                                                              |
| --- | ------------------------------- | ------------------------------------------------------------------------ |
| 1   | Project initialization (`init`) | Quickly initialize new development projects (e.g. FastAPI, Electron etc) |
| 2   | Content downloading (`down`)    | Download content from the internet (YouTube, Libgen).                    |
| 3   | File conversion (`conv`)        | Convert files into other formats (Image, Audio, Video).                  |
| 4   | EC2 instance management (`ec2`) | Manage EC2 instances (launch, terminate).                                |
| 5   | Image editing (`edit`)          | Edit images (scale, round, favicon, logo variants etc).                  |
| 6   | Web utilities (`web`)           | Inspect or view web pages in the terminal.                               |
| 7   | Environment management (`env`)  | Setup and configure development environment (zsh, vim, git, etc).        |
| 8   | Nginx management (`nginx`)      | Manage Nginx configuration files (proxy, static resources).              |

See [COMMANDS](./COMMANDS.md) for more details.

# Installation

```bash
pip install zf-pd
```

This installs a `pd` command in your system (even though the package name is `zf-pd`).

Like other shell tools, pd stores its config in `~/.pdconfig.json`.

See [CONFIG](./CONFIG.md) for more details.

# Usage

## Initializing a new Project

```bash
$ pd init fastapi --name /path/to/fastapi-test
```

This will create a new FastAPI project called `fastapi-test` inside `/path/to` directory.

## Downloading a YouTube video

```bash
pd down youtube -l https://www.youtube.com/watch?v=... -f mp4 # or mp3, text etc
```

This will output a file called `{TITLE}.txt` at the current directory.

## Downloading a Book

```bash
pd down libgen -n "Sun Tzu" -t "The Art of War"
```

This will output a file called `The Art of War.pdf` at the current directory.

## Generating logo varations

```bash
$ pd edit logos -p /path/to/logo.png -t iOS - "20%"

# Outputs
# /path/to/logo40.png
# /path/to/logo60.png
# ...
```

This will generate all required iOS logos with `20%` border radius at `/path/to` directory.

## Resizing multiple images

You can use the `resize` command to resize multiple images at once. You specify the dimensions using `-d "512x512"` and
`-n` specifies no suffix.

```bash
$ pd edit resize -p path/to/folder/*.png -d "512x512" -n

# Outputs
# Resized image saved as path/to/folder/0.png
# Resized image saved as path/to/folder/1.png
```

## Converting MP4 to MP3

```bash
$ pd conv video -p /path/to/file.mp4 -f mp3
```

This will output a file called `file.mp3` at `/path/to` directory.

## Processing a modern webpage

```bash
$ pd web view -l https://zeffmuks.com
```

This will display the renderred HTML source of the web page in the terminal.

You can query the rendered HTML using `htmlq`.

```bash
$ pd web view -l https://zeffmuks.com | htmlq ".css-17vaxo2"

<p class="chakra-text css-17vaxo2">Fast JSON5 Python Library</p>
...
<p class="chakra-text css-17vaxo2">Next Generation Content Platform</p>
```

## Launching an EC2 instance

You can launch an EC2 instance using a launch template as below:

```bash
$ pd ec2 launch -n ec2-test -c 1
````

This will launch 1 EC2 instance called `ec2-test` using the launch template specified in `~/.
pdconfig.json`.

Check out the [CONFIG.md](./CONFIG.MD) for more details.

## Generating an Nginx Config

You can generate a Nginx configuration file using the `generate` command.

```bash
$ pd nginx generate -h localhost -p 80 -d example.com -s /path/to/static
```

This will generate Nginx configuration for the given host, port, domain, and static file path.

## License

MIT License

