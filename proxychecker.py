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
import gzip,csv
from http.client import IncompleteRead,BadStatusLine
from sys import exit,argv,stderr

try:
	from os import fork,waitpid,path,unlink,devnull,WEXITSTATUS
except ImportError as e:
	if e.msg == "cannot import name fork":
		stderr.write("[ERROR] fork could not be imported from os, this programm is not for Windows-Users!!\n")
		stderr.write("        (Windows has no syscall named fork()...)\n")
		stderr.write("        You must Upgrade to Linux to use this ;)\n")
		exit(1)

from optparse import OptionParser
from socket import timeout
from random import randint
from time import time

RED		= "\x1b\x5b\x33\x31\x6d"
REDBOLD		= "\x1b\x5b\x31\x3b\x33\x31\x6d"
GREEN		= "\x1b\x5b\x33\x32\x6d"
GREENBOLD	= "\x1b\x5b\x31\x3b\x33\x32\x6d"
YELLOW		= "\x1b\x5b\x30\x3b\x33\x33\x6d"
NOCOLOR		= "\x1b\x5b\x30\x6d"

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
	"Mozilla/5.0 (BlackBerry; U; BlackBerry 9900; en) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.1.0.346 Mobile Safari/534.11+",
	"Opera/12.02 (Android 4.1; Linux; Opera Mobi/ADR-1111101157; U; en-US) Presto/2.9.201 Version/12.02"]

useragent_both	= useragent + useragent_mobile

