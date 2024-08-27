from dash import Dash, dcc, html, Input, Output, ctx, callback, State
import dash_bootstrap_components as dbc
import warnings
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
import importlib
from WeatherRegression import WeatherRegression
warnings.simplefilter(action='ignore', category=FutureWarning)
from pycountry import countries
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="123")
from datetime import date, datetime, timedelta
import pandas as pd
import math
from meteostat import Stations, Daily

geolocator = Nominatim(user_agent="123")
controls = dbc.Card(
    [   
        html.Div(
            [
                "City: ",
                dcc.Input(id='city', value="Sydney", type="text",style={"width":"7rem", "margin":"0.5rem", "text-align":"center"}),
            ]
        ),
        html.Div(
            [
                "Lat.: ", 
                dcc.Input(id="lat", type="number", min=-90, max=90, style={"width":"6rem", "margin":"0.5rem", "text-align":"center"}),
                "Long.: ",
                dcc.Input(id="lon", type="number", min=-180, max=180, style={"width":"6rem", "margin":"0.5rem", "text-align":"center"}),
            ],

        ),
        html.Hr(),
        html.Div(
            [
                html.Button(' Search ',id='button', style={"padding":"0.5rem"}),
                " for the following ",
                dcc.Input(id="search_days", value=3, type="number", min=1, max=10, step=1, style={"width":"3rem", "margin":"0.5rem", "text-align":"center"}),
                " days",
            ],
        ),
    ], 
    body=True, style={"background-color": "transparent"} 
)

controls_1 = dbc.Card(
    [
        html.Div(
            [
                html.H5("Fill the following 4 criteria:"),
            ],
        ),
        html.Hr(),
        html.Div(
            [
                dbc.Label("Average Temperature"),
                html.Br(),
                dcc.Input(id="low_tavg", type="number", value=5, min=-5, max=40, step=0.5, style={"width":"4rem", "margin":"0.5rem", "text-align":"center"}),
                " ~ ", 
                dcc.Input(id="high_tavg", type="number", value=39, min=-5, max=40, step=0.5, style={"width":"4rem", "margin":"0.5rem", "text-align":"center"}),
                "°C",
            ]
        ),
        html.Hr(),
        html.Div(
            [
                dbc.Label("Max difference in temperature"),
                dcc.Input(id="delta_t_limit", value=20, type="number", style={"width":"4rem", "margin":"0.5rem", "text-align":"center"}),
                "°C",
            ],
        ), 
        html.Hr(),
        html.Div(
            [
                dbc.Label("Average Daily Precipition below"),
                dcc.Input(id="precipitation_limit", value=15, type="number", style={"width":"5rem", "margin":"0.5rem","text-align":"center"}),
                "mm",
            ],
        ),      
        html.Hr(),
        html.Div([
                dbc.Label("Snow Depth below"),
                dcc.Input(id="snow_limit", value=2, type="number", style={"width":"5rem", "margin":"0.5rem","text-align":"center"}),
                "mm",
        ]),
    ],
    body=True, style={"background-color": "transparent"}
)
res_map = dbc.Card(
    [html.Div(dcc.Graph(id="map")),], body=True, style={"width":"100%"}
)
res_table = html.Div(dbc.Table(id="table_container"))
#, style={, "background-image":"linear-gradient(to top left, #accdfa, #f7e5ab)"},
app.layout = dbc.Container(
    [
        dcc.ConfirmDialog(
            id='no_station_found',
            message='Sorry... No station nearby provides weather forecast data.',
        ),
        dcc.Loading(
            id="loading_1",
            type="circle", fullscreen=True, style={"backgroundColor": "rgba(255, 255, 224, 0.5)"},
            children=[html.Div(id="loading_output_1")]
        ),
        html.H2("Find Resorts with Weather Forecast Data", style={"padding-top":"2%", "text-align":"center"}),
        html.Hr(),
        #dbc.Row(controls, style={"margin":10}),
        dbc.Row([
        dbc.Col([dbc.Row(res_map),
                 dbc.Row(res_table, style={"text-align":"center"}),
                 ], md=9),
        dbc.Col(
            [
                dbc.Row(controls, style={"margin":"4px"}),
                dbc.Row(controls_1, style={"margin":"4px", "margin-top":"8px"}),
                #dbc.Col(dcc.Graph(id="map"), md=8),
            ], md=3
        ),
        ]
        ),
    ],
    fluid=True, style={"height":"100vh", "font-family":"Lucida Console","font-size":"16px"}
)

@app.callback(
    [
        Output("city", "value"),
        Output("lat", "value"),
        Output("lon", "value"),
        Output("table_container", "children"),
        Output("map", "figure"),
        Output("no_station_found", 'displayed'),
        Output("loading_output_1", "children"),
    ],
    [
        Input('button', 'n_clicks'),
    ],
    [
        State("city", "value"),
        State("search_days", "value"),
        State("low_tavg", "value"),
        State("high_tavg", "value"),
        State("delta_t_limit", "value"),
        State("precipitation_limit", "value"),
        State("snow_limit", "value"),
    ]
)

