import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app
from navbar import Navbar
from views import view_scatter 
from views import view_vobcfault
import util

TILOGO = "https://transitinsight.com/site_media/images/logo-ti.png"

nav = Navbar()
app.title = "ViewTrac"

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Row(
        [
            #dbc.Col(util.get_logo_img(), style={'height':'35px', 'margin-left':'5px', 'margin-top':'5px', 'vertical-align':"middle"}),
            dbc.Col(html.Img(src=TILOGO), style={'height':'35px', 'margin-left':'5px', 'margin-top':'5px', 'vertical-align':"middle"}),
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
    else:
        return '404: missing app = {}'.format(pathname)

if __name__ == '__main__':
    app.run_server(debug=True)
