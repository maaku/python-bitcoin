#
# Copyright © 2012-2013 by its contributors. See AUTHORS for details.
#
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
#

ROOT=$(shell pwd)
CACHE_ROOT=${ROOT}/.cache
PYENV=${ROOT}/.pyenv
APP_NAME=python-bitcoin
PACKAGE=bitcoin

-include Makefile.local

.PHONY: all
all: ${PYENV}/.stamp-h

.PHONY: check
check: all
	mkdir -p build/report/xunit
	@echo  >.pytest.py "import unittest2"
	@echo >>.pytest.py "import xmlrunner"
	@echo >>.pytest.py "unittest2.main("
	@echo >>.pytest.py "    testRunner=xmlrunner.XMLTestRunner("
	@echo >>.pytest.py "        output='build/report/xunit'),"
	@echo >>.pytest.py "    argv=['unit2', 'discover',"
	@echo >>.pytest.py "        '-s','xunit',"
	@echo >>.pytest.py "        '-p','*.py',"
	@echo >>.pytest.py "        '-t','.',"
	@echo >>.pytest.py "    ]"
	@echo >>.pytest.py ")"
	chmod +x .pytest.py
	"${PYENV}"/bin/coverage run .pytest.py || { rm -f .pytest.py; exit 1; }
	"${PYENV}"/bin/coverage xml --omit=".pytest.py" -o build/report/coverage.xml
	rm -f .pytest.py

.PHONY: debugcheck
debugcheck: all
	mkdir -p build/report/xunit
	@echo  >.pytest.py "import unittest2"
	@echo >>.pytest.py "import xmlrunner"
	@echo >>.pytest.py "import exceptions, ipdb, sys"
	@echo >>.pytest.py "class PDBAssertionError(exceptions.AssertionError):"
	@echo >>.pytest.py "    def __init__(self, *args):"
	@echo >>.pytest.py "        exceptions.AssertionError.__init__(self, *args)"
	@echo >>.pytest.py "        print 'Assertion failed, entering PDB...'"
	@echo >>.pytest.py "        if hasattr(sys, '_getframe'):"
	@echo >>.pytest.py "            ipdb.set_trace(sys._getframe().f_back.f_back.f_back)"
	@echo >>.pytest.py "        else:"
	@echo >>.pytest.py "            ipdb.set_trace()"
	@echo >>.pytest.py "unittest2.TestCase.failureException = PDBAssertionError"
	@echo >>.pytest.py "unittest2.main("
	@echo >>.pytest.py "    testRunner=xmlrunner.XMLTestRunner("
	@echo >>.pytest.py "        output='build/report/xunit'),"
	@echo >>.pytest.py "    argv=['unit2', 'discover',"
	@echo >>.pytest.py "        '-s','xunit',"
	@echo >>.pytest.py "        '-p','*.py',"
	@echo >>.pytest.py "        '-t','.',"
	@echo >>.pytest.py "    ]"
	@echo >>.pytest.py ")"
	@chmod +x .pytest.py
	"${PYENV}"/bin/coverage run .pytest.py || { rm -f .pytest.py; exit 1; }
	"${PYENV}"/bin/coverage xml --omit=".pytest.py" -o build/report/coverage.xml
	rm -f .pytest.py

.PHONY: shell
shell: all
	"${PYENV}"/bin/ipython

.PHONY: mostlyclean
mostlyclean:
	-rm -rf dist
	-rm -rf build
	-rm -rf .coverage

.PHONY: clean
clean: mostlyclean
	-rm -rf "${PYENV}"

.PHONY: distclean
distclean: clean
	-rm -rf "${CACHE_ROOT}"
	-rm -rf Makefile.local

.PHONY: maintainer-clean
maintainer-clean: distclean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

# ===--------------------------------------------------------------------===

.PHONY: dist
dist:
	"${PYENV}"/bin/python setup.py sdist

# ===--------------------------------------------------------------------===

${CACHE_ROOT}/virtualenv/virtualenv-1.9.1.tar.gz:
	mkdir -p "${CACHE_ROOT}"/virtualenv
	sh -c "cd '${CACHE_ROOT}'/virtualenv && curl -O 'http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.1.tar.gz'"

${PYENV}/.stamp-h: requirements*.pip ${CACHE_ROOT}/virtualenv/virtualenv-1.9.1.tar.gz
	# Because build and run-time dependencies are not thoroughly tracked,
	# it is entirely possible that rebuilding the development environment
	# on top of an existing one could result in a broken build. For the
	# sake of consistency and preventing unnecessary, difficult-to-debug
	# problems, the entire development environment is rebuilt from scratch
	# everytime this make target is selected.
	${MAKE} clean
	
	# The ${PYENV} directory, if it exists, was removed above. The
	# PyPI cache is nonexistant if this is a freshly checked-out
	# repository, or if the `distclean` target has been run.  This
	# might cause problems with build scripts executed later which
	# assume their existence, so they are created now if they don't
	# already exist.
	mkdir -p "${PYENV}"
	mkdir -p "${CACHE_ROOT}"/pypi
	
	# `virtualenv` is used to create a separate Python installation for
	# this project in `${PYENV}`.
	tar \
	    -C "${CACHE_ROOT}"/virtualenv --gzip \
	    -xf "${CACHE_ROOT}"/virtualenv/virtualenv-1.9.1.tar.gz
	python "${CACHE_ROOT}"/virtualenv/virtualenv-1.9.1/virtualenv.py \
	    --clear \
	    --distribute \
	    --never-download \
	    --prompt="(${APP_NAME}) " \
	    "${PYENV}"
	-rm -rf "${CACHE_ROOT}"/virtualenv/virtualenv-1.9.1
	
	# M2Crypto is installed by easy_install so that we can fetch a binary
	# install, which might have configuration options to perform better on
	# a wider variety of targets.
	"${PYENV}"/bin/easy_install M2Crypto
	
	# readline is installed here to get around a bug on Mac OS X
	# which is causing readline to not build properly if installed
	# from pip, and the fact that a different package must be used
	# to support it on Windows/Cygwin.
	if [ "x`uname -o`" == "xCygwin" ]; then \
	    "${PYENV}"/bin/pip install pyreadline; \
	else \
	    "${PYENV}"/bin/easy_install readline; \
	fi
	
	# pip is used to install Python dependencies for this project.
	CFLAGS=-I/opt/local/include LDFLAGS=-L/opt/local/lib \
	"${PYENV}"/bin/python "${PYENV}"/bin/pip install \
	    --download-cache="${CACHE_ROOT}"/pypi \
	    -r "${ROOT}"/requirements.pip; \
	for reqfile in "${ROOT}"/requirements-*.pip; do \
	    CFLAGS=-I/opt/local/include LDFLAGS=-L/opt/local/lib \
	    "${PYENV}"/bin/python "${PYENV}"/bin/pip install \
	        --download-cache="${CACHE_ROOT}"/pypi \
	        -r "$$reqfile"; \
	done
	
	# All done!
	touch "${PYENV}"/.stamp-h

#
# End of File
#
