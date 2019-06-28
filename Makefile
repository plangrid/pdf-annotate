.PHONY: setup test

setup:
	-pyenv virtualenv -p python3.5 3.5.4 py35-pdf-annotate
	-pyenv virtualenv -p python3.6 3.6.5 py36-pdf-annotate
	pyenv local py35-pdf-annotate py36-pdf-annotate
	pip install tox
