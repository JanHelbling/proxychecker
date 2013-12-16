proxychecker:
	@echo ======================================
	@echo ProxyChecker, \(C\) 2013 by Jan Helbling
	@echo ==============GNU/GPLv3+==============
	@echo Nothing todo...
	@echo Possible options:
	@echo "   make test"
	@echo "   make install"
	@echo "   make uninstall"
install:
	install proxychecker.py /usr/bin/proxychecker
uninstall:
	rm -f /usr/bin/proxychecker
test:
	./proxychecker.py -i proxylist.txt -t 3
