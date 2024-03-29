[comment]: <> (what cli does, treat it as the brochure of my car)

# powermole/gui

This program will let you perform port forwarding, redirect internet traffic, and transfer files to, and issue commands on,
a host without making a direct connection (ie. via one or more intermediate hosts), which would undoubtedly compromise your privacy.
This solution can only work when you or your peers own one or more hosts as this program communicates with SSH servers.
This program can be viewed as a multi-versatile wrapper around SSH with the ProxyJump directive enabled.
Powermole automatically creates a ssh/scp configuration file to enable key-based authentication with the intermediate hosts.

Powermolegui provides two modes:
* TOR mode
  *  The target destination host acts as an exit node (in TOR terminology).
* FOR(warding) mode
  *  Connections are forwarded to the target destination host.

Regardless which mode is enabled, several options are presented when the tunnel is established:
* COMMAND
  * This option provides a rudimentary terminal interface to provide access to OS services on the target destination host.
* TRANSFER
  * This options allows selected files to be transferred to the target destination host.


## Demo

### Running powermole with FOR mode enabled and option COMMAND is selected.

In this mode, connections are forwarded to the target destination host, on which, for example, an email server (e.g. Postfix) is running.
When the user has set the application directive in the configuration file, a program of choice will be started automatically.
For example, Mozilla Thunderbird.
In this demo, one gateway (intermediate host) is involved and option COMMAND is selected.

[comment]: <> (During the demo, highlight the words "local ports ... will be forwarded")
<img alt="powermole for mode with command" src="img/executing_powermolegui_for_1_gw_command.gif" width="650"/>

### Running powermole with TOR mode enabled ~~and option TRANSFER is selected~~.

