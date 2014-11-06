# Copyright © 2012-2014 by its contributors. See AUTHORS for details.
# Distributed under the MIT/X11 software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

ROOT=$(shell pwd)
CACHE=${ROOT}/.cache
PYENV=${ROOT}/.pyenv
SYSROOT=${ROOT}/.sysroot
CONF=${ROOT}/conf
APP_NAME=python-bitcoin
PACKAGE=bitcoin

-include Makefile.local

.PHONY: all
all: python-env

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
	-rm -rf .build

.PHONY: clean
clean: mostlyclean
	-rm -rf "${PYENV}"
	-rm -rf "${ROOT}"/python_bitcoin.egg-info
	-rm -rf "${SYSROOT}"

.PHONY: distclean
distclean: clean
	-rm -rf "${CACHE}"
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

${CACHE}/pyenv/virtualenv-1.11.6.tar.gz:
	mkdir -p "${CACHE}"/pyenv
	curl -L 'https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.6.tar.gz' >'$@' || { rm -f '$@'; exit 1; }

${CACHE}/pyenv/pyenv-1.11.6-base.tar.gz: ${CACHE}/pyenv/virtualenv-1.11.6.tar.gz
	-rm -rf "${PYENV}"
	mkdir -p "${PYENV}"

	# virtualenv is used to create a separate Python installation
	# for this project in ${PYENV}.
	tar \
	    -C "${CACHE}"/pyenv --gzip \
	    -xf "${CACHE}"/pyenv/virtualenv-1.11.6.tar.gz
	python "${CACHE}"/pyenv/virtualenv-1.11.6/virtualenv.py \
	    --clear \
	    --never-download \
	    --prompt="(${APP_NAME}) " \
	    "${PYENV}"
	-rm -rf "${CACHE}"/pyenv/virtualenv-1.11.6

	# Snapshot the Python environment
	tar -C "${PYENV}" --gzip -cf "$@" .
	rm -rf "${PYENV}"

${CACHE}/pyenv/pyenv-1.11.6-extras.tar.gz: ${CACHE}/pyenv/pyenv-1.11.6-base.tar.gz ${ROOT}/requirements.txt ${CONF}/requirements*.txt ${SYSROOT}/.stamp-gmp-h ${SYSROOT}/.stamp-mpfr-h ${SYSROOT}/.stamp-mpc-h
	-rm -rf "${PYENV}"
	mkdir -p "${PYENV}"
	mkdir -p "${CACHE}"/pypi

	# Uncompress saved Python environment
	tar -C "${PYENV}" --gzip -xf "${CACHE}"/pyenv/pyenv-1.11.6-base.tar.gz
	find "${PYENV}" -not -type d -print0 >"${ROOT}"/.pkglist

	# Upgrade the version of setuptools we are using, since blist requires
	# a modern copy and the virtualenv setup above doesn't pull from the
	# internet.
	"${PYENV}"/bin/pip install --upgrade setuptools

	# readline is installed here to get around a bug on Mac OS X
	# which is causing readline to not build properly if installed
	# from pip, and the fact that a different package must be used
	# to support it on Windows/Cygwin.
	if [ "x`uname -s`" = "xCygwin" ]; then \
	    "${PYENV}"/bin/pip install pyreadline; \
	else \
	    "${PYENV}"/bin/easy_install readline; \
	fi

	# pip is used to install Python dependencies for this project.
	for reqfile in "${ROOT}"/requirements.txt \
	               "${CONF}"/requirements*.txt; do \
	    CFLAGS="-I'${SYSROOT}'/include" \
	    LDFLAGS="-L'${SYSROOT}'/lib" \
	    "${PYENV}"/bin/python "${PYENV}"/bin/pip install \
	        --download-cache="${CACHE}"/pypi \
	        -r "$$reqfile" || exit 1; \
	done

	# Snapshot the Python environment
	cat "${ROOT}"/.pkglist | xargs -0 rm -rf
	tar -C "${PYENV}" --gzip -cf "$@" .
	rm -rf "${PYENV}" "${ROOT}"/.pkglist

.PHONY:
python-env: ${PYENV}/.stamp-h

${PYENV}/.stamp-h: ${CACHE}/pyenv/pyenv-1.11.6-base.tar.gz ${CACHE}/pyenv/pyenv-1.11.6-extras.tar.gz ${ROOT}/setup.py
	-rm -rf "${PYENV}"
	mkdir -p "${PYENV}"

	# Uncompress saved Python environment
	tar -C "${PYENV}" --gzip -xf "${CACHE}"/pyenv/pyenv-1.11.6-base.tar.gz
	tar -C "${PYENV}" --gzip -xf "${CACHE}"/pyenv/pyenv-1.11.6-extras.tar.gz

	# Install the project package as a Python egg:
	"${PYENV}"/bin/python "${ROOT}"/setup.py develop

	# All done!
	touch "$@"

# ===--------------------------------------------------------------------===

${CACHE}/gmp/gmp-5.1.3.tar.xz:
	mkdir -p ${CACHE}/gmp
	curl -L 'https://ftp.gnu.org/gnu/gmp/gmp-5.1.3.tar.xz' >'$@' || { rm -f '$@'; exit 1; }

${CACHE}/gmp-5.1.3-pkg.tar.gz: ${CACHE}/gmp/gmp-5.1.3.tar.xz
	if [ -d "${SYSROOT}" ]; then \
	    mv "${SYSROOT}" "${SYSROOT}"-bak; \
	fi
	mkdir -p "${SYSROOT}"

	rm -rf "${ROOT}"/.build/gmp
	mkdir -p "${ROOT}"/.build/gmp
	tar -C "${ROOT}"/.build/gmp --strip-components 1 --xz -xf "$<"
	bash -c "cd '${ROOT}'/.build/gmp && ./configure --prefix '${SYSROOT}'"
	bash -c "cd '${ROOT}'/.build/gmp && make all install"
	rm -rf "${ROOT}"/.build/gmp

	# Snapshot the package
	tar -C "${SYSROOT}" --gzip -cf "$@" .
	rm -rf "${SYSROOT}"
	if [ -d "${SYSROOT}"-bak ]; then \
	    mv "${SYSROOT}"-bak "${SYSROOT}"; \
	fi

