import dash
import dash_core_components as dcc
import dash_cytoscape as cyto
import dash_html_components as html
import networkx as nx
import itertools
import community as community_louvain
from cytoscape_generator import gen_cy_pos, gen_cy_data


G = nx.karate_club_graph()
ev_centrality = nx.algorithms.centrality.eigenvector_centrality(G)
d_centrality = nx.algorithms.centrality.degree_centrality(G)
bw_centrality = {frozenset(k):v for k,v in nx.algorithms.centrality.edge_betweenness_centrality(G).items()}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(["Layout:",
              dcc.Dropdown(id='layout-input',
                        options=[
                            {'label':'Spring','value':'spring'},
                            {'label':'Circular','value':'circular'},
                            {'label':'Kamada Kawai','value':'kamada_kawai'}],
                        value='spring')]),
    html.Div(["Community Detection:",
              dcc.Dropdown(id='algorithm-input',
                           options=[
                               {'label':'Girvan Newman','value':'gn'},
                               {'label':'Ground Truth','value':'gt'},
                               {'label':'Label Propogation','value':'lp'},
                               {'label':'Louvain','value':'lv'}],
                           value='gt')]),
    html.Div(["Partition:",
              dcc.Slider(id='step-slider',
                         min=0,
                         max=5,
                         value=0,
                         marks={0:'ground truth',2:'2',3:'3',4:'4',5:'5'})],
              style={'display':'none'},
              id='step-div'),
    cyto.Cytoscape(
        id='cytoscape',
        zoom=0,
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '700px'}),
    html.P(id='cytoscape-mouseoverNodeData-output'),
    html.P(id='cytoscape-mouseoverEdgeData-output')
])

@app.callback(
        [dash.dependencies.Output('cytoscape','elements'),
         dash.dependencies.Output('cytoscape','stylesheet'),
         dash.dependencies.Output('step-div','style')],
        [dash.dependencies.Input('layout-input','value'),
        dash.dependencies.Input('algorithm-input','value'),
        dash.dependencies.Input('step-slider','value')])
def update_elements(layout_value,algorithm_value,step_value):
    stylesheet = [
            {'selector': 'node',
             'style': {'content': 'data(label)'}},
            {'selector':'.R',
             'style': {'background-color':'red'}},
            {'selector':'.B',
             'style': {'background-color':'blue'}},
            {'selector':'.G',
             'style': {'background-color':'green'}},
            {'selector':'.Y',
             'style': {'background-color':'yellow'}},
            {'selector':'.O',
             'style': {'background-color':'orange'}},
            ]

    pos_data = gen_cy_pos(G, layout_value)
    step = None

    if algorithm_value == 'gn':
        comp = nx.algorithms.community.centrality.girvan_newman(G)
        limited = itertools.takewhile(lambda c: len(c) <= step_value, comp)
        cc = None
        for communities in limited:
            cc = list(sorted(c) for c in communities)
        step = {'display':'block'}

    elif algorithm_value == 'lp':
        cc = [list(i) for i in nx.algorithms.community.label_propagation.label_propagation_communities(G)]

    elif algorithm_value == 'lv':
        partition = community_louvain.best_partition(G)
        cc = [[] for i in set(partition.values())]
        for k,v in partition.items():
            cc[v].append(k)
    else:
        # Ground truth case
        cc = None

    step = {'display':'none'} if step is None else step

    return gen_cy_data(G, pos_data, cc),  stylesheet, step

@app.callback(dash.dependencies.Output('cytoscape-mouseoverNodeData-output', 'children'),
              dash.dependencies.Input('cytoscape', 'mouseoverNodeData'))
def displayTapNodeData(data):
    if data:
        node_id = int(data['label'][:-3])
        deg_str = ', Degree Centrality: ' + str(d_centrality[node_id])
        ev_str = ', Eigenvector Centrality: ' + str(ev_centrality[node_id])
        return "Node: " + data['label'] + deg_str + ' ' + ev_str 


@app.callback(dash.dependencies.Output('cytoscape-mouseoverEdgeData-output', 'children'),
              dash.dependencies.Input('cytoscape', 'mouseoverEdgeData'))
def displayTapEdgeData(data):
    if data:
        edge_id = frozenset([int(data['source'].upper()), int(data['target'].upper())])
        bw_str = ', Betweenness Centrality: ' + str(bw_centrality[edge_id])
        return "Edge: " + str(list(edge_id)) + bw_str



if __name__ == '__main__':
    app.run_server(debug=True)
