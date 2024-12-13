import copy
import plotly.graph_objects as go

from dash import Dash, html, ctx
import dash_cytoscape as cyto
import json
import yaml
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output


DQ_color_dict = {0: '#3DBDFF',
                 1: '#8282E9',
                 2: '#C425D2',
                 3: '#200E78',
                 4: '#4239FA',
                 5: '#2439D7',
                 6: '#50C7FF',
                 7: '#9291E8',
                 8: '#15104D',
                 9: '#A6A3E7',
                 10: '#9D40F1',
                 11: '#B93CD3',
                 12: '#FA6BE2',
                 13: '#C842F6',
                 14: '#2D166C',
                 15: '#FE82EE',
                 16: '#2A46E5',
                 17: '#A22DF0',
                 18: '#AA175E',
                 19: '#4B3DF9',
                 20: '#C840D2',
                 21: '#220E79',
                 22: '#4E3BFC',
                 23: '#45C9FF',
                 24: '#8D30F0',
                 25: '#70194F',
                 26: '#29A7DB',
                 27: '#4128F8',
                 28: '#B6B3E6',
                 29: '#670D53',
                 30: '#8A8AE8',
                 31: '#99145E',
                 32: '#7C7EDA',
                 -1: 'grey',
                 -2: 'white'}


with open("data/topic_elm_list.json", "r") as f:
    startup_elms = json.load(f)
startup_elm_list = startup_elms["elm_list"]

with open("data/topics.json", "r") as f:
    lda_topics = json.load(f)

with open("data/filter_token_hist.json", "r") as f:
    filter_token_hist_dict = json.load(f)

topics_txt = [lda_topics[str(i)] for i in range(len(lda_topics))]
topic_weight_tuple_list = [[(j.split("*")[1].replace('"', ""), j.split("*")[0]) for j in i['weight_token']]
                           for i in topics_txt]

# token_weight_tuple_list = [[(j.split("*")[1].replace('"', ""), j.split("*")[0]) for j in i] for i in topics_txt]

def get_node_data(node_data):
    node_idx = node_data[0]['id']
    job_title = node_data[0]['filter']
    topic_idx = node_data[0]['topic_idx']
    topic_color = node_data[0]['color']
    return node_idx, job_title, topic_idx, topic_color

def get_node_topic_data(scatter_node_data, network_node_data, triggered_id):
    if triggered_id is None:
        return (None, None)
    elif triggered_id=='cytoscape_network':
        node_idx, topic_idx, topic_color = get_network_node_data(network_node_data)
    elif triggered_id=='cytoscape_core':
        node_idx, job_title, topic_idx, topic_color = get_node_data(scatter_node_data)

    print("node_idx: {}".format(node_idx))
    print("topic_idx: {}".format(topic_idx))
    print("topic_color: {}".format(topic_color))
    return topic_idx, topic_color, node_idx


def get_network_node_data(node_data):
    node_idx = node_data[0]['id']
    topic_idx = node_data[0]['topic_idx']
    topic_color = node_data[0]['color']
    return node_idx, topic_idx, topic_color

def generate_topic_bar_graph(topic_idx, color='rgb(248, 248, 249)'):
    topic_list = [temp[0] for temp in topic_weight_tuple_list[topic_idx]]
    weight_list = [float(temp[1]) for temp in topic_weight_tuple_list[topic_idx]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
                x=weight_list[::-1], y=topic_list[::-1],
                orientation='h',
                marker_color=color
            ))

    return fig


def generate_topic_bar_pie_graph(topic_idx, color):
    token_list = [temp_tuple[0] for temp_tuple in topic_weight_tuple_list[topic_idx]]
    weight_list = [float(temp_tuple[1]) for temp_tuple in topic_weight_tuple_list[topic_idx]]

    fig = make_subplots(1, 2,
                        specs=[[{'type': 'xy'}, {"type": "xy"}],
                               ],
                        horizontal_spacing=0.1  # Adjust the vertical spacing here

                        )

    fig.add_trace(go.Bar(
        x=token_list,
        y=weight_list* 100,
        marker_color=color,
        # marker_line_color='black',
    ), row=1, col=1
    )

    # TODO: KeyError: '-2'
    job_title_index = lda_topics[str(topic_idx)]['filter_index']
    job_title_value = lda_topics[str(topic_idx)]['filter_value']
    job_title_pie_colors = [color for _ in range(len(job_title_index))]

    total_count = sum(job_title_value)
    job_title_ratio = [elem/total_count*100 for elem in job_title_value]

    fig.add_trace(go.Bar(
        x=job_title_index,
        y=job_title_ratio,
        marker_color=color,
    ), row=1, col=2
    )

    fig.update_layout(
        height=200,
        showlegend=False,
        margin=dict(l=75, r=75, t=25, b=25),
        xaxis_tickangle=-45,
        plot_bgcolor='white'
    )

    fig.update_xaxes(title_text="Weight of tokens in topic {}".format(topic_idx), tickfont=dict(size=12), row=1, col=1)
    fig.update_xaxes(title_text="Percentage of subjects in topic {}".format(topic_idx), tickfont=dict(size=12), row=1, col=2)

    fig.update_yaxes(title_text="Token weight", row=1, col=1, automargin=True, title_standoff=5)
    fig.update_yaxes(title_text="[%]", row=1, col=2, automargin=True, title_standoff=5)

    return fig