.PHONY: gmp-pkg
gmp-pkg: ${SYSROOT}/.stamp-gmp-h

${SYSROOT}/.stamp-gmp-h: ${CACHE}/gmp-5.1.3-pkg.tar.gz
	mkdir -p "${SYSROOT}"

	# Uncompress the package snapshots
	tar -C "${SYSROOT}" --gzip -xf "$<"

	# All done!
	touch "$@"

# ===--------------------------------------------------------------------===

${CACHE}/mpfr/mpfr-3.1.2.tar.xz:
	mkdir -p ${CACHE}/mpfr
	curl -L 'http://ftp.gnu.org/gnu/mpfr/mpfr-3.1.2.tar.xz' >'$@' || { rm -f '$@'; exit 1; }

${CACHE}/mpfr-3.1.2-pkg.tar.gz: ${CACHE}/mpfr/mpfr-3.1.2.tar.xz ${CACHE}/gmp-5.1.3-pkg.tar.gz
	if [ -d "${SYSROOT}" ]; then \
	    mv "${SYSROOT}" "${SYSROOT}"-bak; \
	fi
	mkdir -p "${SYSROOT}"
	tar -C "${SYSROOT}" --gzip -xf ${CACHE}/gmp-5.1.3-pkg.tar.gz
	find "${SYSROOT}" -not -type d -print0 >"${ROOT}"/.pkglist

	rm -rf "${ROOT}"/.build/mpfr
	mkdir -p "${ROOT}"/.build/mpfr
	tar -C "${ROOT}"/.build/mpfr --strip-components 1 --xz -xf "$<"
	bash -c "cd '${ROOT}'/.build/mpfr && ./configure \
	    --prefix '${SYSROOT}' \
	    --with-gmp='${SYSROOT}'"
	bash -c "cd '${ROOT}'/.build/mpfr && make all install"
	rm -rf "${ROOT}"/.build/mpfr

	# Snapshot the package
	cat "${ROOT}"/.pkglist | xargs -0 rm -rf
	tar -C "${SYSROOT}" --gzip -cf "$@" .
	rm -rf "${SYSROOT}"
	if [ -d "${SYSROOT}"-bak ]; then \
	    mv "${SYSROOT}"-bak "${SYSROOT}"; \
	fi

.PHONY: mpfr-pkg
mpfr-pkg: ${SYSROOT}/.stamp-mpfr-h

${SYSROOT}/.stamp-mpfr-h: ${CACHE}/mpfr-3.1.2-pkg.tar.gz ${SYSROOT}/.stamp-gmp-h
	# Uncompress the package snapshots
	tar -C "${SYSROOT}" --gzip -xf "$<"

	# All done!
	touch "$@"

# ===--------------------------------------------------------------------===

${CACHE}/mpc/mpc-1.0.1.tar.gz:
	mkdir -p ${CACHE}/mpc
	curl -L 'http://www.multiprecision.org/mpc/download/mpc-1.0.1.tar.gz' >'$@' || { rm -f '$@'; exit 1; }

${CACHE}/mpc-1.0.1-pkg.tar.gz: ${CACHE}/mpc/mpc-1.0.1.tar.gz ${CACHE}/gmp-5.1.3-pkg.tar.gz ${CACHE}/mpfr-3.1.2-pkg.tar.gz
	if [ -d "${SYSROOT}" ]; then \
	    mv "${SYSROOT}" "${SYSROOT}"-bak; \
	fi
	mkdir -p "${SYSROOT}"
	tar -C "${SYSROOT}" --gzip -xf ${CACHE}/gmp-5.1.3-pkg.tar.gz
	tar -C "${SYSROOT}" --gzip -xf ${CACHE}/mpfr-3.1.2-pkg.tar.gz
	find "${SYSROOT}" -not -type d -print0 >"${ROOT}"/.pkglist

	rm -rf "${ROOT}"/.build/mpc
	mkdir -p "${ROOT}"/.build/mpc
	tar -C "${ROOT}"/.build/mpc --strip-components 1 --gzip -xf "$<"
	bash -c "cd '${ROOT}'/.build/mpc && ./configure \
	    --prefix '${SYSROOT}' \
	    --with-gmp='${SYSROOT}' \
	    --with-mpfr='${SYSROOT}'"
	bash -c "cd '${ROOT}'/.build/mpc && make all install"
	rm -rf "${ROOT}"/.build/mpc

	# Snapshot the package
	cat "${ROOT}"/.pkglist | xargs -0 rm -rf
	tar -C "${SYSROOT}" --gzip -cf "$@" .
	rm -rf "${SYSROOT}"
	if [ -d "${SYSROOT}"-bak ]; then \
	    mv "${SYSROOT}"-bak "${SYSROOT}"; \
	fi

.PHONY: mpc-pkg
mpc-pkg: ${SYSROOT}/.stamp-mpc-h

${SYSROOT}/.stamp-mpc-h: ${CACHE}/mpc-1.0.1-pkg.tar.gz ${SYSROOT}/.stamp-gmp-h ${SYSROOT}/.stamp-mpfr-h
	# Uncompress the package snapshots
	tar -C "${SYSROOT}" --gzip -xf "$<"

	# All done!
	touch "$@"
