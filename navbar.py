import dash_bootstrap_components as dbc
import dash_html_components as html

TILOGO = "https://transitinsight.com/site_media/images/logo-ti.png"
#TILOGO = "ti_logo.jpg"

def Navbar():
    navbar = dbc.Navbar(
        [
            dbc.DropdownMenu(
                children=[
                    #dbc.DropdownMenuItem("VOBC Fault", header=True),
                    dbc.DropdownMenuItem("VOBC Fault Report", href="/views/vobcfault_v"),
                    dbc.DropdownMenuItem("VOBC Fault Correlation", href="/views/view2"),
                    dbc.DropdownMenuItem("Page 3", href="/views/view3"),
                    #dbc.DropdownMenuItem("Communication", header=True),
                    dbc.DropdownMenuItem("Comm Loss Correlation", href="/views/view2"),

                ],
                label="VOBC Report",
                style={'backgroundColor':'lightgrey', 'color':'blue'},
                color="lightgrey",
                toggle_style={"color": "black"},
            ),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("VOBC Fault Correlation", href="/views/view2"),
                    dbc.DropdownMenuItem("Page 3", href="/apps/app3"),
                ],
                label="Wayside Report",
                style={'backgroundColor':'lightgrey', 'color':'blue'},
                color="lightgrey",
                toggle_style={"color": "black"},
            ),
        ],
        style={'backgroundColor':'lightgrey'},
        color="lightgrey",#if remove this line, above doesn't work
        #backgroundColor="lightgrey",


        #dark=False,
    )

    return navbar


def Navbar_simple():
    navbar = dbc.NavbarSimple(
        children=[
            #dbc.NavItem(dbc.NavLink("VOBC Fault Report", href="/views/vobcfault_v")),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("VOBC Fault", header=True),
                    dbc.DropdownMenuItem("VOBC Fault Report", href="/views/vobcfault_v"),
                    dbc.DropdownMenuItem("VOBC Fault Correlation", href="/views/view2"),
                    dbc.DropdownMenuItem("Page 3", href="/views/view3"),
                    dbc.DropdownMenuItem("Communication", header=True),
                    dbc.DropdownMenuItem("Comm Loss Correlation", href="/views/view2"),

                ],
                nav=True,
                in_navbar=True,
                label="VOBC Report",
            ),

            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("VOBC Fault Correlation", href="/views/view2"),
                    dbc.DropdownMenuItem("Page 3", href="/apps/app3"),
                ],
                nav=True,
                in_navbar=True,
                label="Wayside Report",
            ),
            dbc.NavItem(dbc.NavLink("Who We Are", href="http://www.transitinsight.com", target="_blank")),
        ],
        brand="ViewTrac",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True,
    )

    return navbar
