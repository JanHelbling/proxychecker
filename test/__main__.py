#!/usr/bin/python3

import os

if __name__ == "__main__":
	os.execvp("bin/proxychecker",["bin/proxychecker","-i","data/proxys.lst","-o","/dev/null"])

