#!/usr/bin/python3
#
# (C) 2013 by Jan Helbling
# jan.helbling@gmail.com
# License: GNU/GPLv3 http://www.gnu.org/licenses/gpl-3.0.txt
# Comment: Just another ProxyChecker in Python
#
# Todo: Use OptParse to parse options
#

import urllib.request
import http.client
from os import fork,wait

from sys import exc_info,exit,argv
from socket import timeout

class proxychecker:
	"""Another Proxychecker in Python"""
	def __init__(self,in_file,out_file,testsite,to,process_num,contains=""):
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
		self.process_num	=	process_num
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
		cnt = 0
		for proxy in self.proxys:
			if not fork():
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
	argc	=	len(argv)
	if argc != 7 and argc != 6:
		print("Usage:",argv[0]," <proxy.lst> <output> <testsite> <timeout> <number of process>[ testsite must contains]")
		exit(0)
	if argc == 6:
		p	=	proxychecker(argv[1],argv[2],argv[3],float(argv[4]),int(argv[5]))
	elif argc == 7:
		p	=	proxychecker(argv[1],argv[2],argv[3],float(argv[4]),int(argv[5]),argv[6])
	exit(0)
