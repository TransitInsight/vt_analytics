import dash
from flask import Flask
import flask
#from dashapp import server as application
import dash_bootstrap_components as dbc

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = flask.Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED], server=server)
app.secret_key = 'secretkeythatyouneverguess'

# app = dash.Dash(__name__)

#server = app.server
app.config.suppress_callback_exceptions = True