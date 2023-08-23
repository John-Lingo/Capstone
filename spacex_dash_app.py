# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# inital values for range slider
min_value = 2500
max_value = 8000

# Create "Booster Version Category" column in database
spacex_df['Booster Version Category'] = 'unknown'
for index, row in spacex_df.iterrows():
    spacex_df.loc[index, 'Booster Version Category'] = spacex_df.loc[index,'Booster Version'].split(' ')[1]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                            options=[{'label': 'All Sites', 'value': 'ALL'},
                                                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},],
                                            value='ALL',
                                            placeholder='Select a launch site',
                                            searchable=True),
                                html.Br(),

                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                                value=[min_value, max_value]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # return the outcomes piechart for all sites combined (success only)
        filtered_df = spacex_df[spacex_df['class']==1].groupby("Launch Site", as_index=False).sum()
        fig = px.pie(filtered_df, values='class', 
                    names='Launch Site',
                    title='Total Successful Launches by Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        pie_df=pd.DataFrame(data={'Result':['Success', 'Failure'], 'Count':[filtered_df['class'].sum(),filtered_df['class'].count()-filtered_df['class'].sum()]})
        fig = px.pie(pie_df, values='Count', 
                    names='Result',
                    title='Launch Success Rate for Site ' + entered_site)
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    # Apply the range limits from the slider
    pre_filtered_df = spacex_df[spacex_df['Payload Mass (kg)']<=payload_range[1]]
    filtered_df = pre_filtered_df[pre_filtered_df['Payload Mass (kg)']>=payload_range[0]]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title='Correlation between Payload Mass and Success for All Sites')
        return fig
    else:
        site_df = filtered_df[filtered_df['Launch Site']==entered_site]
        fig = px.scatter(site_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title='Correlation between Payload Mass and Success for Site ' + entered_site)
        return fig
        # return the outcomes piechart for a selected site

# Run the app
if __name__ == '__main__':
    app.run_server()
