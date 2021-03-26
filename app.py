#=============================================================================#
#                                                                             #
#                             Covid19 Dashboard                               #
#                                                                             #
#=============================================================================#

# Perform imports here:
import pandas as pd
pd.options.mode.chained_assignment = None  # default  = 'warn'
import numpy as np
import io
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output
import plotly.express as px

from elements import SPAIN_COLOURS
from data import get_covid_data_Spain, get_geo_Spain_data, get_sunburst_data

# Launch the application:
app = dash.Dash(external_stylesheets=[dbc.themes.CERULEAN])
app.config.suppress_callback_exceptions = True
server = app.server

# Spain Data
df_spain = get_covid_data_Spain()

Spain = df_spain.groupby('Date').sum().reset_index()
Spain['Region'] = 'Spain'
df_spain = pd.concat([df_spain,Spain],axis=0)

df_spain_line_data = df_spain[['Date', 'Cases',
                               'Daily Cases; 7-day rolling average', 'Deaths',
                               'Daily Deaths; 7-day rolling average', 'Region']]
df_geo_spain = get_geo_Spain_data(df_spain)
df_sunburst = get_sunburst_data(df_spain)


#=============================================================================#
#                                                                             #
#                               Plots - Spain                                 #
#                                                                             #
#=============================================================================#

#=============================================================================#
#                                  Sunburst                                   #
#=============================================================================#

fig_sunburst = px.sunburst(df_sunburst,
                           path=['Country','Region','Cases','variable'],
                           values='value',color='Region',
                           color_discrete_map = SPAIN_COLOURS)

#=============================================================================#
#                                                                             #
#                                 Layout                                      #
#                                                                             #
#=============================================================================#

#=============================================================================#
#                                   Sidebar                                   #
#=============================================================================#

