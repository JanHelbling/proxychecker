#!/usr/bin/python3
#
# (C) 2013 by Jan Helbling
# jan.helbling@gmail.com
# License: GNU/GPLv3 http://www.gnu.org/licenses/gpl-3.0.txt
# Comment: Just another ProxyChecker in Python
#

import urllib.request
import http.client
from os import fork,wait
from optparse import OptionParser

from sys import exc_info,exit,argv
from socket import timeout

class proxychecker:
	"""Another Proxychecker in Python"""
	def __init__(self,in_file,out_file,testsite,to,process_num,contains=""):
		"""Run's the programm."""
		try:
			# Open the proxylist to be checked and the outputfile
			self.in_file	=	open(in_file,"rb")
			self.proxys	=	self.in_file.readlines()
			self.out_file	=	open(out_file,"w")
		except IOError as e:
			print(exc_info()[1])
			exit(1)
		
		self.to			=	to
		self.testsite		=	testsite
		self.contains		=	contains
		self.process_num	=	process_num
		# Calling the Main-Function
		self.main()
	
	def check_proxy(self,proxy):
		"""Checks a proxy and save it to file, if the string "contains" is in content."""
		proxy		=	proxy.rstrip("\r\n ") # remove \r\n from the line
		proxyhdl	=	urllib.request.ProxyHandler({'http':proxy})
		opener		=	urllib.request.build_opener(proxyhdl) # Build a opener with the proxy
		
		try:
			fd	=	opener.open(self.testsite,timeout=self.to) # Open the website, with timeout to
			content	=	(fd.read()).decode("utf-8") # reads the content and decode it
			fd.close()
			if self.contains in content: #Check if the string contains is in content, if true
				print("[OK]",proxy)
				self.save_proxy(proxy) # write proxy to file
		except IOError as e:
			print("[FAIL]",proxy)
		except http.client.BadStatusLine as e:
			print("[FAIL]",proxy)
	
	def save_proxy(self,proxy):
		"""Save the proxy to file."""
		self.out_file.write(proxy+"\n")
		self.out_file.flush()
	
	def main(self):
		"""Main"""
		cnt = 0
		for proxy in self.proxys:
			if not fork(): # man fork
				proxy = proxy.decode("utf-8")
				self.check_proxy(proxy)
				exit(0)
			cnt = cnt + 1
			if cnt == self.process_num:
				for i in range(self.process_num):
					wait()
				cnt = 0
		self.in_file.close()
		self.out_file.close()
		print("[DONE!]")

if __name__ == "__main__":
	if len(argv) == 1:
		print("Invalid number of arguments! Use -h for options.")
		exit(0)
	# Parse options and run the proxychecker
	parser = OptionParser()
	parser.add_option("-i", "--input", dest="input",help="read proxys from file", metavar="FILE")
	parser.add_option("-o", "--output", dest="output",help="write proxys to file", metavar="FILE",default="checked_proxys.txt")
	parser.add_option("-u", "--testsite", dest="testsite",help="use this site for requests", metavar="WEBSITE",default="http://www.gnu.org")
	parser.add_option("-c", "--contains", dest="contains",help="good hit must contains", metavar="STRING",default="GNU")
	parser.add_option("-t", "--timeout", dest="to",help="timeout", metavar="TIMEOUT",type="float",default=5.0)
	parser.add_option("-p", "--process", dest="numproc",help="num of processes", metavar="NUM",default=10)
	(options, args) = parser.parse_args()
	p = proxychecker(options.input,options.output,options.testsite,options.to,options.numproc,options.contains)
