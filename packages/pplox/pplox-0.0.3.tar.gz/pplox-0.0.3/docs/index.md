# Welcome to pplox

pplox is a pure Python implementation of the Lox programming language from Robert Nystrom's [Crafting Interpreters](https://craftinginterpreters.com/).
This project was developed using additional material and automated test cases provided by CodeCrafters.
Alongside the interpreter, this also includes continuous integration and continuous deployemnt using GitHub Actions for automated testing and release.

## Usage

To use this project, we provide a `pip` package which you can install using `pip install pplox`. 
To use the tokenizer run `pplox --tokenize <filename>`.
Currently expression evaluation is under development.  

## Project Layout

    .github/workflows/cicd.yml    # The CI/CD configuration pipeline.
    pplox/
        cli.py                    # The command-line interface
        ...                       # The interpreter implementation
    test_scanner.py               # Test for the scanner.
    docs/                         # Project documentation

## Build Pipeline

We have build pipelines set up to publish every push to [TestPyPI](https://test.pypi.org/project/pplox/) and every tag to [PyPI](https://pypi.org/project/pplox/).
Every release is tested using our test suite.

## Developing

If you want to contribute, the source code is hosted on [https://github.com/karlcaga/pplox](https://github.com/karlcaga/pplox).
Clone the repo with `git@github.com:karlcaga/pplox.git`.
Report bugs to [https://github.com/karlcaga/pplox/issues](https://github.com/karlcaga/pplox/issues).
