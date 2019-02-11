.PHONY: setup test

setup:
	-pyenv virtualenv -p python2.7 2.7.15 py27-pdf-annotate
	-pyenv virtualenv -p python3.5 3.5.6 py35-pdf-annotate
	-pyenv virtualenv -p python3.6 3.6.8 py36-pdf-annotate
	pyenv local py35-pdf-annotate py36-pdf-annotate py27-pdf-annotate
	pip install tox
