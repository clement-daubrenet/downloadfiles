from flask import Flask, request, redirect, session, url_for, make_response, send_from_directory
from requests_oauthlib import OAuth2Session
import os

app = Flask(__name__)

# I created a new project in Google API with new credentials for it that I entered there
client_id = 'MYCLIENTID'
client_secret = 'MYCLIENTSECRET'

# A callback endpoint defined later
redirect_uri = 'https://127.0.0.1:5000/callback'

# Various urls coming from the documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
refresh_url = token_url
scope = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]


@app.route("/")
def login():
    """
    Redirection towards Google login.
    n.b: after the login, the callback endpoint is called.
    """
    google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = google.authorization_url(authorization_base_url,
                                                        access_type="offline",
                                                        prompt="select_account")
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route("/callback", methods=["GET"])
def callback():
    """
    Fetching the application access token.
    n.b: the redirection to this callback comes with an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    google = OAuth2Session(client_id, redirect_uri=redirect_uri,
                           state=session['oauth_state'])
    token = google.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)
    session['oauth_token'] = token
    return redirect(url_for('.download'))


@app.route("/download", methods=["GET"])
def download():
    """
    Downloading a zip files.
    n.b: The file is stored locally.
    :return:
    """
    filename = 'file_to_download.zip'
    response = make_response(send_from_directory(os.getcwd(), filename))
    response.headers['Content-Disposition'] = 'attachment; filename=' + filename
    response.content_type = 'application/zip'
    return response


if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(host='127.0.0.1', port=5000, debug=True)
