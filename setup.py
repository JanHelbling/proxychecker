#!/usr/bin/python3

from DistUtilsExtra.auto import setup


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
    license="LGPL-3+",
    platforms=["linux"],
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
	- Colored Output
	- gzip support
	- Open website to regex for proxys

"""
)
