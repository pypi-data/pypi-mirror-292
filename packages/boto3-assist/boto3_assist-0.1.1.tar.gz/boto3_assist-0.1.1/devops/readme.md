# DevOps

## building
```sh
python setup.py sdist bdist_wheel
```

## deploying

```sh
twine upload dist/*

```

## uploading and testing with a "test"

```sh

twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pip install --index-url https://test.pypi.org/simple/ boto3-assist

```

pypi-AgEIcHlwaS5vcmcCJGQ0Zjk3ODRmLTgxZDMtNDViNy1iN2QwLWZkZDQzNTEyY2UwMgACKlszLCI3YzZmZTIzYS04MDVkLTQ0YjYtODlkZS04YTJiODJiNjBmMDQiXQAABiBxfnzdKtx6gff_FbuwKKV8D4b7XkUJJESxSqU1_mkCRA