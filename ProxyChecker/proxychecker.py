#!/usr/bin/python3
#
#    proxychecker.py is a multithreaded hitfaker and proxychecker
#
#    Copyright (C) 2014 by Jan Helbling <jan.helbling@gmail.com>
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

import gzip,sys,re,gettext

from http.client import IncompleteRead,BadStatusLine
from os import path
from platform import system

from gettext import gettext as _

if path.exists("/usr/share/locale"):
	gettext.bindtextdomain('proxychecker', '/usr/share/locale')
	gettext.textdomain('proxychecker')

if system() == "Windows":
	sys.stderr.write(_(" [ERROR] fork could not be imported from os, this programm is not for Windows-Users!!\n"))
	sys.stderr.write(_("        (Windows has no syscall named fork()...\n"))
	sys.stderr.write(_("        You must Upgrade to Linux to use this ;)\n"))
	sys.exit(1)

if sys.platform in ["unixware7"]:
	from os import fork1 as fork
else:
	from os import fork

from os import waitpid,unlink,devnull,WEXITSTATUS

from socket import timeout
from random import randint
from time import time

RED		= "\x1b\x5b\x33\x31\x6d"
REDBOLD		= "\x1b\x5b\x31\x3b\x33\x31\x6d"
GREEN		= "\x1b\x5b\x33\x32\x6d"
GREENBOLD	= "\x1b\x5b\x31\x3b\x33\x32\x6d"
YELLOW		= "\x1b\x5b\x30\x3b\x33\x33\x6d"
NOCOLOR		= "\x1b\x5b\x30\x6d"

proxyregex	= re.compile("\d+\.\d+\.\d+\.\d+:\d+")

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

useragent_all	= useragent + useragent_mobile

