# Product Catalog Website

This project renders multiple web pages with CRUD and Google OAuth2. The root route displays a list of product categories. Each of theses categories has a list of products that can be displayed by clicking on the "Product List" button. Uses can add new categories and products, edit them and delete them. However, to make changes, uses must be logged in - using Google login.

## Table of Contents
1. Getting Started
2. Author
 

## 1. Getting Started

These instructions will get you a copy of the project. 

### Prerequisites

* Python 2.7
* flask - render_template, request, redirect, jsonify, url_for
* sqlalchemy - create_engine
* sqlalchemy.orm - sessionmaker
* os
* requests
* google.oauth2.credentials
* google_auth_oauthlib.flow
* sqlalchemy import Column, ForeignKey, Integer, String
* sqlalchemy.ext.declarative - declarative_base
* sqlalchemy.orm - relationship


### Google Developer Console
* Create a web application project and obtain client ID for the app. Download the json file and save it as client_secret.json in the same location as the app.py file.
* Go to Google Drive API - ensure it is enabled 

### Install & Run

###### Step 1
Clone the project from [udacity-project4-product-catalog.](https://github.com/selenewaide/udacity-project4-product-catalog.git)
```
git clone https://github.com/selenewaide/udacity-project4-product-catalog.git
```

###### Step 2
Ensure that the client_secret.json file has been saved in - see Google Developer Console section above.

###### Step 3
Run the app.py file to render the website.
```
python app.py
```


## 2. Author

Selene Waide


