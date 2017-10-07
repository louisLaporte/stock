# Run Application
You need first to update your PYTHONPATH
```
$ export PYTHONPATH=$PYTHONPATH:$PWD
```
Install python package required
```
$ sudo pip3 install -r requirements.txt
```

BOKEH

To run the user interface:
```
$ bokeh serve --show ui/stock.py
```
