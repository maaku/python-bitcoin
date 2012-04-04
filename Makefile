# === makefile ------------------------------------------------------------===
# Copyright © 2011-2012, RokuSigma Inc. and contributors. See AUTHORS for more
# details.
#
# Some rights reserved.
#
# Redistribution and use in source and binary forms of the software as well as
# documentation, with or without modification, are permitted provided that the
# following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * The names of the copyright holders or contributors may not be used to
#    endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE AND
# DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ===----------------------------------------------------------------------===

.PHONY: all
all: .pkg/.stamp-h

.PHONY: check
check: .pkg/.stamp-h
	mkdir -p build/report/xunit
	echo "\
	import unittest2; \
	import xmlrunner; \
	unittest2.main( \
	  testRunner=xmlrunner.XMLTestRunner(output='build/report/xunit'), \
	  argv=['unit2', 'discover', \
	    '-s','python_patterns', \
	    '-p','*.py', \
	    '-t','.', \
	  ] \
	)" >.pytest.py
	chmod +x .pytest.py
	.pkg/bin/coverage run .pytest.py || { rm -f .pytest.py; exit 1; }
	.pkg/bin/coverage xml --omit=".pytest.py" -o build/report/coverage.xml
	rm -f .pytest.py

.PHONY: shell
shell: .pkg/.stamp-h
	.pkg/bin/ipython

.PHONY: mostlyclean
mostlyclean:

.PHONY: clean
clean: mostlyclean
	-rm -rf build
	-rm -rf .coverage
	-rm -rf .pkg

.PHONY: distclean
distclean: clean
	-rm -rf .cache

.PHONY: maintainer-clean
maintainer-clean: distclean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

.PHONY: dist
dist:

# ===--------------------------------------------------------------------===
# ===--------------------------------------------------------------------===

.cache/virtualenv/virtualenv-1.6.4.tar.gz:
	mkdir -p .cache/virtualenv
	sh -c "cd .cache/virtualenv && curl -O http://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.6.4.tar.gz"

.pkg/.stamp-h: conf/requirements*.pip .cache/virtualenv/virtualenv-1.6.4.tar.gz
	${MAKE} clean
	tar \
	  -C .cache/virtualenv --gzip \
	  -xf .cache/virtualenv/virtualenv-1.6.4.tar.gz
	python .cache/virtualenv/virtualenv-1.6.4/virtualenv.py \
	  --clear \
	  --no-site-packages \
	  --distribute \
	  --never-download \
	  --prompt="(python-patterns) " \
	  .pkg
	rm -rf .cache/virtualenv/virtualenv-1.6.4
	.pkg/bin/easy_install readline
	mkdir -p .cache/pypi
	for reqfile in conf/requirements*.pip; do \
	  .pkg/bin/python .pkg/bin/pip install \
	    --download-cache="`pwd`"/.cache/pypi \
	    -r $$reqfile; \
	done
	touch .pkg/.stamp-h

# ===--------------------------------------------------------------------===
# End of File
# ===--------------------------------------------------------------------===
