install:
	install proxychecker.py /usr/bin/proxychecker
test:
	./proxychecker.py -i proxylist.txt -t 3
