#import preprocessing
import plotly.io as pio

'''Default template: 'plotly'
Available templates:
    ['ggplot2', 'seaborn', 'simple_white', 'plotly',
        'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
        'ygridoff', 'gridon', 'none']'''
pio.templates.default = "plotly"

ElasticSearchDS = {
    "host": "win2019",
    "port": "9200",
    "sqlurl": "http://win2019:9200/_xpack/sql",
}


vobc_fault_color_dict = {
    '00': "#074263", 
    '01': "#0B5394", 
    '02': "#3D85C6", 
    '03': "#6D9EEB", 
    '04': "#A4C2F4",
    '05': "#CFE2F3", 
    '06': "#5B0F00", 
    '07': "#85200C", 
    '08': "#A61C00", 
    '09': "#CC4125", 
    '10': "#DD7E6B", 
    '11': "#E6B8AF", 
    '12': "#F8CBAD", 
    '13': "#F4CCCC", 
    '14': "#274E13", 
    '15': "#38761D", 
    '16': "#E06666", 
    '17': "#CC0000", 
    '18': "#20124D"}

es_fetch_size = 5000