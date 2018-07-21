.PHONY: setup test

setup:
	-pyenv virtualenv -p python2.7 2.7.13 py27
	-pyenv virtualenv -p python3.5 3.5.4 py35
	-pyenv virtualenv -p python3.6 3.6.5 py36
	pyenv local py35 py36 py27
	pip install tox
