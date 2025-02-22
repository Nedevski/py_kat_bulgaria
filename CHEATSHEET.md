### Create venv:

`python3 -m venv venv`

### Mount venv:

`source venv/bin/activate`

### Install requirements:

`pip install -r requirements.txt`

`pip install -r requirements-test.txt`

---

### Run tests:

`python3 setup.py pytest`

---

### Create a package

[Tutorial link](https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f)

### Upload package prerequisites:

`pip install wheel`

`pip install twine`

### Upload package:

`python3 setup.py bdist_wheel`

`twine upload dist/*`

### One-liner:

`python3 setup.py bdist_wheel && twine upload dist/*`

---

### If pip does not see the latest version of the package in HomeAssistant (run twice)

`pip3 uninstall kat_bulgaria -y && pip3 install kat_bulgaria --upgrade`
