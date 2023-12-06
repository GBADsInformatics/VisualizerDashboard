# 
# Contains routes for the flask app
# Everything commented out in this file is used for OAuth login functionality 
# 


from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import current_app as app
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
# from six.moves.urllib.parse import urlencode


# PROFILE_KEY = 'profile'
# JWT_PAYLOAD = 'jwt_payload'
app.secret_key = env.get('SECRET_KEY',"randomstringofcharacters")
app.debug = env.get('DEBUG','false').lower() in ('true', '1', 't')

DASH_BASE_URL = env.get('BASE_URL','/dash')

AUTH0_CALLBACK_URL = env.get('AUTH0_CALLBACK_URL', DASH_BASE_URL+"/")
AUTH0_CLIENT_ID = env.get('AUTH0_CLIENT_ID', None)
AUTH0_CLIENT_SECRET = env.get('AUTH0_CLIENT_SECRET', None)
AUTH0_DOMAIN = env.get('AUTH0_DOMAIN',"test-auth0-test1.us.auth0.com")
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get('AUTH0_AUDIENCE', None)
AUTH0_REDIRECT = env.get('AUTH0_REDIRECT', DASH_BASE_URL+"/")


# @app.route('/')
# def home():
#     """Landing page."""
#     return render_template(
#         'index.jinja2',
#         title='Plotly Dash Flask Tutorial',
#         description='Embed Plotly Dash into your Flask applications.',
#         template='home-template',
#         body="This is a homepage served with Flask."
#     )

# @app.errorhandler(Exception)
# def handle_auth_error(ex):
#     response = jsonify(message=str(ex))
#     response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
#     return response


# oauth = OAuth(app)

# auth0 = oauth.register(
#     'auth0',
#     client_id=AUTH0_CLIENT_ID,
#     client_secret=AUTH0_CLIENT_SECRET,
#     api_base_url=AUTH0_BASE_URL,
#     access_token_url=AUTH0_BASE_URL + '/oauth/token',
#     authorize_url=AUTH0_BASE_URL + '/authorize',
#     client_kwargs={
#         'scope': 'openid profile email',
#     },
# )

# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         if PROFILE_KEY not in session:
#             return redirect('/login')
#         return f(*args, **kwargs)
#     return decorated


# Controllers API
@app.route('/')
def home():
    return redirect(AUTH0_REDIRECT)


# @app.route('/callback')
# def callback_handling():
#     auth0.authorize_access_token()
#     resp = auth0.get('userinfo')
#     userinfo = resp.json()

#     session[JWT_PAYLOAD] = userinfo
#     session[PROFILE_KEY] = {
#         'user_id': userinfo['sub'],
#         'name': userinfo['name'],
#         'picture': userinfo['picture']
#     }
#     return redirect(AUTH0_REDIRECT)


# @app.route('/login')
# def login():
#     return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


# @app.route('/logout')
# def logout():
#     session.clear()
#     params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
#     return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


# @app.route('/dashboard')
# @requires_auth
# def dashboard():
#     return render_template('dashboard.html',
#     userinfo=session[PROFILE_KEY],
#     userinfo_pretty=json.dumps(session[JWT_PAYLOAD], indent=4))