def generate_filter_bar_graph(filter_idx):
    token_list = list(filter_token_hist_dict[filter_idx].keys())
    token_count_list = list(filter_token_hist_dict[filter_idx].values())

    print(token_list)
    print(token_count_list)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=token_list,
        y=token_count_list,
        marker_color='grey',
        # marker_line_color='black',
    )
    )

    fig.update_layout(
        height=200,
        showlegend=False,
        margin=dict(l=75, r=75, t=25, b=25),
        xaxis_tickangle=-45,
        plot_bgcolor='white'
    )

    fig.update_xaxes(title_text="Tokens", tickfont=dict(size=12))
    fig.update_yaxes(title_text="Token count", automargin=True, title_standoff=5)


    return fig


def jobtopic_bar_pie_factory(topic_idx, topic_color):
    if topic_idx is None:
        return generate_topic_bar_pie_graph(0, DQ_color_dict[0])

    return generate_topic_bar_pie_graph(topic_idx, topic_color)



with open('data/topic_color.txt') as f:
    lines = f.readlines()
topic_color = [line.rstrip('\n') for line in lines]



def_stylesheet = [
    {
        "selector": "node",
        "style": {
            "width": "data(node_size)",
                  "height": "data(node_size)",
                  "width": 0.5,
                  "height": 0.5,
                  'background-color': 'data(color)',
                  'opacity': 0.5,
                  'font-size': '1px'
                  }
    },
]

with open("data/token_network_elm_list.json", "r") as f:
    startup_network_elms = json.load(f)
startup_network_elm_list = startup_network_elms["elm_list"]


def_stylesheet_network = [
    {
        "selector": "node",
        "style": {
                  "width": "data(node_size)",
                  "height": "data(node_size)",
                  'background-color': "data(color)",
                  "border-color": "black",
                  "border-opacity": "1",
                  "border-width": 0.1,
                  "label": "data(name)",
                  'opacity': 0.35,
                  'font-size': 1,
                  # 'text-opacity': 0.75
                  }
    },
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier',
             'width': "data(edge_weight)",
            'opacity': 0.25,
        }
    },
]



col_swatch = px.colors.qualitative.Dark24

def take_dict_value(key, dictionary):
    try:
        return dictionary[key]
    except:
        return key

app = Dash(__name__)



app.layout = html.Div([
    dbc.Row([
        dbc.Col([
            cyto.Cytoscape(
                    id='cytoscape_network',
                    layout={'name': 'preset'},
                    style={'width': '100%', 'height': '400px'},
                    elements=startup_network_elm_list,
                    # elements=[],
                    stylesheet=def_stylesheet_network,
                ),
            

        ]), 
    ]), 

    dbc.Row([
        dcc.Graph(
                                    figure=jobtopic_bar_pie_factory(topic_idx=0, topic_color=DQ_color_dict[0]),
                                    id='topic_bar_pie'
                                )
    ]),

    dbc.Row([
        cyto.Cytoscape(
            id='cytoscape_core',
            layout={'name': 'preset'},
            style={'width': '100%', 'height': '400px'},
            elements=startup_elm_list,
            # elements=[],
            stylesheet=def_stylesheet,
        ),
    ]),

dbc.Row(
                            [
                                dbc.Alert(
                                    id="node-data",
                                    children="Click on a node to see its details here",
                                    color="secondary",
                                )
                            ]
                        ),

])



@app.callback(
            Output('cytoscape_core', 'stylesheet',),
            [
                Input("cytoscape_core", "selectedNodeData"),
                # Input("topic_weight_bar", "clickData")
            ],
              )
