#!/usr/bin/python3

from os import execvp,waitpid,WEXITSTATUS
from sys import stderr,exit

if sys.platform in ["unixware7"]:
        from os import fork1 as fork
else:
        from os import fork

if __name__ == "__main__":
	pid	=	0
	try:
		pid	=	fork()
		if not pid:
			print("./bin/proxychecker.py -i data/proxys.lst -o /dev/null -p 10 -t 2")
			execvp("bin/proxychecker",["bin/proxychecker","-i","data/proxys.lst","-o","/dev/null","-p","16","-t","2"])
	except KeyboardInterrupt as e:
		stderr.write("[CTRL+C , KeyboardInterrupt!]")
		exit(1)
	except OSError as e:
		stderr.write(e.filename+": "+e.strerror)
		exit(1)
	pid,st	= waitpid(pid,0)
	st	= WEXITSTATUS(st)
	exit(st)
