![link=https://badge.fury.io/py/midpoint-cli](https://badge.fury.io/py/midpoint-cli.svg)

## Midpoint CLI

This project is a command line client interface used to drive an Evolveum Midpoint identity management server.

The objectives of this tool are to enable:

* Administrator access to run tasks and review data
* Scripting for remote controlled automation
* Test scenarios implementation

The client currently supports:

* Users and Organizational units display
* User search
* Running tasks synchronously
* Retrieving object definitions of any kind
* Uploading objects from local files and applying patches

Features currently under development:

* Auto completion to search of IDs or task names
* Improved task results display: retrieve and display a human readable status output
* Any other tasks that would be sumbitted in the issue tracker of this project on Gitlab

The strong points of this project are:

* All commands can be run directly or using an interactive prompt session
* Colorful output
* A user-friendly bash compatible command line history management
* Full interactive help system
* A classical midpoint-cli [command] [command options] syntax

## Usage

### General syntax

```bash
usage: midpoint-cli [-h] [-v] [-u USERNAME] [-p PASSWORD] [-U URL]
                    [command] [arg [arg ...]]

An interactive Midpoint command line client.

positional arguments:
  command               Optional command to be executed immediately.
  arg                   Optional command arguments.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Set the username to authenticate this session.
  -u USERNAME, --username USERNAME
                        Set the username to authenticate this session.
  -p PASSWORD, --password PASSWORD
                        Set the password to authenticate this session.
  -U URL, --url URL     Midpoint base URL

Available commands:
  get       Get an XML definition from the server from an existing OID reference.
  put       Create/Update a server object based on an XML structure.
  delete    Delete a server object based on its type and OID.

  task      Manage server tasks.
  resource  Manage resources on the server.

  org       Manage organizations.
  user      Manage users.

Midpoint-cli version 0.7.0, created and maintained by Yannick Kirschhoffer alcibiade@alcibiade.org
```

### Exernal configuration files (since v1.2)

Settings can be provided from an external configuration file. It can be either:

* .midpoint-cli.cfg in the home directory of the current user
* midpoint-cli.cfg in the current working directory

The syntax is as follows:

```
[Midpoint]
url = https://localhost:8080/midpoint/
username = administrator
password = ...
```

### Environment variables (since v1.2)

The script will scan environment variables to read input parameters. This is
particularily useful for injection of password or in-container execution.

The variables are:

* MIDPOINT_URL
* MIDPOINT_USERNAME
* MIDPOINT_PASSWORD

## Requirements

This program is compatible with Python version 3.7 or above.

## Installation

### Through PyPI

The most common way to install midpoint-cli on your own computer is to use the PyPI repository:

```bash
yk@lunar:~$ pip3 install midpoint-cli
Collecting midpoint-cli
  Downloading https://files.pythonhosted.org/packages/91/03/eaebde078e3560dfa919924d0a7c395f07a2e3fc9740223ea53db3afad05/midpoint-cli-0.7.0.tar.gz

[...]

Successfully built midpoint-cli clint tabulate args
Installing collected packages: args, clint, idna, urllib3, chardet, certifi, requests, tabulate, midpoint-cli
Successfully installed args-0.1.0 certifi-2019.9.11 chardet-3.0.4 clint-0.5.1 idna-2.8 midpoint-cli-0.7.0 requests-2.22.0 tabulate-0.8.5 urllib3-1.25.6

```

### Development build

To install the current development version from GIT:

```bash
yk@lunar:~/dev$ git clone https://gitlab.com/alcibiade/midpoint-cli.git
Cloning into 'midpoint-cli'...
remote: Enumerating objects: 374, done.
remote: Counting objects: 100% (374/374), done.
remote: Compressing objects: 100% (176/176), done.
remote: Total 374 (delta 229), reused 299 (delta 175)
Receiving objects: 100% (374/374), 62.84 KiB | 0 bytes/s, done.
Resolving deltas: 100% (229/229), done.

yk@lunar:~/dev$ pip3 install midpoint-cli/
Processing ./midpoint-cli
Collecting clint (from midpoint-cli===0.8-snapshot)
Collecting requests (from midpoint-cli===0.8-snapshot)
  Using cached https://files.pythonhosted.org/packages/51/bd/23c926cd341ea6b7dd0b2a00aba99ae0f828be89d72b2190f27c11d4b7fb/requests-2.22.0-py2.py3-none-any.whl
Collecting tabulate (from midpoint-cli===0.8-snapshot)
Collecting args (from clint->midpoint-cli===0.8-snapshot)
Collecting chardet<3.1.0,>=3.0.2 (from requests->midpoint-cli===0.8-snapshot)
  Using cached https://files.pythonhosted.org/packages/bc/a9/01ffebfb562e4274b6487b4bb1ddec7ca55ec7510b22e4c51f14098443b8/chardet-3.0.4-py2.py3-none-any.whl
Collecting urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1 (from requests->midpoint-cli===0.8-snapshot)
  Using cached https://files.pythonhosted.org/packages/e0/da/55f51ea951e1b7c63a579c09dd7db825bb730ec1fe9c0180fc77bfb31448/urllib3-1.25.6-py2.py3-none-any.whl
Collecting certifi>=2017.4.17 (from requests->midpoint-cli===0.8-snapshot)
  Using cached https://files.pythonhosted.org/packages/18/b0/8146a4f8dd402f60744fa380bc73ca47303cccf8b9190fd16a827281eac2/certifi-2019.9.11-py2.py3-none-any.whl
Collecting idna<2.9,>=2.5 (from requests->midpoint-cli===0.8-snapshot)
  Using cached https://files.pythonhosted.org/packages/14/2c/cd551d81dbe15200be1cf41cd03869a46fe7226e7450af7a6545bfc474c9/idna-2.8-py2.py3-none-any.whl
Building wheels for collected packages: midpoint-cli
  Running setup.py bdist_wheel for midpoint-cli ... done
  Stored in directory: /home/yk/.cache/pip/wheels/2a/5a/d6/54312f2db19e2a44cea90e4e1c186e7c1beb7192b4974db759
Successfully built midpoint-cli
Installing collected packages: args, clint, chardet, urllib3, certifi, idna, requests, tabulate, midpoint-cli
Successfully installed args-0.1.0 certifi-2019.9.11 chardet-3.0.4 clint-0.5.1 idna-2.8 midpoint-cli-0.7.0 requests-2.22.0 tabulate-0.8.5 urllib3-1.25.6

yk@lunar:~/dev$ midpoint-cli -v
Midpoint CLI Version 0.8-snapshot
```

### Anaconda

Anaconda packages are not available yet.

## Setting up a sanbox environment

If you wish to test this project locally and don’t have a midpoint server available, you can use the
following instructions.

### Using the Evolveum managed Docker image

Pull the image locally:

```bash
yk@lunar:~$ docker pull evolveum/midpoint
Using default tag: latest
latest: Pulling from evolveum/midpoint

[...]

Digest: sha256:1e29b7e891d17bf7b1cf1853c84609e414c3a71d5c420aa38927200b2bdecc8e
Status: Downloaded newer image for evolveum/midpoint:latest
docker.io/evolveum/midpoint:latest


```

Then run the server and bind the port 8080:

```bash
yk@lunar:~$ docker run -d --name midpoint-1 -p8080:8080 evolveum/midpoint
c048d519395ca48c8e94e361a2239b1c35c5e5305a29600895056e030d6a576f

yk@lunar:~$ midpoint-cli
Welcome to Midpoint client ! Type ? for a list of commands
midpoint> users
OID                                   Name           Title    FullName                Status    EmpNo    Email    OU
------------------------------------  -------------  -------  ----------------------  --------  -------  -------  ----
00000000-0000-0000-0000-000000000002  administrator           midPoint Administrator  enabled
midpoint>

yk@lunar:~$ docker stop midpoint-1
midpoint-1
```

## Deployment of a new version

* Update revision in src/midpoint_cli/__init__.py
* Commit and tag with corresponding version number
* Generate markdown documentation: downdoc README.adoc
* Build distribution: python setup.py sdist
* Upload distribution to PyPI: twine upload dist/*