def generate_stylesheet(node_data,
                        # click
                        ):

    if node_data is None or len(node_data)==0:
        return def_stylesheet

    updated_stylesheet = copy.deepcopy(def_stylesheet)

    # node_annot_text = "Subject: {}\nTokens: {}".format(
    #     node_data[0]['filter'],
    #     node_data[0]['token_bow']
    # )

    node_annot_text = "Subject: {}".format(
        node_data[0]['filter'],
    )

    selected_node_idx, selected_job_title, selected_topic_idx, selected_topic_color = get_node_data(node_data)

    updated_stylesheet.append({
        # "selector": 'node[id = "{}"]'.format(node[0]['id']),
        "selector": 'node[topic_idx = {}]'.format(selected_topic_idx),
        "style": {
            # 'background-color': '#B10DC9',
            # "border-color": "black",
            "border-opacity": 0,
            "opacity": 1,
            # "label": "data(label)",
            # "label": node_annot_text,
            "color": "black",
            "text-opacity": 0.8,
            "font-size": 5,
            'z-index': 9999,
            "text-wrap": "wrap"
        }
    }
    )

    updated_stylesheet.append({
        "selector": 'node[id = "{}"]'.format(selected_node_idx),
        "style": {
            # 'background-color': '#B10DC9',
            "border-color": "black",
            "border-width": 0.1,
            "border-opacity": 1,
            "opacity": 1,
            # "label": "data(label)",
            "label": node_annot_text,
            "color": "black",
            "text-opacity": 0.8,
            "font-size": 5,
            'z-index': 9999,
            "text-wrap": "wrap"
        }
    }
    )

    return updated_stylesheet




@app.callback(
            Output('cytoscape_network', 'stylesheet'),
            [
                Input("cytoscape_network", "selectedNodeData"),
            ],
              )
def generate_network_stylesheet(network_node_data,):
    if network_node_data is None or len(network_node_data)==0:
        return def_stylesheet_network

    updated_network_stylesheet = copy.deepcopy(def_stylesheet_network)

    node_idx, topic_idx, topic_color = get_network_node_data(network_node_data)

    updated_network_stylesheet.append({
        "selector": 'node[id = "{}"]'.format(node_idx),
        "style": {
            # 'background-color': '#B10DC9',
            "border-color": "black",
            "border-width": 0.1,
            "border-opacity": 1,
            "opacity": 1,
            "color": "black",
            "text-opacity": 0.8,
            "font-size": 1,
            'z-index': 9999,
            "text-wrap": "wrap"
        }
    }
    )

    updated_network_stylesheet.append({
        "selector": 'edge[source = "{}"]'.format(node_idx),
        "style": {
            "line-color": 'red',
            'opacity': 1,
            'font-size': 1,
            'z-index': 5000
        }
    }
    )

    updated_network_stylesheet.append({
        "selector": 'edge[target = "{}"]'.format(node_idx),
        "style": {
            "line-color": 'red',
            'opacity': 1,
            'font-size': 1,

            'z-index': 5000
        }
    }
    )

    return updated_network_stylesheet

@app.callback(
    Output("topic_bar_pie", "figure"),
    [
        Input("cytoscape_core", "selectedNodeData"),
        Input("cytoscape_network", "selectedNodeData")
     ]
)
def update_topic_bar_pie_chart(scatter_node_data, network_node_data):
    # from .models import jobtopic_bar_pie_factory, get_node_topic_data
    def jobtopic_bar_pie_factory(topic_idx, topic_color):
        if topic_idx is None:
            # return generate_topic_bar_pie_graph(0, DQ_color_dict[0])
            return go.Figure()

        return generate_topic_bar_pie_graph(topic_idx, topic_color)

    triggered_id = ctx.triggered_id

    if triggered_id=='cytoscape_network' and (network_node_data is None or len(network_node_data)==0):
        return go.Figure()

    elif triggered_id=='cytoscape_core' and (scatter_node_data is None or len(scatter_node_data)==0):
        return go.Figure()

    topic_idx, topic_color, node_idx = get_node_topic_data(scatter_node_data, network_node_data, triggered_id)

    if topic_idx==-1:
        print("Checkpoint")

        return generate_filter_bar_graph(node_idx)

    return jobtopic_bar_pie_factory(topic_idx, topic_color)

@app.callback(
    Output("node-data", "children"), [Input("cytoscape_core", "selectedNodeData")]
)
def display_nodedata(datalist):

    contents = "Click on a node to see its details here"
    if datalist is None or len(datalist)==0:
        return contents


    subject = datalist[0]['filter']
    text = datalist[0]['text']
    bow = datalist[0]['token_bow']

    profile_description_split = text.split('\n')

    contents = []
    contents.append(html.H3("Subject: {}".format(subject)))

    for line_split in profile_description_split:
        contents.append(html.P(line_split))
    contents.append(html.H3("Tokens: {}".format(bow)))
    return contents

if __name__ == '__main__':
    app.run_server(debug=True)