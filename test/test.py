#!/usr/bin/python3
#
#    test.py, part of proxychecker (module to run the test)
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

from gettext import gettext as _
from os import execvp
from sys import stderr,exit

import gettext

if path.exists("/usr/share/locale"):
	gettext.bindtextdomain('proxychecker_test', '/usr/share/locale')
	gettext.textdomain('proxychecker_test')

class test:
	def __init__(self):
		print("./bin/proxychecker.py -i data/proxys.lst -o /dev/null -p 15 -t 2")
		self.__run()
	def __run(self):
		try:
			execvp("bin/proxychecker",["bin/proxychecker","-i","data/proxys.lst","-o","/dev/null","-p","16","-t","2"])
		except KeyboardInterrupt as e:
			stderr.write(_("[CTRL+C, KeyboardInterrupt!]\n"))
			exit(1)
		except OSError as e:
			stderr.write(e.filename+": "+e.strerror+"\n")
			exit(1)
		exit(0)
