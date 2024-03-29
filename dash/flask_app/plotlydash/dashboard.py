from __future__ import annotations
import json
from logging import disable
from operator import gt
from os.path import exists
from os import environ as env
import requests
import numpy as np
import pandas as pd
import math
import urllib.parse
import dash
from dash import dcc,html,dash_table,callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
from datetime import date, datetime
from functools import wraps
from flask import session, redirect
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from dash.exceptions import PreventUpdate
from layouts import *
from dash.dependencies import Input, Output, State
# from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
import json
from textwrap import dedent

# default='warn'
pd.options.mode.chained_assignment = None  

# dash base url
DASH_BASE_URL = env.get('BASE_URL','/dash')

# Importing dataset
DATAFRAME = pd.read_csv('datasets/Faostat_Data.csv')

# Insert data cleaning here
COUNTRIES = sorted(DATAFRAME['country'].unique())
SPECIES = sorted(DATAFRAME['species'].unique())

METASET = 'datasets/metadata/'
METADATA_SOURCES = {
    'EXAMPLE DATA':{ # Datasources added in this section needs to be updated in layouts.py line 205
        'METADATA': METASET+'20220613_FAOSTAT_QCL.csv', # The displayed meta data table
        'DOWNLOAD': METASET+'20220613_FAOSTAT_QCL.json', # For download as json button
        'PROVENANCE': METASET+'ExampleProvenance.txt', # Provenance for dataset
    },
}
METADATA_OTHER = {
    'GLOSSARY':{
        'CSV': METASET+'MetadataGlossary.csv',
    },
}


def filterdf(code, column, df):
    if code is None:
        return df
    if isinstance(code,list):
        if len(code) == 0:
            return df
        return df[df[column].isin(code)]
    return df[df[column]==code]


# PROFILE_KEY = 'profile'
# JWT_PAYLOAD = 'jwt_payload'

def init_dashboard(server):
            
    dash_app = dash.Dash(__name__,
        server=server,
        title='FAOSTAT Data Visualizer',
        routes_pathname_prefix=DASH_BASE_URL+'/',
        external_stylesheets=[
            # 'https://codepen.io/chriddyp/pen/bWLwgP.css',
            dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP
        ],
    )
    # Setting active page
    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False)
    ],id='page-content')
    init_callbacks(dash_app)
    return dash_app.server

# isLoggedIn = False
# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         global isLoggedIn
#         if PROFILE_KEY not in session:
#             isLoggedIn = False
#             return redirect('/login')
#         isLoggedIn = True
#         return f(*args, **kwargs)
#     return decorated

# def checkRole():
#     isRole = False
#     y = json.dumps(session[JWT_PAYLOAD])
#     person_dict = json.loads(y)
#     p = (person_dict["http://gbad.org/roles"]) # This link sends you to the Ground Based Air Defense website lmao
#     stringver = json.dumps(p)
#     print(stringver)
#     if 'Verified User' in stringver:
#         isRole = True
#     else:
#         isRole = False
#     return isRole

# def getJWT(personDict,userCat):
#     p = (personDict[userCat])
#     stringVer = json.dumps(p)
#     s1 = stringVer.replace("[]","")
#     strippedString = s1.strip('"')
#     return strippedString

# @requires_auth
# def getUserContent():
#     y = json.dumps(session[JWT_PAYLOAD])
#     personDict = json.loads(y)
#     userEmail = getJWT(personDict,"email")
#     print(userEmail)
#     return userEmail


