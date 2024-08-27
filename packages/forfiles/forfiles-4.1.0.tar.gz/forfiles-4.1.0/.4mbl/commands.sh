exit 0 #! not meant to be executed

py -m pip install --upgrade build && py -m build && py -m twine upload -u __token__ -p $(cat ./.4mbl/pypi/token.txt) dist/*

rmrf venv/testing_forfiles && py -m venv venv/testing_forfiles && venv/testing_forfiles/Scripts/activate && py -m pip install --upgrade forfiles
