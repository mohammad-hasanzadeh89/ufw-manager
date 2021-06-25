# ufw-manager
Flask REST-API and React UI for managing UFW service


## Table of Contents

- [Installation](#installation)
- [Management](#management)
- [Addresses](#addresses)
- [License](#license)

## Installation

1.download installtion file from <a download="install.sh" href="https://github.com/mohammad-hasanzadeh89/ufw-manager/raw/master/install.zip" title="install">HERE</a> (right click on it and click on "Save Link As...")

2.run the script as root

```
$ chmod +x install.sh
$ sudo bash install.sh 
```

now enjoy it.

## Management
You can manage ufw-mng service with these command:

* managing config file of ufw-mng:

```
$ cd /opt/ufw-manager/ && source venv/bin/activate && sudo python3 manage.py
```
or

```
$ cd /opt/ufw-manager/ 
/opt/ufw-manager$ source venv/bin/activate
(vnev) /opt/ufw-manager$ sudo python3 manage.py
```

* start ufw-mng:

```
$ service ufw-mng start
```

* stop ufw-mng:

```
$ service ufw-mng stop
```

* restart ufw-mng:

```
$ service ufw-mng restart
```

* enable ufw-mng:

```
$ service ufw-mng enable
```

* see status of ufw-mng:

```
$ service ufw-mng status
```

If you like this you can support me with a star and share it

## Addresses

API documentation is accessible at this address when you run the local server at: http://0.0.0.0:8080/docs/

React UI is accessible at this address when you run the local server at: http://0.0.0.0:8080/

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


- **[GNU GPL v3 license](https://opensource.org/licenses/gpl-3.0.html)**
- Copyright 2021 © <a href="https://github.com/mohammad-hasanzadeh89" target="_blank">Mohammad Hasanzadeh</a>.
