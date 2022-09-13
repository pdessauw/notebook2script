# Notebook2script

A simple-minded converter to extract Jupyter notebook code into a Python script. Make 
sure the [Python](https://www.python.org/downloads/) version used is >=3.9.

## Usage

To convert a notebook, use the following command:
```shell
python convert.py ${path_to_notebook} --output ${path_to_script}
```

If the output seems too messy, try with `--reformat` option:
```shell
python convert.py ${path_to_notebook} --output ${path_to_script} --reformat
```

N.B.: This option is EXPERIMENTAL, do not expect a lot out of it.
