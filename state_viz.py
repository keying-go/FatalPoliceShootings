# Import packages
from dash import Dash, html, dash_table, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px


# Incorporate data
df = pd.read_csv('fatal-police-shootings-data.csv')
df = df.dropna(subset=["state"])
df["date"] = pd.to_datetime(df['date'])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.to_period('M')

# count shootings by race
state_df = df.groupby(["state","year","race"])["id"].count().reset_index().rename(columns={"id":"count"}).sort_values(by=["year"])

# calculate shooting rate per 1k pop by race
race = pd.read_csv("state_race.csv").rename(columns={"State":"state"})
race = race.melt(id_vars="state",var_name="race" ,value_name="race_pop")
race_df = state_df.merge(race,how="left",on=["state","race"]).sort_values(by="year")
race_df["rate"] = race_df["count"]/race_df["race_pop"]*1000

state_df["race"] = state_df.race.map({"W": "White, non-Hispanic",
"B": "Black, non-Hispanic",
"A": "Asian",
"N": "Native American",
"H": "Hispanic",
"O": "Other"})
race_df["race"] = race_df.race.map({"W": "White, non-Hispanic",
"B": "Black, non-Hispanic",
"A": "Asian",
"N": "Native American",
"H": "Hispanic",
"O": "Other"})

# Initialize the app
app = Dash(__name__)


app.layout = html.Div([
    html.H1(children='Fatal Police Shootings 2015 - 2022', style={'textAlign':'center',"font-size":20}),
    html.Div(children="Race"),
    dcc.Dropdown(state_df.race.unique(), 'White, non-Hispanic', id='dropdown-selection',style={"width": "50%"},),
    html.Br(),
    html.Div(children = ["year",html.Br(),dcc.Slider(
        df['year'].min(),
        df['year'].max(),
        step=None,
        value=df['year'].min(),
        marks={str(year): str(year) for year in df['year'].unique()},
        id='year-slider')],style={"width":"60%", "Align":"Center"}),
    
    html.Div(children = [dcc.Graph(id='graph-count',style={'display': 'inline-block'}),dcc.Graph(id='graph-rate',style={'display': 'inline-block'})]),
    
])

@callback(
    Output('graph-count', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('year-slider', 'value')
)
def update_graph(race,year):
    
    return px.choropleth(state_df[(state_df["race"]==race)&(state_df["year"]==year)],title="Count of fatal police shootings by race",locations="state", locationmode="USA-states", color="count", range_color=(0,80),
                     hover_name="state", 
                     scope="usa")

@callback(
    Output('graph-rate', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('year-slider', 'value')
)
def update_graph(race,year):
    
    return px.choropleth(race_df[(race_df["race"]==race)&(race_df["year"]==year)],
                          title = "Rate of fatal police shootings by race (per 1000 people)",
                          locations="state", locationmode="USA-states", color="rate", range_color=(0,5),
                     hover_name="state", 
                     scope="usa")

if __name__ == '__main__':
    app.run(debug=True)

