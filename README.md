# PyCyanide

## What is this?

A simple script to download comics from [Cyanide and Happiness](http://explosm.net/).


## How does this work?

It uses [requests](https://pypi.python.org/pypi/requests/) and [lxml](https://pypi.python.org/pypi/lxml/) to download comics from [Cyanide and Happiness](http://explosm.net/).

## How do I use this?

1. Clone the repo
    ```
    git clone git@github.com:thesantosh/pycyanide.git
    cd PyCyanide
    ```

2. Install [Pipenv](https://github.com/kennethreitz/pipenv)

    ```
    pip install pipenv
    ```

3. Install required packages

    ```
    pipenv --two
    pipenv install
    ```

4. Run `pipenv` shell

    ```
    pipenv shell
    ```

5. Run the script

    ```
    python pycyanide.py
    ```

    or

    ```
    python pycyanide.py --start 1613 --end 1512
    ```
