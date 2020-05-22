import dash_bootstrap_components as dbc

TILOGO = "https://transitinsight.com/site_media/images/logo-ti.png"

def Navbar():
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
