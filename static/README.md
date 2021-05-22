if you want to use another port number for gunicorn server, then change the port number in /script/baseURL.json to what you set in gunicorn and run this command:
npm run build

example:
from:
{
    "url": "http://localhost:5000/api/"
}
to:
{
    "url": "http://localhost:{New Port Number}/api/"
}