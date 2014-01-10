#!/usr/bin/python3

try:
	from DistUtilsExtra.auto import setup
except ImportError:
	print("You need python-distutils-extra to compile the gettext po => mo files")
	print("ArchLinux: sudo pacman -S python-distutils-extra")
	print("Ubuntu:    sudo apt-get install python-distutils-extra")
	print("Fedora:    sudo yum install python-distutils-extra")

from distutils.core import Command

class proxychecker_test(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'test/'])
        raise SystemExit(errno)

setup(
    name="proxychecker",
    version = "1.0",
    description = "ProxyChecker and Hitfaker",
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