##CALLBACKS -------------------------------------------------------------------------------------------------------------------------------------------------------------
def init_callbacks(dash_app):
    
    # # Callbacks to handle login components
    # @dash_app.callback(
    #     Output(component_id='login-button', component_property='style'),
    #     Input('url', 'pathname')
    # )
    # @requires_auth
    # def login_button(pathname):
    #     checkRole()
    #     return {'margin-left': '5px', 'display': 'none'}
    
    # @dash_app.callback(
    #     Output(component_id='logout-button', component_property='style'),
    #     Input('url', 'pathname')
    # )
    # @requires_auth
    # def logout_button(pathname):
    #     return {'margin-top': '10px', 'margin-right':'10px', 'float': 'right'}

    # # Callback to handle feedback.
    # @dash_app.callback(
    #     Output('feedback-text', 'value'),
    #     Output('feedback-button', 'disabled'),
    #     Output('feedback-text', 'disabled'),
    #     Input("feedback-button", "n_clicks"),
    #     State('feedback-text', 'value')
    # )
    # def feedback_box(n, text):
    #     if (n > 0 and text != None and text != ""):
    #         outF = open("feedback.txt", "a")
    #         outF.writelines('["'+text+'"]\n')
    #         outF.close()
    #         return\
    #             "Thank you for your feedback",\
    #             True,\
    #             True
    #     else:
    #         print("no")
    
    # Callback to handle changing the page based on the pathname provided.
    @dash_app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == DASH_BASE_URL+'/':
            layout = page_1
        else:
            layout = "404"
        return layout


    #################################
    # Visualizer Specific Callbacks #
    #################################

    # Update stored options
    @dash_app.callback(
        Output('stored-options', 'data'),
        [State('tabs', 'value')],
        Input('options-countries-a', 'value'),
        Input('options-countries-b', 'value'),
        Input('options-countries-c', 'value'),
        Input('options-countries-d', 'value'),
        Input('options-species-a', 'value'),
        Input('options-species-b', 'value'),
        Input('options-species-c', 'value'),
        Input('options-species-d', 'value'),
    )
    def update_stored_options_a(tab, drop1a, drop1b, drop1c, drop1d, drop2a, drop2b, drop2c, drop2d):
        if tab == 'tab-2':
            return {'options-country':drop1b,'options-species':drop2b}
        elif tab == 'tab-3':
            return {'options-country':drop1c,'options-species':drop2c}
        elif tab == 'tab-4':
            return {'options-country':drop1d,'options-species':drop2d} 
        else:
            return {'options-country':drop1a,'options-species':drop2a}


    # Update options values on changing tab
    @dash_app.callback(
        Output('options-countries-a', 'value'),
        Output('options-countries-b', 'value'),
        Output('options-countries-c', 'value'),
        Output('options-countries-d', 'value'),
        Output('options-species-a', 'value'),
        Output('options-species-b', 'value'),
        Output('options-species-c', 'value'),
        Output('options-species-d', 'value'),
        Output('options-choice-c', 'value'),
        Output('options-choice-d', 'value'),
        [Input('tabs', 'value')],
        State('stored-options', 'data'),
    )
    def options_on_tab_change(selected_tab,stored_options):
        if stored_options is None:
            return COUNTRIES[0], COUNTRIES[0], COUNTRIES[0], COUNTRIES[0], SPECIES[0], SPECIES[0], SPECIES[0], SPECIES[0], "Country", "Country"
        return stored_options['options-country'],stored_options['options-country'],stored_options['options-country'],stored_options['options-country'], \
            stored_options['options-species'],stored_options['options-species'], stored_options['options-species'], stored_options['options-species'], "Country", "Country"


    # Init dropdowns
    @dash_app.callback(
        Output('options-countries-a', 'options'),
        Output('options-species-a', 'options'),
        Output('options-countries-b', 'options'),
        Output('options-species-b', 'options'),
        Output('options-countries-c', 'options'),
        Output('options-species-c', 'options'),
        Output('options-choice-c', 'options'),
        Output('options-choice-d', 'options'),
        Output('options-countries-d', 'options'),
        Output('options-species-d', 'options'),
        Input('dummy_div', 'children'),
    )
    def dropdown_options(_a):
        # Return applicable options
        return COUNTRIES,SPECIES,COUNTRIES,SPECIES,COUNTRIES,SPECIES,['Country', 'Species'],['Country', 'Species'],COUNTRIES,SPECIES

    # Displaying graph
    # TAB 1
    @dash_app.callback(
        Output('graph-container', 'children'),
        Input('options-countries-a', 'value'),
        Input('options-species-a', 'value')
    )
    def create_graph(country, species):
        
        # Declare descriptor string
        graphDesc = "" + country + " , " + species


        # Filtering the dataframe to only include specific species/countries
        
        df = filterdf(country,'country',DATAFRAME)
        df = filterdf(species,'species',df) #only use the species given by user

        #ensure years are in proper order
        df = df.sort_values("year")  
        fig = None
        
        df['colours'] = ['#43BCCD' if fl == 'A' else '#662E9B' if fl == 'E' else '#F1D302' if fl == 'I' else '#FFFFFF' if fl == 'M' else '#EA3546' for fl in df['flag']]
        colors = ['#43BCCD', '#662E9B', '#F1D302', '#EA3546', '#FFFFFF']
        labels = ['Official', 'Estimated', 'Imputed', 'Non-FAO', 'Missing']

        fig = go.Figure() #Initialize plot
        fig.add_trace(go.Scatter(x=df['year'], y=df['population'], mode='lines+markers', name='', marker=dict(size=10, color=df['colours'], line=dict(width=2,
                                        color='DarkSlateGrey')), line=dict(color='black')))
        
        df.loc[:, 'flag'] = df['flag'].replace(['A', 'E', 'I', 'X', 'M'], ['Official', 'Estimated', 'Imputed', 'Non-FAO', 'Missing'])
        # Adding colours for legend
        for color, label in zip(colors, labels):
            if label in df['flag'].unique():
                fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=12, color=color, line=dict(width=2,
                                            color='DarkSlateGrey')), showlegend=True, legendgroup=color, name=label))

        
        
        #Alter graph output if user has made selections through the dash
        if(country is not None and species is not None):

            #TODO
            # -Provide list of graphs that go over a certain threshold %
            # -
            
            if df.empty:
                plotTitle = species + " Population by Year in " + country + " is an Empty Dataset"
                graphDesc = "Warning: " + species + " Population by Year in " + country + " is an Empty Dataset"
            else:
                plotTitle = species + " Population by Year in " + country

                df.loc[:, 'flag'] = df['flag'].replace(['Official', 'Estimated', 'Imputed', 'Non-FAO', 'Missing'],['A', 'E', 'I', 'X', 'M'])
                #Prepare the flag values to determine which one is most present in the current graph
                counts = df['flag'].value_counts()
                if 'E' in counts:
                    fValue = (counts['E'] / len(df)) * 100
                else:
                    fValue = 0
                if 'A' in counts:
                    oValue = (counts['A'] / len(df)) * 100
                else:
                    oValue = 0
                if 'X' in counts:
                    uValue = (counts['X'] / len(df)) * 100
                else:
                    uValue = 0
                if 'I' in counts:
                    iValue = (counts['I'] / len(df)) * 100
                else:
                    iValue = 0

                graphDesc = species + " Population by Year in " + country + ":\n"
                highest = max(fValue,oValue,uValue,iValue)
                
                if fValue == highest:
                    graphDesc = graphDesc + " Contains " +  f"{fValue:.2f}%" + " Estimated Values."
                elif oValue == highest:
                    graphDesc = graphDesc + " Contains " +  f"{oValue:.2f}%" + " Official Values. "
                elif uValue == highest:
                    graphDesc = graphDesc + " Contains " +  f"{uValue:.2f}%" + " Non-FAO Values."
                else:
                    graphDesc = graphDesc + " Contains " +  f"{iValue:.2f}%" + " Imputed Values. "
        else:
            plotTitle = " "

        for trace in fig['data']:
            if trace['name'] == '':
                trace['showlegend'] = False

        fig.update_layout(title=dict(text=plotTitle, font=dict(size=25), automargin=True, yref='paper'), template="plotly_white")
        fig.update_layout(
            margin={"r":10,"t":45,"l":10,"b":10},
            font=dict(
                size=16,
            )
        )
        fig.layout.autosize = True


        return dcc.Graph(className='main-graph-size', id="main-graph", figure=fig)

    # Displaying Flag Summary
    # TAB 3
    @dash_app.callback(
        Output('summary-container', 'children'),
        Output('species-container-c', 'style'),
        Output('options-countries-c', 'style'),
        Output('country-title-c', 'style'),
        Input('options-countries-c', 'value'),
        Input('options-species-c', 'value'),
        Input('options-choice-c', 'value')
    )
    def create_summary(country, species, choice):
        
        # Filter the dataframe according to user's option selections
        styleC = {'display': 'block'}
        styleS = {'display': 'block'}
        styleTitle={"margin":"0.4rem 0 0.2rem 0", 'display': 'block'}
        if(choice == 'Country'):
            df = filterdf(country,'country',DATAFRAME)
            styleS = {'display': 'none'}
            styleC = {'display': 'block'}
            styleTitle={"margin":"0.4rem 0 0.2rem 0", 'display': 'block'}
        else:
            df = filterdf(species,'species',DATAFRAME)
            styleS = {'display': 'block'}
            styleC = {'display': 'none'}
            styleTitle={"margin":"0.4rem 0 0.2rem 0", 'display': 'none'}

        fig = None

        #Alter dataframe for readability
        df.loc[:, 'flag'] = df['flag'].replace(['A', 'E', 'I', 'X', 'M'], ['Official', 'Estimated', 'Imputed', 'Non-FAO', 'Missing'])

        df_group = df.groupby(['year', 'flag']).size().reset_index(name='count')
        df_group['percent'] = df_group.groupby('year')['count'].apply(lambda x: x / x.sum() * 100).round(2)
        
        #Adding percentages to graph
        if not df.empty:
            fig = go.Figure()
            legend_flags = []
            
            for i, year in enumerate(df_group['year'].unique()): #For each year
                df_year = df_group[df_group['year'] == year]
                df_yearS = df_year.sort_values(['flag'], ascending=False)
                for j, row in enumerate(df_yearS.iterrows()): #For each row in the year
                    if row[1]['flag'] == 'Official':
                        color = "#43BCCD"
                    elif row[1]['flag'] == 'Estimated':
                        color = '#662E9B'
                    elif row[1]['flag'] == 'Imputed':
                        color = '#F1D302'
                    elif row[1]['flag'] == 'Non-FAO':
                        color = '#EA3546'
                    else:
                        color = '#000000'
                        
                    showlegend = False
                    if row[1]['flag'] not in legend_flags: #Only add to legend if first occurence of flag
                        showlegend = True
                        legend_flags.append(row[1]['flag'])
                    fig.add_trace(
                        go.Bar(
                            x=[row[1]['year']],
                            y=[row[1]['percent']],
                            name=row[1]['flag'],
                            marker_color=color,
                            legendgroup=row[1]['flag'],
                            showlegend=showlegend
                        )
                    )

            fig.update_layout(barmode='stack', yaxis={'title': 'Percentage'}, xaxis={'title': 'Year'})

        #Set title for graph
        if(country is not None):
            if df.empty:
                plotTitle = " "
            else:
                if(choice == 'Country'):
                    plotTitle = "Yearly Percentage of Flags in " + country
                else:
                    plotTitle = "Yearly Percentage of Flags for " + species + " Across all Countries"
                
        else:
            plotTitle = " "

        fig.update_layout(title=dict(text=plotTitle, font=dict(size=25), automargin=True, yref='paper'), template="plotly_white")
        fig.update_layout(
            margin={"r":10,"t":45,"l":10,"b":10},
            font=dict(
                size=16,
            )
        )
        fig.layout.autosize = True

        return dcc.Graph(className='main-graph-size', id="main-graph", figure=fig), styleS, styleC, styleTitle
    


    # Updating Datatable
    # TAB 2
    @dash_app.callback(
        Output('data-table-container','children'),
        Input('options-countries-b', 'value'),
        Input('options-species-b', 'value')
    )
    def render_table(country,species):
        
        # Filtering the dataframe to only include specific species/countries
        df = filterdf(country,'country',DATAFRAME)        
        df = filterdf(species,'species',df)

        #ensure years are in proper order
        df = df.sort_values("year")  
    
        # Rendering the data table
        cols = [{"name": i, "id": i,"hideable":True} for i in df.columns]
        cols[0] = {"name": "ID", "id": cols[0]["id"],"hideable":True}
        datatable = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=cols,
            export_format="csv",
            style_cell={
            'textAlign':'left',
            'font-family':'sans-serif'}
        )
        return datatable

    # Updating Analyze Table
    # TAB 4
    @dash_app.callback(
        Output('acc-table-container','children'),
        Output('species-container-d', 'style'),
        Output('options-countries-d', 'style'),
        Output('country-title-d', 'style'),
        Input('options-countries-d', 'value'),
        Input('options-species-d', 'value'),
        Input('options-percent-d', 'value'),
        Input('options-choice-d', 'value')
    )
    def render_table(country,species,percent,choice):
        # Filtering the dataframe to only include specific species/countries
        # Filter the dataframe according to user's option selections
        sortChoice = 'species'
        styleC = {'display': 'block'}
        styleS = {'display': 'block'}
        styleTitle={"margin":"0.4rem 0 0.2rem 0", 'display': 'block'}
        if(choice == 'Country'):
            df = filterdf(country,'country',DATAFRAME)
            styleS = {'display': 'none'}
            styleC = {'display': 'block'}
            styleTitle={"margin":"0.4rem 0 0.2rem 0", 'display': 'block'}
            sortChoice = 'species'
        else:
            df = filterdf(species,'species',DATAFRAME)
            styleS = {'display': 'block'}
            styleC = {'display': 'none'}
            styleTitle={"margin":"0.4rem 0 0.2rem 0", 'display': 'none'}
            sortChoice = 'country'
        
        #ensure years are in proper order
        df = df.sort_values([sortChoice,"year"])

        newdf = pd.DataFrame(columns=df.columns)
        newdf.drop(newdf.index , inplace=True)

        newdf.insert(3, 'previous year population', np.nan)
        k = 0
        l = 0
        for j in df['population']:
            if(k != 0):
                if(df[sortChoice].iloc[k] == df[sortChoice].iloc[k-1]): # if countries are the same
                    if(df['population'].iloc[k-1] != 0): # if not the first year of said country
                        diff = ((df['population'].iloc[k] - df['population'].iloc[k-1]) / df['population'].iloc[k-1]) * 100

                        if diff < 0:
                            diff = diff * -1
                        if diff > percent:
                            newdf = newdf.append(df.iloc[k], ignore_index=True)
                            newdf.loc[l, 'previous year population'] = df['population'].iloc[k-1]
                            l+=1
            k+=1



        # Rendering the data table

        cols = [{"name": i, "id": i,"hideable":True} for i in newdf.columns]
        cols[0] = {"name": "ID", "id": cols[0]["id"],"hideable":True}


        datatable = dash_table.DataTable(
            data=newdf.to_dict('records'),
            columns=cols,
            export_format="csv",
            style_cell={
            'textAlign':'left',
            'font-family':'sans-serif'},
            style_table={'height': '600px', 'overflowY': 'auto'}
        )

        return datatable, styleS, styleC, styleTitle

    # Updating Alert
    @dash_app.callback(
        Output('alert-container','children'),
        Input('options-countries-a', 'value'),
    )
    def render_alert(country):
        amsg = None

        # ADD LOGIC HERE TO CREATE ALERT MESSAGES
        # amsg syntax:
        # amsg = ['Please choose 1 type when graphing multiple countries.','danger']

        if amsg is None: 
            return None
        else:
            return dbc.Alert([html.H5('Warning'),amsg[0]], color=amsg[1])
    
    
    ### Updating METADATA ###
    @dash_app.callback(
        Output('metadata-container','children'),
        Output('download-container','children'),
        Output('meta-type','data'),
        Input('meta-gbads-button','n_clicks'),
        Input('provenance-button','n_clicks'),
        Input('glossary-button','n_clicks'),
        Input('meta-source-dropdown','value'),
        State('meta-type','data'),
    )
    def update_meta(MetaButton,ProvButton,GlossButton,MetaValue,MetaType):        
        # Filtering data with the menu values
        pressed = callback_context.triggered[0]['prop_id'].split('.')[0]
        df = ''
        downloadButton = ''
        meta=MetaType

        if (pressed == 'meta-source-dropdown' and MetaType == 'meta') or pressed == 'meta-gbads-button' or pressed == '':
            meta = 'meta'
            df = pd.read_csv(METADATA_SOURCES[MetaValue]['METADATA'], names=['Col1', 'Col2'])
            # # UNCOMMENT FOR DOWNLOAD AS JSON BUTTON
            # req = requests.get(METADATA_SOURCES[MetaValue]['DOWNLOAD'])
            # json_data = json.dumps(req.json(), indent=2, ensure_ascii=False).replace('#', '%23')
            # downloadButton = html.A(
            #     href=f"data:text/json;charset=utf-8,{json_data}",
            #     children='Download Metadata',download=METADATA_SOURCES[MetaValue]['DOWNLOAD'].split('/')[-1],id='meta-download-button',className='download-button'
            # )
        elif (pressed == 'meta-source-dropdown' and MetaType == 'pro') or pressed == 'provenance-button':
            meta = 'pro'
            with open(METADATA_SOURCES[MetaValue]['PROVENANCE']) as file:
                df = dcc.Markdown(file.readlines())
            return df,downloadButton,meta
        elif pressed == 'glossary-button':
            df = pd.read_csv(METADATA_OTHER['GLOSSARY']['CSV'], names=['Col1', 'Col2'])

        datatable = dash_table.DataTable(
            data=df.to_dict('records'),
            # Removing header
            css=[{'selector': 'tr:first-child','rule': 'display: none'}],
            # Adding hyperlinks
            columns=[
                {'name': 'Col1', 'id': 'Col1'},
                {'name': 'Col2', 'id': 'Col2', 'presentation': 'markdown'}
            ],
            # Styling
            style_cell={'textAlign': 'left'},
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=[
                {
                    'if': {
                        'column_id': 'Col1',
                    },
                    'fontWeight': 'bold'
                }
            ],
            cell_selectable=True,
        )
        return datatable,downloadButton,meta