## Publish a New Version to PyPI
1. Increment the version number.
2. Install twine `pip install --upgrade twine` if you haven't already.
3. Build Distribution: Generate distribution files using the following command: `python setup.py sdist bdist_wheel`
4. If you don't already have your twine + pypi credentials setup, follow the instructions [here](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#create-an-account).
5. Finally, run `twine upload dist/*`.