class proxychecker:
	"""A advanced Proxychecker/Hitfaker in Python"""
	def __init__(self,in_file,out_file,testsite,to,process_num,contains,referer,browserstring,postdata,cookie,color,header):
		"""Run's the program"""
		global RED,REDBOLD,GREEN,GREENBOLD,YELLOW,NOCOLOR
		if header != "":
			if header.count(":") != 1:
				stderr.write(_("{0}[ERROR] --header should exactly contains one \":\" !!!{1}").format(RED,NOCOLOR))
				exit(1)
			self.header		=	(header.split(":")[0],header.split(":")[1])
		else:
			self.header		=	("","")
		self.color		=	color.lower()
		self.cookie             =       cookie
		self.postdata           =       postdata.encode("utf-8","ignore")
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
		if self.color == "none":
			RED 		= ""
			REDBOLD		= ""
			GREEN 		= ""
			GREENBOLD	= ""
			YELLOW		= ""
			NOCOLOR		= ""
		try:
			# Open (and read) the proxylist to be checked and the outputfile
			if in_file not in ["-","/dev/stdin"] and not in_file.startswith("http://"):
				if in_file.lower().endswith(".gz"):
					self.in_file	=	gzip.open(in_file,"rb")
				else:
					self.in_file	=	open(in_file,"rb")
				self.proxys	=	self.in_file.readlines()
				self.in_file.close()
			elif in_file.startswith("http://"):
				print(_("{0}[INFO] gather proxys from url...").format(YELLOW),end="")
				self.fd		=	urllib.request.urlopen(in_file)
				self.content	=	(self.fd.read()).decode("utf-8","ignore")
				self.fd.close()
				self.proxys	=	proxyregex.findall(self.content)
				print(_("...{0}[DONE, {1} proxys found]{2}").format(GREEN,len(self.proxys),NOCOLOR))
			else:
				self.proxys	=	sys.stdin.readlines()
			if out_file not in [devnull,"/dev/stdout","/dev/stderr","/dev/stdin"]:
				self.__check_for_old_files(out_file) 	# check if the out_file already exists
			if out_file in ["/dev/stdout","-"]:
				self.out_file	=	open("/dev/stdout","w")
				self.devnull	=	open(devnull,"w")
				sys.stdout	=	self.devnull
				sys.stdin	=	self.out_file
			else:
				self.out_file	=	open(out_file,"w")
		except urllib.error.URLError as e:
			print(_("...{0}[FAIL]{1}").format(RED,NOCOLOR))
			if type(e.args[0]) == str:
				sys.stderr.write(_("{0} [ERROR] couldn\'t open {1}: {2}{3}\n").format(RED,in_file,e.args[0],NOCOLOR))
			else:
				sys.stderr.write(_("{0} [ERROR] couldn\'t open {1}:  {2}{3}\n").format(RED,in_file,e.args[0].strerror,NOCOLOR))
			sys.exit(1)
		except IOError as e:
			if type(e.args[0]) == str:
				sys.stderr.write(_("{0} [ERROR] {1}").format(RED,e.args[0]))
			else:
				sys.stderr.write(_("{0} [ERROR] {1}: {2}\n").format(RED,e.filename,e.strerror))
			sys.exit(1)
		print(_("{0}[INFO] Remove invalid lines from list...").format(YELLOW),end="")
		self.__remove_empty_lines()
		print(_("{0}..[DONE, {1} lines removed]{2}").format(GREEN,self.invalid_line_counter,NOCOLOR))
		
		self.totalproxys	=	len(self.proxys)
		print(_("{0}[TOTAL: {1} Proxys]{2}").format(YELLOW,self.totalproxys,NOCOLOR))
		
		if self.totalproxys == 0:
			sys.stderr.write(_("{0} [ERROR] no proxys found...{1}\n").format(RED,NOCOLOR))
			if out_file == devnull:
				exit(1)
			sys.stderr.write(_("{0} [Remove outputfile]...").format(YELLOW))
			try:
				unlink(out_file)
				sys.stderr.write(_("...{0}[DONE]{1}\n").format(GREEN,NOCOLOR))
			except IOError as e:
				sys.stderr.write(_("...{0}[FAIL]{1}\n").format(RED,NOCOLOR))
				sys.stderr.write(_("{0} [ERROR] While removing {1}: {2}{3}\n").format(RED,e.filename,e.strerror,NOCOLOR))
			sys.exit(1)
		
		print(_("{0}[INFO] ({1}working{0})=(current/total){2}").format(YELLOW,GREEN,NOCOLOR))
		
		# Calling the Main-Function
		self.__main()
	
	def __remove_empty_lines(self):
		"""Remove empty/invalid nonproxys from the list."""
		self.invalid_line_counter	=	len(self.proxys)
		self._proxys			=	[]
		for proxy in self.proxys:
			if type(proxy) != str:
				proxy	=	proxy.decode("utf-8","ignore")
			proxy		=	proxyregex.findall(proxy)
			if proxy != []:
				self._proxys.append(proxy[0])
		self.proxys			=	self._proxys
		self._proxys			=	[]	
		self.invalid_line_counter	=	self.invalid_line_counter - len(self.proxys)
	
	def __check_for_old_files(self,out_file):
		"""Checks if the path "out_file" exists, if true, then compress it to a gzipped archive with the next number."""
		if path.exists(out_file):
				self.i  =       0
				while True:
					self.filename   =       out_file+"."+str(self.i)+".gz"
					if not path.exists(self.filename):
						print(_("{0}[INFO] Compressing {1} in {2} => ").format(YELLOW,out_file,self.filename),end="")
						try:
							self.gzfd       =       gzip.open(self.filename,"wb",9)
							self.fd         =       open(out_file,"rb")
							self.gzfd.write(self.fd.read())
							self.gzfd.close()
							self.fd.close()
							unlink(out_file)
							print(_("{0}[DONE]{1}").format(GREEN,NOCOLOR))
							break
						except IOError as e:
							print(_("{0}[FAIL]{1}").format(RED,NOCOLOR))
							sys.stderr.write(_("{0} [ERROR] with file {1}: {2}{3}\n").format(RED,e.filename,e.strerror,NOCOLOR))
							sys.exit(1)
					self.i          =       self.i + 1
	
	def __check_proxy(self,proxy):
		"""Checks a proxy and save it to file, if the string "contains" is in content, returns true if Success,false on fail"""
		proxyhdl	=	urllib.request.ProxyHandler({'http':proxy})
		opener		=	urllib.request.build_opener(proxyhdl) # Build a opener with the proxy
		if self.browserstring == "desktop": #check if browserstring is desktop,mobile or all, add the Cookie if set
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent[randint(0,len(useragent)-1)]),('Cookie',self.cookie),(self.header[0],self.header[1])] #Add User-Agent (and Headers/Cookies if set)
		elif self.browserstring == "mobile":
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent_mobile[randint(0,len(useragent_mobile)-1)]),('Cookie',self.cookie),(self.header[0],self.header[1])]
		else:
			opener.addheaders	=	[('Referer',self.referer),('User-Agent',useragent_all[randint(0,len(useragent_all)-1)]),('Cookie',self.cookie),(self.header[0],self.header[1])]
		try:
			starttime	=	time()
			fd		=	opener.open(self.testsite,timeout=self.to,data=self.postdata) # Open the website, with timeout to and postdata
			content		=	fd.read()
			endtime		=	time()
			contenttype	=	fd.getheader("Content-Type")
			content		=	content.decode("utf-8","ignore")
			fd.close()
			endtime		=	(endtime-starttime).__round__(3)
			if self.contains in content: #Check if the string contains is in content, if true
				print(_("{0}[OK]  \t=>{1}({0}{2}{1})=({3}/{4})          {0}{5}\t-->{6}sec.{7}").format(GREEN,YELLOW,self.cnt+1,self.totalcnt,self.totalproxys,proxy,endtime,NOCOLOR))
				self.__save_proxy(proxy)	# write proxy to file
				return True
			else:				# else, fail
				if (contenttype == "text/plain" or contenttype == "text/html") and len(content) < 30:
					print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->Doesnt contain the String: {7}{8}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,content,NOCOLOR))
				else:
					print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->Doesnt contain the String!{7}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,NOCOLOR))
		except IOError as e:
			if e.strerror != None:
				print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->{7}{8}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,e.strerror,NOCOLOR))
			else:
				try:
					if type(e.reason) == str:
						print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->{7}{8}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,e.reason,NOCOLOR))
					elif e.reason.args[0] == "timed out":
						print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->Timed Out{7}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,NOCOLOR))
					else:
						print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->{7}{8}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,e.reason.strerror,NOCOLOR))
				except AttributeError:
						print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->Timed Out{7}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,NOCOLOR))
				except TypeError:
						print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->Timed Out{7}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,NOCOLOR))
		except BadStatusLine:
			print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->BadStatusLine{7}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,NOCOLOR))
		except IncompleteRead:
			print(_("{0}[FAIL]\t=>{1}({2}{3}{1})=({4}/{5})          {0}{6}\t-->IncompleteRead{7}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,NOCOLOR))
		except KeyboardInterrupt:	# [CTRL] + [C]
			print(_("{0}[ABORTED CTRL+C]     =>{1}({2}{3}{1})=({4}/{5}) {0}{6}\t-->Interrupted by User{7}").format(RED,YELLOW,GREEN,self.cnt,self.totalcnt,self.totalproxys,proxy,NOCOLOR))
		return False
	
	def __save_proxy(self,proxy):
		"""Save the proxy to file."""
		self.out_file.write(proxy+"\n")
		self.out_file.flush()
	
	def __main(self):
		"""Main, the main-programm"""
		cnt = 0
		pids = []
		for proxy in self.proxys:
			self.totalcnt	=	self.totalcnt + 1
			pids.append(fork()) # man fork
			if not pids[-1]:
				if self.__check_proxy(proxy):
					sys.exit(0)
				sys.exit(1)
			if len(pids) == self.process_num:
				for pid in pids:
					try:
						(_pid,st)	=	waitpid(pid,0)	# man/pydoc3 (os.) waitpid
						if WEXITSTATUS(st) == 0:
							self.cnt=	self.cnt + 1
					except KeyboardInterrupt:
						sys.exit(1)
				pids = []
		for pid in pids:
			try:
				(_pid,st)	=	waitpid(pid,0) 	# get the exit_code from the forked subproccess
				if WEXITSTATUS(st) == 0:		# if it's 0, __check_proxy has returned true
					self.cnt=       self.cnt + 1 	# incerase the counter
			except KeyboardInterrupt:
				sys.exit(1)
		self.out_file.close()
		if self.cnt == 0:
			print(_("{0}[!!!EPIC FAIL!!!] None of {1} proxys we have checked are working...\nremoving the output-file...{2}").format(REDBOLD,self.totalproxys,NOCOLOR),end="")
			try:
				unlink(self.out_file.name)
				print(_("{0}...{1}[OK]{2}").format(REDBOLD,GREEN,NOCOLOR))
			except IOError as e:
				print(_("{0}...[FAIL]{1}").format(RED,NOCOLOR))
				sys.stderr.write(_(" [ERROR] Couldn\'t remove {0}: {1}\n").format(e.filename,e.strerror))
				sys.exit(1)
		else:
			print(_("{0}[!!!DONE!!!] {1} of {2} proxys we have checked are working!{3}").format(GREENBOLD,self.cnt,self.totalproxys,NOCOLOR))
			print(_("{0}[New Proxylist saved to => {1}]{2}").format(GREEN,self.out_file.name,NOCOLOR))
		sys.exit(0)
