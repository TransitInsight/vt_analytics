import dash_bootstrap_components as dbc

def Navbar():
    navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="/views/vobcfault_v")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="/views/view2"),
                dbc.DropdownMenuItem("Page 3", href="/apps/app3"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="ViewTrac",
    brand_href="#",
    color="primary",
    dark=True,
    fluid=True,
    )

    return navbar
