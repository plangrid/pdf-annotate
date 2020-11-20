.PHONY: setup test

PY35 ?= '3.5.10'
PY36 ?= '3.6.12'
PY37 ?= '3.7.9'

setup:
	-pyenv virtualenv -p python3.5 $(PY35) py35-pdf-annotate
	-pyenv virtualenv -p python3.6 $(PY36) py36-pdf-annotate
	-pyenv virtualenv -p python3.7 $(PY37) py37-pdf-annotate
	pyenv local py35-pdf-annotate py36-pdf-annotate py37-pdf-annotate
	pip install tox
