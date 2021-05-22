# ufw-manager
Flask REST-API and React UI for managing UFW service


## Table of Contents

- [Installation](#installation)
- [Addresses](#addresses)
- [License](#license)

## Installation

1.Create a virtual environment

```
$ python3 -m venv venv
```

2.Activate the virtual environment

```
$ source venv/bin/activate
```

3.Install python requirements

```
$ pip3 install -r requirements.txt 
``` 

4.Navigate to the static folder with cd command

```
$ cd static
```

5.Install react requirements

```
/static$ npm install
``` 

6.Build react project

```
/static$ npm run build
```

7.Navigate back to main diractory and run gunicorn server with root privilages and port you want

```
/static$ cd ..
$ sudo venv/bin/gunicorn -b=127.0.0.1:<PORT> app:app
```
now enjoy it.

If you like this you can support me with a star and share it

## Addresses

API documentation is accessible at this address when you run the local server at: http://localhost:{PORT}/docs/

React UI is accessible at this address when you run the local server at: http://localhost:{PORT}/

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


- **[GNU GPL v3 license](https://opensource.org/licenses/gpl-3.0.html)**
- Copyright 2021 © <a href="https://github.com/mohammad-hasanzadeh89" target="_blank">Mohammad Hasanzadeh</a>.
