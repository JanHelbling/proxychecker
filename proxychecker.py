#!/usr/bin/python3
#
# (C) 2013 by Jan Helbling
# jan.helbling@gmail.com
# License: GNU/GPLv3
# Comment: Just another ProxyChecker in Python
#

import urllib.request
import http.client
import threading

from sys import exc_info,exit,argv
from socket import timeout

class proxychecker:
	def __init__(self,in_file,out_file,testsite,to,contains=""):
		try:
			self.in_file	=	open(in_file,"rb")
			self.proxys	=	self.in_file.readlines()
			self.out_file	=	open(out_file,"w")
		except IOError as e:
			print(sys.exc_info()[1])
			exit(1)
		
		self.to			=	to
		self.testsite		=	testsite
		self.contains		=	contains
		self.main()
	
	def check_proxy(self,proxy):
		proxy		=	proxy.rstrip("\r\n ")
		proxyhdl	=	urllib.request.ProxyHandler({'http':proxy})
		opener		=	urllib.request.build_opener(proxyhdl)
		
		try:
			fd	=	opener.open(self.testsite,timeout=self.to)
			content	=	(fd.read()).decode()
			fd.close()
			if self.contains in content:
				print("[OK]",proxy)
				self.save_proxy(proxy)
		except IOError as e:
			print("[FAIL]",proxy)
		except http.client.BadStatusLine as e:
			print("[FAIL]",proxy)
	
	def save_proxy(self,proxy):
		self.out_file.write(proxy+"\n")
		self.out_file.flush()
	
	def main(self):
		for proxy in self.proxys:
			proxy = proxy.decode("utf-8")
			self.check_proxy(proxy)
		self.in_file.close()
		self.out_file.close()
		print("[DONE!]")

if __name__ == "__main__":
	argc	=	len(argv)
	if argc != 6 and argc != 5:
		print("Usage:",argv[0]," <proxy.lst> <output> <testsite> <timeout> [ testsite must contains]")
		exit(0)
	if argc == 5:
		p	=	proxychecker(argv[1],argv[2],argv[3],float(argv[4]))
	elif argc == 6:
		p	=	proxychecker(argv[1],argv[2],argv[3],float(argv[4]),argv[5])
	exit(0)