class proxychecker:
	"""A advanced Proxychecker/Hitfaker in Python"""
	def __init__(self,in_file,out_file,testsite,to,process_num,contains,referer,browserstring,postdata,cookie,color,fmt):
		"""Run's the program"""
		global RED,REDBOLD,GREEN,GREENBOLD,YELLOW,NOCOLOR
		self.fmt		=	fmt.lower()
		self.color		=	color.lower()
		self.cookie             =       cookie
		self.postdata           =       postdata.encode("utf-8")
		self.browserstring      =       browserstring.lower()
		self.referer            =       referer
		self.to                 =       to
		self.testsite           =       testsite
		if not self.testsite.lower().startswith("http://"):		# check if testsite starts with http://, if not
			self.testsite   =       "http://" + self.testsite	# add http:// before the testsite
		self.contains           =       contains
		self.process_num        =       process_num
		self.cnt                =       0
		self.totalcnt		=	0
		if self.browserstring not in ["mobile","desktop","both"]:
                        stderr.write("[ERROR] Invalid Browserstring, use \"mobile\",\"desktop\" or \"both\"!\n")
                        exit(1)
		if self.color not in ["yes","none"]:
			stderr.write("[ERROR] Invalid value for color, use \"yes\" or \"none\"!\n")
			exit(1)
		if self.fmt not in ["csv","txt","gz"]:
			stderr.write("[ERROR] Invalid Fileformat, use \"txt\", \"csv\" or \"gz\"!\n")
			exit(1)
		if self.color == "none":
			RED 		= ""
			REDBOLD		= ""
			GREEN 		= ""
			GREENBOLD	= ""
			YELLOW		= ""
			NOCOLOR		= ""
		try:
			# Open (and read) the proxylist to be checked and the outputfile
			if in_file.lower().endswith(".gz"):
				self.in_file	=	gzip.open(in_file,"rb")
			else:
				self.in_file	=	open(in_file,"rb")
			self.proxys	=	self.in_file.readlines()
			self.in_file.close()
			if out_file != devnull:
				if self.fmt == "gz" and not out_file.lower().endswith(".gz"):
					out_file = out_file + ".gz"
				elif self.fmt == "csv" and not out_file.lower().endswith(".csv"):
					out_file = out_file + ".csv"
				self.__check_for_old_files(out_file) 	# check if the out_file already exists
			if self.fmt == "gz":
				self.out_file	=	gzip.open(out_file,"wb")
			elif self.fmt == "txt":
				if self.fmt == "txt":
					self.out_file	=	open(out_file,"w")
			elif self.fmt == "csv":
				if self.fmt == "csv":
					self.out_file	=	open(out_file,"w")
					self.csv_writer	=	csv.writer(self.out_file)
		except IOError as e:
			stderr.write("[ERROR] Could not open "+e.filename+": "+e.strerror+"\n")
			exit(1)
		print(YELLOW,"[INFO] Remove empty lines from list...",end="")
		self.__remove_empty_lines()
		print("..."+GREEN+"["+str(self.invalid_line_counter),"lines removed]",NOCOLOR)
		
		self.totalproxys	=	len(self.proxys)
		print(YELLOW,"[TOTAL:",self.totalproxys,"Proxys]")
		
		print(YELLOW,"[INFO] ("+GREEN+"working"+YELLOW+")=(current/total)",NOCOLOR)
		# Calling the Main-Function
		self.main()
	
	def __remove_empty_lines(self):
		"""Remove empty lines from a list, eg. b"\n"."""
		self.invalid_line_counter	=	len(self.proxys)
		try:
			self.proxys.remove(b"\n")
		except ValueError as e:
			pass
		try:
			self.proxys.remove(b" \n")
		except ValueError as e:
			pass
		try:
			self.proxys.remove(b"  \n")
		except ValueError as e:
			pass
		try:
			self.proxys.remove(b"\r\n")
		except ValueError as e:
			pass
		try:
			self.proxys.remove(b" \r\n")
		except ValueError as e:
			pass
		try:
			self.proxys.remove(b"  \r\n")
		except ValueError as e:
			pass
		self.invalid_line_counter	=	self.invalid_line_counter - len(self.proxys)
	
	def __check_for_old_files(self,out_file):
		"""Checks if the path "out_file" exists, if true, then compress it to a gzipped archive with the next number."""
		if path.exists(out_file):
				if self.fmt == "gz":
					self.filename.rstrip(".gz")
				self.i  =       0
				while True:
					self.filename   =       out_file+"."+str(self.i)+".gz"
					if not path.exists(self.filename):
						print(YELLOW,"[INFO] Compressing ",out_file,"in",self.filename+" => ",end="")
						try:
							self.gzfd       =       gzip.open(self.filename,"wb",9)
							self.fd         =       open(out_file,"rb")
							self.gzfd.write(self.fd.read())
							self.gzfd.close()
							self.fd.close()
							unlink(out_file)
							print(GREEN,"[DONE]",NOCOLOR)
							break
						except IOError as e:
							print(RED,"[FAIL]",NOCOLOR)
							stderr.write("[ERROR] with file "+e.filename+": "+e.strerror+"\n")
							exit(1)
					self.i          =       self.i + 1
	
	def check_proxy(self,proxy):
		"""Checks a proxy and save it to file, if the string "contains" is in content, returns true if Success,false on fail"""
		proxy		=	proxy.decode("utf-8","ignore").rstrip("\r\n ") # decode it and remove \r\n from the line
		proxyhdl	=	urllib.request.ProxyHandler({'http':proxy})
		opener		=	urllib.request.build_opener(proxyhdl) # Build a opener with the proxy
		if self.browserstring == "desktop": #check if browserstring is desktop,mobile or both, add the Cookie if set
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent[randint(0,len(useragent)-1)]),('Cookie',self.cookie)] #Add User-Agent (and Cookies if set)
		elif self.browserstring == "mobile":
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent_mobile[randint(0,len(useragent_mobile)-1)]),('Cookie',self.cookie)]
		else:
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent_both[randint(0,len(useragent_both)-1)]),('Cookie',self.cookie)]
		try:
			starttime	=	time()
			fd	=	opener.open(self.testsite,timeout=self.to,data=self.postdata) # Open the website, with timeout to and postdata
			content	=	fd.read()
			endtime	=	time()
			content	=	content.decode("utf-8","ignore")
			fd.close()
			endtime	=	(endtime-starttime).__round__(3)
			if self.contains in content: #Check if the string contains is in content, if true
				print(GREEN,"[OK]\t=>",YELLOW+"("+GREEN+str(self.cnt+1)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+GREEN,proxy,"\t-->",endtime,"sec.",NOCOLOR)
				self.save_proxy(proxy,endtime)	# write proxy to file
				return True
			else:				# else, fail
				print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t--> String not matched",NOCOLOR)
		except IOError as e:
			if e.strerror != None:
				print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t-->",e.strerror,NOCOLOR)
			else:
				try:
					if type(e.reason) == str:
						print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t-->",e.reason,NOCOLOR)
					elif e.reason.args[0] == "timed out":
						print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t--> Timed Out",NOCOLOR)
					else:
						print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t-->",e.reason.strerror,NOCOLOR)
				except AttributeError:
					print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t--> Timed Out",NOCOLOR)
		except BadStatusLine as e:
			print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t--> BadStatusLine",NOCOLOR)
		except IncompleteRead as e:
			print(RED,"[FAIL]\t=>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy,"\t--> IncompleteRead",NOCOLOR)
		except KeyboardInterrupt:	# [CTRL] + [C]
			print(RED,"[ABORTED CTRL+C] =>",YELLOW+"("+GREEN+str(self.cnt)+YELLOW+")=("+str(self.totalcnt)+"/"+str(self.totalproxys)+")"+RED,proxy, "\t--> Interrupted by User",NOCOLOR)
		return False
	
	def save_proxy(self,proxy,time):
		"""Save the proxy to file."""
		if self.fmt == "txt":
			self.out_file.write(proxy+"\n")
			self.out_file.flush()
		elif self.fmt == "gz":
			self.out_file.write((proxy+"\n").encode("utf-8","ignore"))
			self.out_file.flush()
		elif self.fmt == "csv":
			ip,port	=	proxy.split(":")
			self.csv_writer.writerow((ip,port,time))
	
	def main(self):
		"""Main, the main-programm"""
		cnt = 0
		pid = []
		for proxy in self.proxys:
			self.totalcnt	=	self.totalcnt + 1
			pid.append(fork()) # man fork
			if not pid[-1]:
				if self.check_proxy(proxy):
					exit(0)
				exit(1)
			if len(pid) == self.process_num:
				for i in pid:
					try:
						(_pid,st)	=	waitpid(i,0)	# man/pydoc3 (os.) waitpid
						if WEXITSTATUS(st) == 0:
							self.cnt=	self.cnt + 1
					except KeyboardInterrupt:
						exit(1)
				pid = []
		for i in pid:
			try:
				(_pid,st)	=	waitpid(i,0) 	# get the exit_code from the forked subproccess
				if WEXITSTATUS(st) == 0:		# if it's 0, check_proxy has returned true
					self.cnt=       self.cnt + 1 	# incerase the counter
			except KeyboardInterrupt:
				exit(1)
		self.out_file.close()
		if self.cnt == 0:
			print(REDBOLD,"[!!!EPIC FAIL!!!] None of",self.totalproxys," proxys we checked are working... removing the output-file...",NOCOLOR,end="")
			try:
				unlink(self.out_file.name)
				print(GREEN+"[OK]",NOCOLOR)
			except IOError as e:
				print(RED+"[FAIL]",NOCOLOR)
		else:
			print(GREENBOLD,"[!!!DONE!!!]",self.cnt,"of",self.totalproxys," proxys we checked are working!",NOCOLOR)
			print(GREEN,"[New Proxylist saved =>",self.out_file.name+"]",NOCOLOR)
		exit(0)

if __name__ == "__main__":
	if len(argv) < 2 or ("-i" not in argv and "--input" not in argv and "-h" not in argv and "--help" not in argv):
		print("Invalid number of arguments! Use -h for options.")
		exit(0)
	# Parse options and run the proxychecker
	parser = OptionParser()
	parser.add_option("-i", "--input", dest="input",help="read proxys from file (gz format supported)", metavar="FILE")
	parser.add_option("-o", "--output", dest="output",help="write proxys to file, default: checked_proxys", metavar="FILE",default="checked_proxys")
	parser.add_option("-u", "--testsite", dest="testsite",help="use this site for requests, default http://www.gnu.org", metavar="WEBSITE",default="http://www.gnu.org")
	parser.add_option("-c", "--contains", dest="contains",help="good hit must contains, default GNU", metavar="STRING",default="GNU")
	parser.add_option("-t", "--timeout", dest="to",help="timeout, default 5.0", metavar="TIMEOUT",type="float",default=5.0)
	parser.add_option("-p", "--process", dest="numproc",help="number of processes, default 10", type="int",metavar="NUM",default=10)
	parser.add_option("-r", "--referer", dest="referer",help="use this site as referer, default None",metavar="REFERER",default="")
	parser.add_option("-b", "--browser-string", dest="browserstring", help="mobile,desktop or both, default desktop", metavar="TYPE",default="desktop")
	parser.add_option("-P", "--post-data", dest="postdata", help="data for postrequests, (eg. foo=bar\&info=false), default None",metavar="DATA",default="")
	parser.add_option("-C", "--cookie", dest="cookie", help="cookies, seperated by ; (eg. \"abc=123; def=456;\"), default None",metavar="COOKIE",default="")
	parser.add_option("-e", "--color", dest="color", help="colored output, none or yes, default yes",metavar="COLOR",default="yes")
	parser.add_option("-x", "--export-format",dest="format",help="write proxys in format: csv,txt or gz, default txt",metavar="format",default="txt")
	(options, args) = parser.parse_args()
	p = proxychecker(options.input,options.output,options.testsite,options.to,options.numproc,options.contains,options.referer,options.browserstring,options.postdata,options.cookie,options.color,options.format)
