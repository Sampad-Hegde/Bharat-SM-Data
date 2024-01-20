# Install wheel optionally twine
```shell
pip install wheel twine
```

# To build new package version:

```shell
python setup.py sdist bdist_wheel
```


# Twine test files and formats
```shell
twine check dist/*
```

# To publish to test-PYPI:
```shell
twine upload -r testpypi build/Bharat_sm_data-<version>*
```

# Testing Test-pypi package

```shell
 pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple Bharat-sm-data=={version}
```


# To publish to PYPI:
```shell
twine upload build/Bharat_sm_data-<version>*
```