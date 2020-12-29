import networkx as nx

def gen_cy_pos(graph, layout='circular'):
    layout_mapping = {'circular': nx.circular_layout,
                      'kamada_kawai': nx.kamada_kawai_layout,
                      'spring': nx.spring_layout}
    pos = layout_mapping[layout](graph,scale=500,seed=52) if layout == 'spring' else \
          layout_mapping[layout](graph,scale=500)
    return pos

def gen_cy_data(graph, pos,community_classification=None):
    colors = ['R','B','G','Y','O']
    class_mapping = {'Mr. Hi':'R','Officer':'B'}
    if community_classification is not None:
        community_classification.sort()
        comm_mapping = {i:colors[e_idx] for e_idx,e in enumerate(community_classification)
                                        for i in e}
     
    cy = nx.readwrite.json_graph.cytoscape_data(graph)
    for v in cy['elements']['nodes']:
        v['data']['label'] = v['data'].pop('name') 
        v['classes'] = class_mapping[v['data']['club']] if community_classification is None else \
                        comm_mapping[v['data']['value']]
        v['data']['label'] = v['data']['label'] + '(' + v['classes'] + ')'
        v['position'] = {'x': pos[int(v['data']['id'])][0],
                         'y': pos[int(v['data']['id'])][1]}
    element_list = cy['elements']['nodes'].copy()
    element_list.extend(cy['elements']['edges'])
    
    return element_list