sidebar = html.Div(
    [
        html.Div('Covid-19 Dashboard',
        style={'color':'#2fa4e7', 'fontSize':'4vw'}),
        html.Hr(),
        html.P(
            'Data following the Covid-19 pandemic', className='lead'
        ),
        dbc.Nav(
            [
                dbc.NavLink('World', href='/World', id='page-1-link'),
                dbc.NavLink('Spain', href='/Spain', id='page-2-link'),
                dbc.NavLink('Cyprus', href='/Cyprus', id='page-3-link'),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style= {
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '20%',
        'padding': '2rem 1rem',
        'background-color': '#f8f9fa',
    },
)

content = html.Div(
    id='page-content',
    style={
        'margin-left': '25%',
    }
)

#=============================================================================#
#                                   Spain                                     #
#=============================================================================#

spain = dbc.Container([
    #=========================================================================#
    #=== Row 1
    dbc.Row(html.H1('Spain')),
    dbc.Row([
        html.Div([
            dbc.Label('Select Regions:'),
            dcc.RadioItems(
                id = 'region_set',
                options = [
                    {'label': ' Spain', 'value': 'Spain'},
                    {'label': ' Madrid, Catalonia', 'value': 'MC'},
                    {'label': ' All Regions', 'value': 'All'},
                ],
                value = 'MC',
                labelStyle =
                {
                    'display': 'inline-block',
                    'margin': '5px',
                }
            ),#RadioItems
            dcc.Dropdown(
                id = 'Selected_Regions',
                multi = True,
            ),
        ],
            style = {
                'width': '100%',
            }
        ),#Div
    ]),#Row 1

    #=========================================================================#
    #=== Row 2
    dbc.Row([
        #=====================================================================#
        #=== Col1
        dbc.Col([
            dbc.Card([
                dbc.FormGroup([
                    #=========================================================#
                    #=== Metric Selector
                    dbc.Label('Metric:'),
                    dbc.RadioItems(
                        id = 'yaxis_scale_s',
                        options =[
                            {'label': 'Linear','value': False},
                            {'label': 'Logarithmic','value': True},
                        ],
                        value = False,
                    ),#RadioItems
                ]),#FormGroup
                dbc.FormGroup([
                    #=========================================================#
                    #=== Data Selector
                    dbc.RadioItems(
                        id = 'Spain_Data_to_show',
                        options =[
                            {'label': 'Confirmed','value': 'Cases'},
                            {'label': 'Daily Confirmed',
                             'value': 'Daily Cases; 7-day rolling average'},
                            {'label': 'Deaths','value': 'Deaths'},
                            {'label': 'Daily Deaths',
                             'value': 'Daily Deaths; 7-day rolling average'},
                        ],
                        value = 'Daily Cases; 7-day rolling average',
                    ),#RadioItems
                ]),#FormGroup
            ],
                style = {
                    'width': '11rem',
                },
                body = True
            ),#Card
        ],
            md = 2,
        ),#Col1

        #=====================================================================#
        #=== Col2
        dbc.Col([
            dcc.Graph(id = 'Spain_Line_Graph')
        ],
            md = 10,
        ),#Col2
    ],
        align = 'center',
    ),#Row2

    #=========================================================================#
    #=== Row 3
    dbc.Row([
        #=====================================================================#
        #=== Col1
        dbc.Col([
            dbc.Card([
                html.Div([
                    dbc.Row([
                        daq.BooleanSwitch(id='boolean_switch_spain',on=False),
                        dbc.Label('Animate Map')
                    ]),
                ],
                    style = {
                        'padding': '0.5rem 0.5rem',
                    }
                ),
                dbc.FormGroup([
                    #=========================================================#
                    #=== Map Data Selector
                    dbc.RadioItems(
                        id = 'Spain_Map_Data_to_show',
                        options =[
                            {'label': 'Confirmed','value': 'Cases'},
                            {'label': 'Daily Confirmed',
                            'value': 'Daily Cases'},
                            {'label': 'Deaths','value': 'Deaths'},
                            {'label': 'Daily Deaths',
                            'value': 'Daily Deaths'},
                        ],
                        value = 'Cases',
                    ),#RadioItems
                ],
                ),#FormGroup
            ],
                style = {
                    'width': '11rem',
                },
                body = True,
            ),#Card
        ],
            md = 2,
        ),#Col1

        #=====================================================================#
        #=== Col2
        dbc.Col([
            dcc.Graph(id = 'Spain_Map')
        ],
            md = 10,
        ),#Col2
    ],
        align = 'center',
    ),#Row3

    #=========================================================================#
    #=== Row 4
    dbc.Row([
        #=====================================================================#
        #=== Sunburst Plot
        dbc.Label('Click on regions for more info:'),
        dcc.Graph(
            id = 'Sunburst',
            figure = fig_sunburst
        ),#Graph
    ],
        align = 'center',
    ),#Row4
    #=========================================================================#
    #=== Row 5
    dbc.Row([
        dbc.Label('Source: Datadista.com ;'),
        html.A(' Data',
               href='https://github.com/datadista/datasets/raw/master/COVID%2019/',
               target='_blank'),
    ]),
])#Container Spain

#=============================================================================#
#                                  Cyprus                                     #
#=============================================================================#

cyprus = dbc.Container([
    dbc.Row([
        html.A('University of Cyprus Covid-19 Dashboard',
               href='https://covid19.ucy.ac.cy/',
               target='_blank')
    ],
        justify='center',
        align='center',
        className='h-50',
    )
],
    style={'height': '100vh'}
)

#=============================================================================#
#                                  World                                      #
#=============================================================================#

world = dbc.Container([
    dbc.Row([
        html.A('Worldwide Covid-19 Dashboard',
               href='https://ckallepitis-covid19.herokuapp.com/',
               target='_blank')
    ],
        justify='center',
        align='center',
        className='h-50',
    )
],
    style={'height': '100vh'}
)

#=============================================================================#
#                               App Layout                                    #
#=============================================================================#

app.layout = html.Div([
    dcc.Location(id='url'),
    sidebar,
    content,
])

#=============================================================================#
#                                                                             #
#                           Callbacks & Functions                             #
#                                                                             #
#=============================================================================#

#=============================================================================#
#                                 Sidebar                                     #
#=============================================================================#
# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f'page-{i}-link', 'active') for i in range(1, 4)],
    [Input('url', 'pathname')],
)
def toggle_active_links(pathname):
    if pathname == '/':
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f'/page-{i}' for i in range(1, 4)]


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page_content(pathname):
    if pathname == '/World':

        return world
    elif pathname in ['/', '/Spain']:

        return spain
    elif pathname == '/Cyprus':

        return cyprus
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1('404: Not found', className='text-danger'),
            html.Hr(),
            html.P(f'The pathname {pathname} was not recognised...'),
        ]
    )
