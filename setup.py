#!/usr/bin/python3

from sys import executable,stderr,exit,version

if version < "3":
	stderr.write("You need python3 to run this!\n")
	stderr.write("ArchLinux:     sudo pacman -S python3\n")
	stderr.write("Ubuntu/Debian: sudo apt-get install python3\n")
	stderr.write("Fedora:        sudo yum install python3\n")
	exit(1)

import subprocess

try:
	from DistUtilsExtra.auto import setup
except ImportError:
	stderr.write("You need python-distutils-extra to compile the gettext .po to .mo files!\n")
	stderr.write("ArchLinux:      sudo pacman -S python-distutils-extra\n")
	stderr.write("Ubuntu/Debian:  sudo apt-get install python-distutils-extra\n")
	stderr.write("Fedora:         sudo yum install python-distutils-extra\n")
	exit(1)

from distutils.core import Command

class proxychecker_test(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        errno = subprocess.call([executable, 'test/'])
        raise SystemExit(errno)

setup(
    name="proxychecker",
    version = "git",
    description = "A Advanced, Multithreaded ProxyChecker and Hitfaker",
    author = "Jan Helbling",
    author_email = "jan.helbling@gmail.com",
    url = "http://jan-helbling.no-ip.biz",
    download_url = "https://github.com/JanHelbling/ProxyChecker/archive/master.zip",
    keywords = ["Proxychecker","Hitfaker"],
    scripts=["bin/proxychecker"],
    cmdclass={"test" : proxychecker_test},
    license="LGPL-3+",
    platforms=["linux","darwin","freebsd","netbsd","unixware7"],
    long_description = """\
 Fetaures:
	- Multithreaded ( with fork)
	- Check site and good hit must contain string
	- Set timeout
	- Set number of Processes
	- Choose between Mobile/Desktop UserAgent
	- Add a HTTP_REFERER
	- Send POST-Requests
	- Send Cookies
        - Send a HTTP-Header
	- Colored Output
	- gzip support
	- Open website to regex for proxys
"""
)
