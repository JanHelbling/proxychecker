#!/usr/bin/python3

from os import execvp
from sys import stderr,exit

if __name__ == "__main__":
	print("./bin/proxychecker.py -i data/proxys.lst -o /dev/null -p 10 -t 2")
	try:
		execvp("bin/proxychecker",["bin/proxychecker","-i","data/proxys.lst","-o","/dev/null","-p","16","-t","2"])
	except KeyboardInterrupt as e:
		stderr.write("[CTRL+C , KeyboardInterrupt!]\n")
		exit(1)
	except OSError as e:
		stderr.write(e.filename+": "+e.strerror+"\n")
		exit(1)
	exit(0)
