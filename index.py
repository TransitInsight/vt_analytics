import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from navbar import Navbar
from views import view_view2 
from views import view_vobcfault

nav = Navbar()

app.title = "ViewTrac"
app.layout = html.Div([
    html.Div([nav]),#, style={'margin-right':'30px'}),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/views/vobcfault_v':
        return view_vobcfault.layout
    elif pathname == '/views/view2':
        return view_view2.layout
    else:
        return '404: missing app = {}'.format(pathname)

if __name__ == '__main__':
    app.run_server(debug=True)