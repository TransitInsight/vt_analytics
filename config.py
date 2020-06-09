#import preprocessing
import plotly.io as pio

'''Default template: 'plotly'
Available templates:
    ['ggplot2', 'seaborn', 'simple_white', 'plotly',
        'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
        'ygridoff', 'gridon', 'none']'''
pio.templates.default = "plotly"

ElasticSearchDS = {
    "in_memory": True,
    "host": "windows2019",
    "port": "9200",
    "sqlurl": "http://windows2019:9200/_xpack/sql",
}


es_fetch_size = 5000


vobc_fault_color_dict = {
    -1: "#074263", 
    1: "#0B5394", 
    2: "#3D85C6", 
    3: "#6D9EEB", 
    4: "#A4C2F4",
    5: "#AFA223", 
    6: "#5B0F00", 
    7: "#85200C", 
    8: "#A61C00", 
    9: "#CC4125", 
    10: "#DD7E6B", 
    11: "#E6B8AF", 
    12: "#F8CBAD", 
    13: "#F4CCCC", 
    14: "#274E13", 
    15: "#38761D", 
    16: "#E06666", 
    17: "#CC0000", 
    18: "#20124D"}

def get_fault_color(faultCode):
    return vobc_fault_color_dict[faultCode]

vobc_fault_marker_color_dict = {
    False: "grey", 
    True: "green" 
}
def get_fault_marker_color(apstat):
    return vobc_fault_marker_color_dict[apstat]

vobc_fault_name_dict = {
    -1: '00. All',
    1: '01. Passenger Alarm',
    2: '02. FAR Level 2 Fault',
    3: '03. FAR Level 3 Fault',
    4: '04. Failed to Dock',
    5: '05. Dynamic Brake Failure',
    6: '06. Converter Failure',
    7: '07. FAR Level 1 Fault',
    8: '08. Train Overspeed',
    9: '09. Target Point Overshoot',
    10: '10. Rollback',
    11: '11. V = 0 Failure',
    12: '12. Obstruction in AUTO Mode',
    13: '13. EB Test Failure',
    14: '14. Power Deselect Failure',
    15: '15. Loss of Door Closed Status'}
