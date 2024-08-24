# pyOsiriX Example Project
An example project to demonstrate a method for creating a full project for use in pyOsiriX.

It uses the following project structure. Look inside each file to see a description of what it does.

```python
pyosirix_example_project/  # The root directory
├── .github/               # Where configuration files for GitHub are located.
│   └── workflows/         # Where you define GitHub actions to be performed when you push code. Run automatically.
│       └── release.yaml   # What actions are performed on a release. For example, upload to Python Package Index (pip).
├── package_1/             # The first Python package, where main source code will be stored. Use as many as you need.
│   ├── __init__.py        # You need an __init__.py file to declare a folder as a Python package. It can be empty!
│   ├── p1_module_1.py     # Each source file is a Python "module".
│   └── p1_module_2.py     # Use as many as you need to make the code structure logical.
├── package_2/             # You can have more than one package if needed and logical.
│   ├── __init__.py        # Don't forget this!
│   ├── p2_module_1.py     # As above.
├── tests/                 # The location of unit tests. These could, for example be run automatically as a GitHub action.
│   ├── p1_1_tests.py      # Test module 1 of package 1.
│   ├── p1_2_tests.py      # Test module 2 of package 1.
│   └── p2_1_tests.py      # Test module 1 of package 2.
├── .bumpversion.cfg       # Tells bump2version the version increment rules.
├── .gitignore             # The gitignore tells git which files not to include in version control.
├── LICENSE                # Tell people what the legal implications of your code are. There are many templates (e.g. MIT).
├── pyosirix_run.py        # This is flexible, but it can be good to be clear where the initial hook for pyosirix is.
├── pyproject.toml         # The configuration file for the Python project. Needed to tell pip  
├── README.md              # This file. GitHub will render it as the first page when you visit a repository online.
├── requirements.txt       # Tell the user (and pip) what the library dependencies are.
└── VERSION                # It can be helpful for clarity to store a master version file.
```

## Requirements
A good way to generate the requirements file automatically is run [`pipreqs`](https://github.com/bndr/pipreqs) as follows from the root directory:
```python
pip install pipreqs
pipreqs . --force
```


