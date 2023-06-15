This project is retired; no further contributions accepted.

# Testing

To run the tests, you have a couple of options.

Option 1: [tox][1]. Install tox, locate yourself in the main project
directory, and run `tox`. All dependencies will be installed in
virtual environments, and the code will be tested against Python 2.6
and 2.7, if they are installed on your system.

Option 2: Install [nose][2] and [mock][4]. Locate yourself in the main
project directory, and run `nosetests`.

# Building documentation

Install [sphinx][3], locate yourself in the `docs` directory and
run `make html`. Then open the `_build/index.html` page.

[1]: http://tox.testrun.org/latest/
[2]: https://nose.readthedocs.org/en/latest/
[3]: http://sphinx.pocoo.org/
[4]: http://pypi.python.org/pypi/mock
