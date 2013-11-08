#!/usr/bin/python3
#
#    proxychecker.py is a multithreaded hitfaker and proxychecker
#
#    Copyright (C) 2013 by Jan Helbling <jan.helbling@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import urllib.request
import http.client
from os import fork,wait
from optparse import OptionParser

from sys import exit,argv
from socket import timeout

import random

useragent = ["Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
	"Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; SLCC1; .NET CLR 1.1.4322)",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0",
	"Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20100101 Firefox/24.0",
	"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0",
	"Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/24.0",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
	"Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14",
	"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; de) Presto/2.9.168 Version/11.52",
	"Lynx/2.8.8dev.3 libwww-FM/2.14 SSL-MM/1.4.1",
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2",
	"Mozilla/5.0 (X11; Linux 3.5.4-1-ARCH i686; es) KHTML/4.9.1 (like Gecko) Konqueror/4.9",
	"w3m/0.5.2 (Linux i686; it; Debian-3.0.6-3)"]

useragent_mobile = ["Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
	"Mozilla/4.0 (compatible; Linux 2.6.22) NetFront/3.4 Kindle/2.5 (screen 824x1200;rotate)",
	"Mozilla/5.0 (Linux; U; Android 2.3.3; zh-tw; HTC_Pyramid Build/GRI40) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari",
	"Mozilla/5.0 (iPhone; U; CPU iPhone OS 1_2_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
	"Mozilla/5.0 (iPad; U; CPU OS 4_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8F191 Safari/6533.18.5",
	"HTC_Touch_3G Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; IEMobile 7.11)",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)",
	"Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.1.0.346 Mobile Safari/534.11+"
	"Opera/12.02 (Android 4.1; Linux; Opera Mobi/ADR-1111101157; U; en-US) Presto/2.9.201 Version/12.02"]
	

class proxychecker:
	"""Another Proxychecker in Python"""
	def __init__(self,in_file,out_file,testsite,to,process_num,contains,referer,browserstring):
		"""Run's the programm."""
		try:
			# Open the proxylist to be checked and the outputfile
			self.in_file	=	open(in_file,"rb")
			self.proxys	=	self.in_file.readlines()
			self.in_file.close()
			self.out_file	=	open(out_file,"w")
		except IOError as e:
			print("Could not open",e.filename+":",e.strerror)
			exit(1)
		self.browserstring	=	browserstring
		self.referer		=	referer
		self.to			=	to
		self.testsite		=	testsite
		if not self.testsite.lower().startswith("http://"): #check if testsite starts with http://, if not
			self.testsite	=	"http://" + self.testsite # add http:// before the testsite
		self.contains		=	contains
		self.process_num	=	process_num
		# Calling the Main-Function
		self.main()
	
	def check_proxy(self,proxy):
		"""Checks a proxy and save it to file, if the string "contains" is in content."""
		proxy		=	proxy.decode("utf-8","replace").rstrip("\r\n ") # remove \r\n from the line
		proxyhdl	=	urllib.request.ProxyHandler({'http':proxy})
		opener		=	urllib.request.build_opener(proxyhdl) # Build a opener with the proxy
		if self.browserstring == "desktop": #check if browserstring is desktop or mobile
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent[random.randint(0,len(useragent)-1)])]
		elif self.browserstring == "mobile":
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent_mobile[random.randint(0,len(useragent_mobile)-1)])]
		else:
			print("Invalid Browserstring, use \"mobile\" or \"desktop\"!")
			exit(1)
		try:
			fd	=	opener.open(self.testsite,timeout=self.to) # Open the website, with timeout to
			content	=	(fd.read()).decode("utf-8","replace") # reads the content and decode it
			fd.close()
			if self.contains in content: #Check if the string contains is in content, if true
				print("\x1b\x5b\x33\x32\x6d[OK]",proxy)
				self.save_proxy(proxy) # write proxy to file
		except IOError as e:
			if e.strerror == None:
				print("\x1b\x5b\x33\x31\x6d[FAIL]",proxy,"\t--> Timed Out")
			else:
				print("\x1b\x5b\x33\x31\x6d[FAIL]",proxy,"\t-->",e.strerror)
		except http.client.BadStatusLine as e:
			print("\x1b\x5b\x33\x31\x6d[FAIL]",proxy,"\t--> BadStatusLine")
		except http.client.IncompleteRead as e:
			print("\x1b\x5b\x33\x31\x6d[FAIL]",proxy,"\t--> Incomplete Read")
		except KeyboardInterrupt as e:
			print("\x1b\x5b\x33\x31\x6d[ABORTED CTRL+C]",proxy, "\t--> Interrupted by User")
	
	def save_proxy(self,proxy):
		"""Save the proxy to file."""
		self.out_file.write(proxy+"\n")
		self.out_file.flush()
	
	def main(self):
		"""Main"""
		cnt = 0
		for proxy in self.proxys:
			if not fork(): # man fork
				self.check_proxy(proxy)
				exit(0)
			cnt = cnt + 1
			if cnt == self.process_num:
				for i in range(self.process_num):
					try:
						wait() # man wait
					except KeyboardInterrupt as e:
						exit(1)
				cnt = 0
		self.out_file.close()

if __name__ == "__main__":
	if len(argv) < 2:
		print("Invalid number of arguments! Use -h for options.")
		exit(0)
	# Parse options and run the proxychecker
	parser = OptionParser()
	parser.add_option("-i", "--input", dest="input",help="read proxys from file", metavar="FILE")
	parser.add_option("-o", "--output", dest="output",help="write proxys to file, default: checked_proxys.txt", metavar="FILE",default="checked_proxys.txt")
	parser.add_option("-u", "--testsite", dest="testsite",help="use this site for requests, default http://www.gnu.org", metavar="WEBSITE",default="http://www.gnu.org")
	parser.add_option("-c", "--contains", dest="contains",help="good hit must contains, default GNU", metavar="STRING",default="GNU")
	parser.add_option("-t", "--timeout", dest="to",help="timeout, default 5.0", metavar="TIMEOUT",type="float",default=5.0)
	parser.add_option("-p", "--process", dest="numproc",help="number of processes, default 10", type="int",metavar="NUM",default=10)
	parser.add_option("-r", "--referer", dest="referer",help="Use this site as referer, default None",metavar="REFERER",default="")
	parser.add_option("-b", "--browser-string", dest="browserstring", help="mobile or desktop, default desktop", metavar="TYPE",default="desktop")
	(options, args) = parser.parse_args()
	p = proxychecker(options.input,options.output,options.testsite,options.to,options.numproc,options.contains,options.referer,options.browserstring)
