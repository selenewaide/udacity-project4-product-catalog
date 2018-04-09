#!/usr/bin/env python2.7
"""Product catalog web application."""

from flask import render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Product
import os
import flask
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow


# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'

app = flask.Flask(__name__)

# secret key
app.secret_key = 'REPLACE ME  this value is here  placeholder.'

engine = create_engine('sqlite:///product_catalog4.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def login():
    """Google login."""
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    # Save credentials back to session in case access token was refreshed.
    flask.session['credentials'] = credentials_to_dict(credentials)

    return render_template('login.html')


@app.route('/authorize')
def authorize():
    """Create flow instance to manage the OAuth 2 Authorization Grant Flow steps."""
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server
        # apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    """
    Specify the state when creating the flow in the callback.

    So that it can verified in the authorization server response.
    """
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('login'))


@app.route('/revoke')
def revoke():
    """Revoking Google credentials."""
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post(
        'https://accounts.google.com/o/oauth2/revoke',
        params={'token': credentials.token},
        headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        print("Credentials successfully revoked.")
        return redirect(url_for('clear_credentials'))
    else:
        return('An error occurred.')


@app.route('/clear')
def clear_credentials():
    """Clear Google credentials."""
    if 'credentials' in flask.session:
        del flask.session['credentials']

    return render_template('logout.html')


def credentials_to_dict(credentials):
    """Google credentials dict."""
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


# ---------------------------------------------------
# PRODUCT CATALOG ROUTES
# ---------------------------------------------------


@app.route('/')
@app.route('/categories/')
def categories_list():
    """List off all the categories."""
    categories = session.query(Category)

    products = session.query(Product).order_by(
        Product.created.desc()).limit(4).all()

    return render_template(
        'categories.html',
        categories=categories,
        products=products)


@app.route('/categories/new', methods=['GET', 'POST'])
def categories_new():
    """Add a new category."""
    if 'credentials' not in flask.session:
        return render_template('login_check.html')

    if request.method == 'POST':
        category_new = Category(name=request.form['name'],
                                description=request.form['description'])
        session.add(category_new)
        session.commit()
        return redirect(url_for('categories_list'))
    else:
        return render_template('categories_new.html')


@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def categories_edit(category_id):
    """Edit a category."""
    if 'credentials' not in flask.session:
        return render_template('login_check.html')

    category_edit = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            category_edit.name = request.form['name']

        if request.form['description']:
            category_edit.description = request.form['description']

        session.add(category_edit)
        session.commit()
        return redirect(url_for('categories_list'))
    else:
        return render_template('categories_edit.html', category=category_edit)


@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
def categories_delete(category_id):
    """Delete a category."""
    if 'credentials' not in flask.session:
        return render_template('login_check.html')

    category_delete = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        session.delete(category_delete)
        session.commit()
        return redirect(url_for('categories_list'))
    else:
        return render_template('categories_delete.html',
                               category=category_delete)


@app.route('/products/<int:category_id>/')
def products_list(category_id):
    """List of all the products for a category."""
    category = session.query(Category).filter_by(id=category_id).one()
    products = session.query(Product).filter_by(category_id=category_id)

    return render_template(
        'products.html', products=products, category=category)


@app.route('/products/<int:category_id>/new', methods=['GET', 'POST'])
def products_new(category_id):
    """Add a new product to a category."""
    if 'credentials' not in flask.session:
        return render_template('login_check.html')

    if request.method == 'POST':
        product_new = Product(name=request.form['name'],
                              description=request.form['description'],
                              price=request.form['price'],
                              category_id=category_id)
        session.add(product_new)
        session.commit()
        return redirect(url_for('products_list', category_id=category_id))
    else:
        return render_template('products_new.html', category_id=category_id)


@app.route('/products/<int:category_id>/<int:product_id>/edit',
           methods=['GET', 'POST'])
def products_edit(category_id, product_id):
    """Edit a product."""
    if 'credentials' not in flask.session:
        return render_template('login_check.html')

    product_edit = session.query(Product).filter_by(
        id=product_id,
        category_id=category_id).one()

    if request.method == 'POST':
        if request.form['name']:
            product_edit.name = request.form['name']

        if request.form['description']:
            product_edit.description = request.form['description']

        if request.form['price']:
            product_edit.price = request.form['price']

        session.add(product_edit)
        session.commit()
        return redirect(url_for('products_list', category_id=category_id))
    else:
        return render_template('products_edit.html',
                               category_id=category_id,
                               product=product_edit)


@app.route('/products/<int:category_id>/<int:product_id>/delete',
           methods=['GET', 'POST'])
def products_delete(category_id, product_id):
    """Delete a product."""
    if 'credentials' not in flask.session:
        return render_template('login_check.html')

    product_delete = session.query(Product).filter_by(
        id=product_id,
        category_id=category_id).one()

    if request.method == 'POST':
        session.delete(product_delete)
        session.commit()
        return redirect(url_for('products_list', category_id=category_id))
    else:
        return render_template('products_delete.html',
                               category_id=category_id,
                               product=product_delete)


@app.route('/products/<int:category_id>/<int:product_id>/api')
def products_api(category_id, product_id):
    """API endpoint for a product."""
    if 'credentials' not in flask.session:
        return render_template('login_check.html')

    product = session.query(Product).filter_by(id=product_id,
                                               category_id=category_id).one()
    return jsonify(product=product.serialize)


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080, debug=True)
