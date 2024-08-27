# public_nested_packages

The purpose of this repository is to test the creation of multiple packages within a single repository. It aims to achieve the following goals:

- Create multiple packages within one repository.
- Prevent circular imports between modules.
- Keep imports at the package level in tests.
- Enable the repository to work independently, with or without the packages installed.

## Installation

You can install the package using pip...or not (that's the purpose!):


```bash
pip install gryszka-hello-package
pip install gryszka-another-package
```