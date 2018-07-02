clean:
	python dev/clean.py

deploy: clean pypi
	git push
	git push --tags
	twine upload dist/*
	python dev/clean.py

deps:
	pip install -r requirements.txt --upgrade
	pip install -r dev/requirements.txt --upgrade

pypi:
	python setup.py sdist

register:
	python setup.py register -r pypi

test: clean
	tox
