import string
import random
import datetime
from functools import wraps
from flask import Flask, request, render_template, Response, redirect
from redis import Redis

app = Flask(__name__)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'username' and password == 'password'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def id_generator():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(4))

@app.route('/')
@requires_auth
def make_url_short():
    long_url = request.args.get('url', '')
    if long_url:
        keyword = request.args.get('keyword', '')
        if keyword:
            if not r.sadd("keywords", keyword):
                return Response("Bad keyword", mimetype="text/plain")
        else:
            keyword = id_generator()
            while not r.sadd("keywords", keyword):
                keyword = id_generator()

        r.set("lurl:" + keyword, long_url)
        return Response(request.url_root + keyword, mimetype="text/plain")
    return Response("Bad URL", mimetype="text/plain")

@app.route('/<keyword>')
def on_click(keyword):
    if r.sismember("keywords", keyword):
        long_url = r.get('lurl:' + keyword)
        r.lpush('clicks:' + keyword, str(datetime.datetime.now().date()))
        return redirect(long_url)

if __name__ == '__main__':
    r = Redis()
    app.run(debug=True)