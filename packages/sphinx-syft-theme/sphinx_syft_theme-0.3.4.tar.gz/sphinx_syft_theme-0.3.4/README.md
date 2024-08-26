# Sphinx Syft Theme

This mini documentation contains the basic development and deployment steps for sphinx-syft-theme. Additional information is available [here](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#packaging-your-project)

Build files

```
python3 -m pip install -e .

pip install build

python3 -m build --sdist

python3 -m build --wheel

twine check dist/*

twine upload dist/*
```

Install dependencies

```
pip install -r requirements.txt

```

This is Sphinx Syft Theme package. You can contribute via [Github](https://github.com/callezenwaka/sphinx-syft-theme/).