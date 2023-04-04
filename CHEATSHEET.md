 Install requirements:

 ```pip install -r requirements.txt``` 
___

 Run tests:

 ```python3 setup.py pytest```
___

[Create a package tutorial](https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f)

Upload package:
```python setup.py bdist_wheel```
```twine upload dist/*```