def fetch_resorts_data(n_clicks, city, search_days, low_tavg, high_tavg, delta_t_limit, precipitation_limit, snow_limit):
    if (n_clicks is not None) and (n_clicks > 0):  
        import pandas as pd
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="123")
        location = geolocator.geocode(city)
        print(location)
        if not location:
            exit
        lat = location.latitude
        lon = location.longitude
        print(lat)

        '''
        elif ctx.triggered_id == "lat":
            lat = 45 if lat is None else lat
            city = geolocator.reverse(str(lat)+','+str(lon))
        elif ctx.triggered_id =="lon":
            lon = -78 if lon is None else lon
            city = geolocator.reverse(str(lat)+','+str(lon))
        elif ctx.triggered_id == "search_days":
            search_days = 3 if search_days is None else search_days
        elif ctx.triggered_id == "low_tavg":
            low_tavg = 5 if low_tavg is None else low_tavg
        elif ctx.triggered_id == "high_tavg":
            high_tavg = 5 if high_tavg is None else high_tavg
        elif ctx.triggered_id == "delta_t_limit":
            delta_t_limit = 10 if delta_t_limit is None else delta_t_limit
        elif ctx.triggered_id =="precipitation_limit":
            precipitation_limit = 10 if precipitation_limit is None else precipitation_limit
        elif ctx.triggered_id == "snow_limit":
            snow_limit = 2 if snow_limit is None else snow_limit
        '''
        
        start = datetime.combine(date.today()+timedelta(days=1), datetime.min.time())
        end = datetime.combine(date.today()+timedelta(days=search_days), datetime.min.time())
        stations = Stations().inventory('daily', (start, end))
        avaliable_stations = stations.fetch()
        avaliable_contries = {}
        for val in avaliable_stations['country']:
            country = countries.get(alpha_2=val).name
            if country not in avaliable_contries:
                avaliable_contries[country] = 1
            else:
                avaliable_contries[country] += 1

        geolocator = Nominatim(user_agent="123")
        '''
        print("Number of weather stations with avaliable forecast data in each countries:")
        for key,val in avaliable_contries.items():
            print(key+": "+str(val))
        print()'''
        
        stations_now = stations.nearby(lat, lon, 300000)
        stations_now = stations_now.fetch()
        if stations_now.empty:
            print("Nearby weather stations do not provide forecasts for the next "+str(search_days)+" days.")
            
        id = stations_now.index.tolist()
        name = stations_now['name'].tolist()
        stations_lat = stations_now['latitude'].tolist()
        stations_lon = stations_now['longitude'].tolist()
        good_stations = []
        good_prcp =  []
        good_delta = []
        good_tavg = []
        good_snow = []
        good_stations_lat = []
        good_stations_lon = []

        for i, station in enumerate(id):
            data = Daily(station, start, end).fetch()
            if len(data)<search_days:
                continue
            total_prcp = 0
            total_snow = 0
            tavg = 0
            delta_t = 0
            goodData = True

            cal = 0
            for val in data['prcp']:
                if math.isnan(val):
                    continue
                cal += 1
                total_prcp += val
            if not cal == 0:
                if not total_prcp == 0:
                    total_prcp = total_prcp/cal
            else:
                goodData = False

            cal = 0
            for val in data['snow']:
                cal += 1
                if math.isnan(val):
                    total_snow += 0
                    continue
                total_snow += val
            if not cal == 0:
                total_snow = total_snow / cal

            cal = 0
            for val in data['tavg']:
                if math.isnan(val):
                    continue
                cal += 1
                tavg += val
            if not cal == 0:
                if not tavg == 0:
                    tavg = tavg/cal
            else:
                goodData = False

            cal = 0
            for (val1, val2) in zip(data['tmin'], data['tmax']):
                if math.isnan(val1) or math.isnan(val2):
                    break
                cal += 1 
                delta_t += (val2 - val1)
            if not cal == 0:
                if not delta_t == 0:
                    delta_t = delta_t/cal
            else:
                goodData = False

            if goodData and total_prcp <= precipitation_limit:
                if delta_t <= delta_t_limit:
                    if total_snow <= snow_limit:
                        if (tavg <= high_tavg) and (tavg >= low_tavg):
                            good_prcp.append(total_prcp)
                            good_snow.append(total_snow)
                            good_delta.append(delta_t)
                            good_tavg.append(tavg)
                            good_stations.append(name[i])
                            good_stations_lat.append(stations_lat[i])
                            good_stations_lon.append(stations_lon[i])
            
        if not good_stations:
            print("No nearby weather stations satisfy the criteria.")
            no_station_found = True
            import pandas as pd
            import plotly.express as px
            px.set_mapbox_access_token('pk.eyJ1IjoidGhlb3NlcnlhdCIsImEiOiJjbHltcjd6OW0wNDNjMmtzNzdyODBrMjc0In0.b2oDRgrEUur1VqMNVSDPfA')
            #px.set_mapbox_access_token(open(".mapbox_token").read())

            df_map = pd.DataFrame()
            df_map['location'] = [city]
            df_map['lat'] = [lat]
            df_map['lon'] = [lon]
            df_map['description'] = ['your location']
            df_map['size'] = [6]
            '''
            MinX, MaxX = min(good_stations_lon), max(good_stations_lon)
            minY, maxY = min(good_stations_lat), max(good_stations_lat)
            MinY = minY - 0.05*(maxY - minY)
            MaxY = maxY + 0.05*(maxY - minY) '''

            map = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="location",
                                    size="size", hover_data={"size": False})
            map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            #map.update_layout(mapbox_bounds={"west": minX, "east": maxX, "south": MinY, "north":MaxY})
            df_map = df_map.drop(columns='size')
            print(df_map)
            lat = ("{:.1f}".format(lat))
            lon = ("{:.1f}".format(lon))
            return city, lat, lon, dbc.Table.from_dataframe(df_map), map, no_station_found, ' '

        else:    
            no_station_found = False
            print("Nearby weather stations with less than "+str(precipitation_limit)+"mm\nof total precipitation in the next "+str(search_days)+" days:")
            for station in good_stations:
                print(station)

            import plotly.express as px
            #import plotly.graph_objects as go
            px.set_mapbox_access_token('pk.eyJ1IjoidGhlb3NlcnlhdCIsImEiOiJjbHltcjd6OW0wNDNjMmtzNzdyODBrMjc0In0.b2oDRgrEUur1VqMNVSDPfA')
            #px.set_mapbox_access_token(open(".mapbox_token").read())

            df_map = pd.DataFrame()
            temp_list = location_formater(good_stations, good_stations_lat, good_stations_lon)
            df_map['lat'] = good_stations_lat
            df_map['lon'] = good_stations_lon
            df_map['location'] = temp_list
            df_map['prcp'] = good_prcp
            df_map['tavg'] = good_tavg
            df_map['delta_t'] = good_delta
            df_map['snow'] = good_snow
            df_map['size'] = [6]*df_map.shape[0]

            import pandas as pd
            filepath = 'informations/informations_2.csv'
            #df = pd.read_csv(filepath)
            test = WeatherRegression(filepath, 'Incidence', ['tavg', 'prcp', 'snow'])
            
            incidence_list = []
            happy_list = []
            for i in range(df_map.shape[0]):
                inc_pred, inc_avg, stk_score = test.stacking_app([df_map.loc[i, ['tavg', 'prcp', 'snow']]])
                incidence_list.append(float(inc_pred[0]))
                if float(inc_pred[0]) < inc_avg:
                    happy_list.append(':)')
                else:
                    happy_list.append(':(')
            '''
            MinX, MaxX = min(good_stations_lon), max(good_stations_lon)
            minY, maxY = min(good_stations_lat), max(good_stations_lat)
            MinY = minY - 0.05*(maxY - minY)
            MaxY = maxY + 0.05*(maxY - minY) '''
            round_df_map = df_map[['location', 'lon', 'lat', 'prcp', 'tavg', 'delta_t', 'snow', 'size']].round(decimals=2)
            round_df_map['mental_disease'] = incidence_list
            round_df_map['Happy?'] = happy_list
            round_df_map = round_df_map.round(decimals=4)
            map = px.scatter_mapbox(round_df_map, lat="lat", lon="lon", hover_name="location",
                                    size="size", hover_data={"size": False}, 
                                    color_continuous_scale=px.colors.sequential.Viridis_r,
                                    color="mental_disease", zoom=5)
            map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            #map.update_layout(mapbox_bounds={"west": minX, "east": maxX, "south": MinY, "north":MaxY})
            round_df_map = round_df_map.drop(columns='size')
            print(round_df_map)
            lat = ("{:.1f}".format(lat))
            lon = ("{:.1f}".format(lon))
            return city, lat, lon, dbc.Table.from_dataframe(round_df_map), map, no_station_found, ' '

def location_formater(good_stations, good_stations_lat, good_stations_lon):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="123")
    good_cities = []
    for i in range(len(good_stations)):
        location = geolocator.reverse(str(good_stations_lat[i])+','+str(good_stations_lon[i]))
        if location is None:
            good_cities.append(good_stations[i])
            continue

        good_addr = location.raw['address']   
        addr = good_addr.get('city','') + ', ' + good_addr.get('suburb', '')
        if addr.endswith(' ') or addr.startswith(','):
            addr = addr.strip(', ')
            addr = addr.strip(',')
        if len(addr) <= 1:
            addr = good_stations[i]
        good_cities.append(addr)
        
    return good_cities

if __name__ == "__main__":
    #app.run_server(debug=True)
    app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)