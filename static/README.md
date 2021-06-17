Install react requirements

```
/static$ npm install
``` 

Build react project

```
/static$ npm run build
```

if you want to use another port number for gunicorn server, then change the port number in /script/baseURL.json to what you set in gunicorn and run this command:
npm run build

example:
from:
{
    "url": "http://0.0.0.0:8080/api/"
}
to:
{
    "url": "http://0.0.0.0:{PORT}/api/"
}