#=============================================================================#
#                                   Spain                                     #
#=============================================================================#

#=============================================================================#
# ========== Dropdown Region list ==========

@app.callback(Output('Selected_Regions', 'options'),
             [Input('Spain_Data_to_show', 'value')])
def callback_region_list(Spain_Data_to_show):
    return [{'label':i,'value':i} for i in df_spain.Region.unique()]

#=============================================================================#
# ========== Region Selector ==========

@app.callback(Output('Selected_Regions', 'value'),
             [Input('region_set', 'value')])
def callback_region_set(region_set_value):

    if region_set_value == 'Spain':
        region_list = df_spain.query("Region == 'Spain'").Region.unique().tolist()
        return region_list
    if region_set_value == 'MC':
        region_list = df_spain.query("Region == ['Madrid','Catalonia']").Region.unique().tolist()
        return region_list
    if region_set_value == 'All':
        region_list = df_spain.query("Region == ['Andalusia','Aragon','Asturias'," +
                                     "'Balearic Islands','Canary Islands','Cantabria'," +
                                     "'Castille and Leon','Castille-La Mancha','Catalonia'," +
                                     "'Valencia','Extremadura','Galicia','Madrid','Murcia'," +
                                     "'Navarre','Basque Country','La Rioja']").Region.unique().tolist()
        return region_list


    return region_list

#=============================================================================#
# ========== Spain Line Graph ==========

@app.callback(Output('Spain_Line_Graph', 'figure'),
              [Input('Selected_Regions', 'value'),
              Input('yaxis_scale_s', 'value'),
              Input('Spain_Data_to_show', 'value')])

def callback_Spain_Line_Graph(Selected_Regions_value,
                              yaxis_scale_s_value,
                              Spain_Data_to_show_value):

    fig = px.line(
        df_spain_line_data.query("Region == "+str(Selected_Regions_value)),
        x = 'Date',
        y = Spain_Data_to_show_value,
        color = 'Region',
        color_discrete_map= SPAIN_COLOURS,
        log_y = yaxis_scale_s_value
    )

    fig.update_traces(hovertemplate=None)

    fig.update_layout(
        template = 'plotly_white',
        hovermode='x',
    )

    return fig

#=============================================================================#
# ========== Spain Map Selector ==========

@app.callback(Output('Spain_Map', 'figure'),
             [Input('Spain_Map_Data_to_show', 'value'),
             Input('boolean_switch_spain', 'on')])
def callback_Spain_Map(Spain_Map_Data_to_show_value,
                      boolean_switch_spain_on):

    df_geo_spain_o = df_geo_spain

    if not boolean_switch_spain_on:
        df_geo_spain_o = df_geo_spain.loc[df_geo_spain.groupby('Region')\
                                                    .Cases.idxmax()]

    fig = px.scatter_geo(
        df_geo_spain_o,
        lat = 'Lat',
        lon = 'Long',
        color = 'Region',
        color_discrete_map= SPAIN_COLOURS,
        hover_name = 'Region',
        hover_data = {
            'Region':False,
            'Date':True,
            'Lat':False,
            'Long':False,
        },
        size = Spain_Map_Data_to_show_value,
        animation_frame = 'Date' if boolean_switch_spain_on else None,
        projection = 'natural earth',
    )

    fig.update_layout(
        margin = dict(t = 0, l = 0, r = 0, b = 0),
        template = 'plotly_white',
    )

    fig.update_geos(fitbounds='locations',showcountries = True)

    if boolean_switch_spain_on:
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 10

    return fig

#=============================================================================#
#=============================================================================#

if __name__ == '__main__':
    app.run_server()
