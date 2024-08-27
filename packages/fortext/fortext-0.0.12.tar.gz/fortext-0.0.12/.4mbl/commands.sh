exit 0 #! not meant to be executed as a file

# building and publishing package
py -m pip install --upgrade build twine && py -m build && py -m twine upload -u __token__ -p $(cat ./.4mbl/pypi/token.txt) dist/*

# testing published package
rmrf venv/testing_fortext && py -m venv venv/testing_fortext && venv/testing_fortext/Scripts/activate && py -m pip install --upgrade fortext
