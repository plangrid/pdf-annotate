.PHONY: setup test

setup:
	-pyenv virtualenv -p python3.6 3.6.8 py36-pdf-annotate
	-pyenv virtualenv -p python3.7 3.7.4 py37-pdf-annotate
	pyenv local py36-pdf-annotate py37-pdf-annotate
	pip install tox
