
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from navbar import Navbar
from views import view_scatter 
from views import view_vobcfault
from views import view_commLoss
from views import view_switch
from views import view_switch_self_move
from views import view_mileage
from views import view_fault_trend
import util
import flask
from flask import Flask
from waitress import serve

TILOGO = "https://transitinsight.com/site_media/images/logo-ti.png"
#TILOGO = "http://localhost:8050/system_icon.png"

nav = Navbar()
app.title = "ViewTrac"


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Row(
        [

            #https://github.com/plotly/dash/issues/71
            
            #dbc.Col(util.get_logo_img(), style={'height':'35px', 'margin-left':'5px', 'margin-top':'5px', 'vertical-align':"middle"}),
            dbc.Col(html.Img(src=TILOGO), style={'height':'30px', 'margin-left':'5px', 'margin-top':'3px', 'margin-bottom':'3px', 'vertical-align':"middle"}),
            dbc.Col(nav, width = 2, style={'backgroundColor':'red'})
        ],
        justify="between",
        style={'backgroundColor':'lightgrey'}
    ),   

    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/views/vobcfault_v':
        return view_vobcfault.layout
    elif pathname == '/views/view2':
        return view_scatter.layout
    elif pathname == '/views/commLoss':
        return view_commLoss.layout
    elif pathname == '/views/view_switch':
        return view_switch.layout
    elif pathname == '/views/view_switch_self_move':
        return view_switch_self_move.layout
    elif pathname == '/views/view_mileage':
        return view_mileage.layout
    elif pathname == '/views/view_fault_trend':
        return view_fault_trend.layout
    else:
        return '404: missing app = {}'.format(pathname)

@app.server.route('/system_icon.png')
def serve_image_system_icon():
    return flask.send_from_directory(".", "ti_logo_small.png")


if __name__ == '__main__':
    #app.run_server(debug=True)
    serve(app.server, host='0.0.0.0', port=80, threads = 16)
