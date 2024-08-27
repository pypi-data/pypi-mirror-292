def plot_map(file_path, map_dropdown, start, end):
    # Enter the start and end year (2012~2021) 
    # to get the mental disease incidence rate world map
    from dash import Dash, html, dcc, Input, Output, State, callback
    import dash_bootstrap_components as dbc
    import plotly.express as px
    import pandas as pd
    from pycountry import countries
    df = pd.read_csv(file_path)
    country_code_not_in_pycountry = {"Micronesia (Federated States of)":'FSM',
                                        "Taiwan":'TWN',
                                        "Democratic People's Republic of Korea":'PRK',
                                        "Republic of Korea":'KOR', "Republic of Moldova":'MDA',
                                        "United States of America":'USA', "Bolivia (Plurinational State of)":'BOL',
                                        "Venezuela (Bolivarian Republic of)":'VEN', "Iran (Islamic Republic of)":'IRN',
                                        "Turkey":'TUR', "Palestine":'PSE', "Democratic Republic of the Congo":'COD',
                                        "United Republic of Tanzania":'TZA', "United States Virgin Islands":'VIR'}

    feature = map_dropdown
    df_a = pd.DataFrame(columns = ['Country', 'Year', feature])

    cal = 0
    dict = df.to_dict(orient='index')
    for i in range(df.shape[0]):
        if (df.loc[i, 'Year'].item() > int(start)) and (df.loc[i, 'Year'].item() <= int(end)):
            df_a.loc[cal] = [df.loc[i, 'Country'], df.loc[i, 'Year'].item(), df.loc[i, feature].item()]
            cal+=1

    for i in range(df_a.shape[0]):
        if countries.get(name=df_a.loc[i, 'Country']):
            df_a.loc[i, 'iso_alpha'] = countries.get(name=df_a.loc[i, 'Country']).alpha_3
        else:
            df_a.loc[i, 'iso_alpha'] = country_code_not_in_pycountry[df_a.loc[i, 'Country']]

    fig = px.choropleth(df_a, locations="iso_alpha",
                        color=feature, # lifeExp is a column of gapminder
                        hover_name="Country", # column to add to hover information
                        color_continuous_scale=px.colors.sequential.Viridis_r)
    return fig


def check_box_selection(wg):
    import ipywidgets as widgets
    from ipywidgets import Checkbox, VBox, HBox
    checkboxes = [widgets.Checkbox(value=False, description=label) for label in wg]
    output = widgets.HBox(children=checkboxes)
    display(output) # it is for jupyter notebook to import and display
    return checkboxes

def checked_list(checked_box):
    selected_data = []
    for i in range(0, len(checked_box)):
        #print(checked_box[i])
        if checked_box[i].value == True:
            selected_data = selected_data+[checked_box[i].description]
    return selected_data

def plot_pairplot(filepath, selected_data):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(filepath)
    if len(selected_data) > 0:
        list_pp = ['Incidence'] + selected_data
        #print("Features: ",list_pp)
        sns.pairplot(df[list_pp], 
                    markers='+',
                    plot_kws=dict(linewidth=1))
        plt.show()