This package includes 
the analysis of relationship between mental disease and weather 
and an application based on the trained ML model.

"mw_data_analysis" folder:
1. eda.py: containing the functions for EDA, ex. making pairplots and global map.
2. WeatherRegression.py: It is designed as a class for the reason that more ML method will be added. The stacking regressor used in the application and demo .ipynb file is here.
3. make_weather_history_data.py: used for fetching the global history weather data. It took hours to complete fetching weather data worldwide for the past dacade, so only run it when you need data for years not in range [2012 ~ 2021]
4. the weather data saved from running 3. and IHME disease statistics for training.(informations/, incidence/, prevalence/)
5. "app.py": This is an application making prediction with the Regression model 

"data_analysis_demo.ipynb": a jupyter notebook demostrating the exploratory data analysis of the mental disease data and history weather data, serving as interactive visualization UI.