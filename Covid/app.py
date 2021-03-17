import numpy as np
import pandas as pd

# import dash dependencies
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px


app = dash.Dash(__name__,)
app.config['suppress_callback_exceptions'] = True

# read excel data and load data to DataFrame
df = pd.read_excel('extract_data_excercise.xlsx',sheet_name='Détails des passages ',engine='openpyxl')


dates_ = df.date.unique()
orl =[]
dyspnee = []
fievre = []
total_infections = []
# On peut chnager la variable ajustement . Elle est egale a 6 par defaur
ajustement  = 6
max_total_passages = df['total passages'].max()


for d in dates_:
    orl_val = float(df[(df.date== d) & (df.variable == 'orl')]['total passages'])
    orl.append(orl_val)

    dyspnee_val = float(df[(df.date== d) & (df.variable == 'dyspnee')]['total passages'])
    dyspnee.append(dyspnee_val)

    fievre_val = float(df[(df.date== d) & (df.variable == 'fievre')]['total passages'])
    fievre.append(fievre_val)

    max_total_passages = max([orl_val, dyspnee_val , fievre_val])
    pct = pd.Series.to_numpy(df[(df['total passages'] == max_total_passages) & (df.date== d)]['pct'])

    total_infections.append(max_total_passages * float(pct[0]) * ajustement)

orl_df = pd.DataFrame({'date' : dates_ , 'orl': orl })
dyspnee_df = pd.DataFrame({'date' : dates_ , 'dyspnee': dyspnee})
fievre_df = pd.DataFrame({'date' : dates_ , 'fievre': fievre})
data   = pd.DataFrame({'date' : dates_ ,'orl':orl , 'dyspnee': dyspnee , 'fievre': fievre , 'total_infections' : total_infections })
fig1 = px.area(data , x ='date' , y = data.columns , title = 'Infections respiratoires(hors codes diagnostics covid 19)')
 

# option dropdown 
khi = [str(d) for d in dates_]
val_tmp = []
for d in range(len(dates_)):
    val_tmp.append(str(dates_[d]).split('T')[0])

mes_options = [{'label' : str(k), 'value' : str(v)} for k,v in zip(val_tmp, dates_)]

# logic graph 2
dff = pd.read_excel('extract_data_excercise.xlsx',sheet_name ='Détails hospitalisations covid',engine='openpyxl')
dff["catégorie d'âge"] = dff["catégorie d'âge"].apply(lambda x: x.split('ans')[0])
dff["catégorie d'âge"] = dff["catégorie d'âge"].apply(lambda x: x.strip())


    # Categorical mapping 
    # 0 => 0-14
    # 1 => 15-44
    # 2 => 45-64
    # 3 => 65-74
    # 4 => 75

categories = {
    '0' : '0-14',
    '1' : '15-44',
    '2' : '45-64',
    '3' : '65-74',
    '4' : '75',    
    }
code = []
for c in dff["catégorie d'âge"]:
    for val in categories:
        if (str(c) == str(categories[val])):
            code.append(val)
            
dff['categories_code'] = code
cat_df = dff[['date' , 'categories_code' , 'total passages']]
# ====================== layout =====================================
app.layout = html.Div(children=[
    html.H1(html.Center(children='Covid app')),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='graph1',
        figure=fig1
    ) ,

    html.H1(html.Center(children="patients hospitalisés selon l'age")),
    # dcc dropdown 
    html.Div(children = [
          dcc.Dropdown(
            id='dropdown',
            options= [{'label': str(k) , 'value' :str(v)} for k,v in zip(val_tmp, dates_)],
            value = mes_options[-1]['value']
            ),

    dcc.Graph(
        id='graph2',  
    )

    ])
  
])
# ===============================================================

# ============== callback =========================

@app.callback(
    dash.dependencies.Output('graph2', 'figure'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_output(selected_value):
    dd = pd.to_datetime(selected_value)   
    df_tmp = cat_df[cat_df['date'] == dd].groupby('categories_code').sum()
    df_tmp['ages'] = ['0-14', '15-44', '45-64', '65-74', '75 ou plus']


    fig2 = px.bar(df_tmp , x = 'ages' , y = 'total passages' )
    return fig2

'''
@app.callback(
    dash.dependencies.Output('graph2', 'figure'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_output(value):
    print(value)
    return None
'''

# start dash app
if __name__ == '__main__':
    app.run_server(debug=True)


# create a  dropdown with dates