In this mode, the target destination host acts as an exit node (in TOR terminology).
For the outside world, the web traffic seems to be originated from the last host.
Once the program states READY, a web browser of choice can be used to browse over the Internet.
In this demo, two gateways (intermediate hosts) are involved ~~and option TRANSFER is selected~~.
Note: the development of the TRANSFER option is discontinued.
Consider resorting to my other package named [powermolecli](https://github.com/yutanicorp/powermolecli).

[comment]: <> (During the demo, highlight the words "local port 8080 will be listening for web traffic")
<img alt="powermole tor mode with transfer" src="img/executing_powermolegui_tor_2_gw_transfer.gif" width="650"/>


## How it works

### Terminology
* **Tunnel** is an established connection from localhost to target destination host through intermediate hosts (called gateways).
* **Agent** is a python module running on the target destination host. It performs various functions.
* **Instructor** sends data and instructions to the *Agent* by utilizing a forwarded connection provided by *Tunnel*.

This cli package uses the lib package to create a Tunnel and models the specific Instructor to communicate with the Agent (on the target destination host).
The Agent communicates directly with the operating system of the host on which it resides.
The Agent is responsible to redirect internet traffic (TOR mode), put files (TRANSFER option), and issue commands (COMMAND option).
For port forwarding (FOR mode), the program simply relies on SSH itself. The Agent also responds to heartbeats send by localhost to check if connection is still intact.

![alt text](img/illustration_how_it_works.png)

For more details, including illustrations, please consult the [powermole library](https://github.com/yutanicorp/powermolelib) on GitHub.


## Requirements (functional)

* The client program only works on macOS and Linux (tested on macOS Ventura, Red Hat, CentOS, Fedora).
* The intermediate hosts (gateways) must be Linux.
* The client and all hosts have Python >3.9 as their default interpreter.
* You need _at least_ 1 gateway.
* You have the associated SSH identification file (i.e. the private key) for these intermediaries.
* Due to security reasons, SSH password login is not supported.
* This program doesn't require root privileges on the client (*to be confirmed*).


## Requirements (software)

### Linux
Follow these instructions to get Tkinter working on the *client*.

* Install Tk interface library
  * ``dnf install python3-tkinter``

### macOS (Ventura 13.4)
Follow these instructions to get Tkinter working with pyenv on the *client*.

* Install Xcode

* Install Brew
  * ``/bin/bash -c " $(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh ")``
  * ``brew install pyenv``

* Download and install (ActiveTcl-8.6) Tcl/Tk libraries
  * The Tkinter module is included with core Python, but you'll need a version of Tcl/Tk on your system to compile it against
    * Visit the ActiveState's website https://www.activestate.com/products/tcl/.
    * Register and download Tcl/Tk libraries for free.

* Edit Zsh shell file
  * Comment out any references to the system's Python interpreter
  * Add the following lines:
    * ``export PYENV_ROOT="$HOME/.pyenv"``
    * ``command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"``
    * ``eval "$(pyenv init -)"``

* Install Python interpreters (eg. 3.10.11)
  * ``pyenv install 3.10.11``
  * ``pyenv global 3.10.11``

* Test successful build of Python
  * ``python -m tkinter -c 'tkinter._test()'``


## Installation

If you use the standard packet manager:

```
$ pip install powermolegui
```
or if you use pipx:
```
$ pipx install powermolegui
```


## Usage

Issue this command to actually execute the program.

```
$ powermolegui
```

Powermole allows you to enter one of the modes listed below.
This is done by opening a [Configuration](https://github.com/yutanicorp/powermolegui#configuration) file.

The JSON file contains directives to enter one of the modes listed below:

* TOR mode
* FOR(warding) mode

In TOR mode, the target destination host acts as an exit node (in TOR terminology).

![alt text](img/illustration_tor.png)

In FOR(warding) mode, connections are forwarded to the target destination host, on which, for example, an email server (e.g. Postfix) is running and a local email client want to connect to its listening ports.

![alt text](img/illustration_forwarding.png)



## Configuration

#### To enable TOR mode

Edit the JSON document in the configuration file to incorporate the keywords **mode**, **gateways**, **destination**, and *optionally* **application** (shown below) and **port**.
When **application** is specified, powermole will start the application of choice once the tunnel is ready.
Please note, if an instance of that application (eg. Firefox) is already running, powermole will terminate immediately.
In the example below, powermole drills through 2 intermediate hosts.
Hitting Ctrl-C in terminal will dismantle the Tunnel (and stop the application).

~~Note: Each server has two interfaces.~~
~~If your servers don't have two interfaces, just use the ip address of "ip_in" for "ip_out".~~

```
    {
    "mode":         "TOR",
    "gateways":    [{"host_ip": "192.168.56.10",
                     "user": "root",
                     "identity_file": "/Users/vincent/.ssh/id_rsa_pl"},
                    {"host_ip": "192.168.56.11",
                     "user": "root",
                     "identity_file": "/Users/vincent/.ssh/id_rsa_cz"}],
    "destination": {"host_ip": "192.168.56.12",
                    "user": "root",
                    "identity_file": "/Users/vincent/.ssh/id_rsa_nl"},
    "application": {"binary_name": "firefox",
                    "binary_location": "/usr/bin/firefox"}
    }
```

#### To enable FOR(warding) mode

Edit the JSON document to incorporate the keywords **mode**, **gateways**, **destination**, **forwarders**, and *optionally* **application** and **port** (shown below).
In the example below, powermole drills through 1 intermediate host.
Hitting Ctrl-C in terminal will dismantle the Tunnel.

```
    {
    "mode":         "FOR",
    "gateways":    [{"host_ip": "192.168.56.10",
                     "port": 22,
                     "user": "root",
                     "identity_file": "/Users/vincent/.ssh/id_rsa_pl"}],
    "destination": {"host_ip": "192.168.56.11",
                    "port": 22,
                    "user": "root",
                    "identity_file": "/Users/vincent/.ssh/id_rsa_cz"},
    "forwarders": [{"local_port": 1587,
                    "remote_interface": "localhost",
                    "remote_port": 587},
                   {"local_port": 1995,
                    "remote_interface": "localhost",
                    "remote_port": 995}]
    }
```

## Error

When running into issues, consider investigating the log messages of type 'debug' sent to the shell and/or
consult the log file in /tmp on destination host.

## Development Workflow

The workflow supports the following steps

 * lint
 * test
 * build
 * document
 * upload
 * graph

These actions are supported out of the box by the corresponding scripts under _CI/scripts directory with sane defaults based on best practices.
Sourcing setup_aliases.ps1 for windows powershell or setup_aliases.sh in bash on Mac or Linux will provide with handy aliases for the shell of all those commands prepended with an underscore.

The bootstrap script creates a .venv directory inside the project directory hosting the virtual environment. It uses pipenv for that.
It is called by all other scripts before they do anything. So one could simple start by calling _lint and that would set up everything before it tried to actually lint the project

Once the code is ready to be delivered the _tag script should be called accepting one of three arguments, patch, minor, major following the semantic versioning scheme.
So for the initial delivery one would call

    $ _tag --minor

which would bump the version of the project to 0.1.0 tag it in git and do a push and also ask for the change and automagically update HISTORY.rst with the version and the change provided.


So the full workflow after git is initialized is:

 * repeat as necessary (of course it could be test - code - lint)
   * code
   * lint
   * test
 * commit and push
 * develop more through the code-lint-test cycle
 * tag (with the appropriate argument)
 * build
 * upload (if you want to host your package in pypi)
 * document (of course this could be run at any point)


## Important Information

This template is based on pipenv. In order to be compatible with requirements.txt so the actual created package can be used by any part of the existing python ecosystem some hacks were needed.
So when building a package out of this **do not** simple call

    $ python setup.py sdist

## Documentation

* Documentation: https://powermolegui.readthedocs.org/en/latest


## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

* **Vincent Schouten** - *Initial work* - [LINK](https://github.com/yutanicorp)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


## Acknowledgments

* Costas Tyfoxylos
* MisterDaneel (developer of pysoxy)

