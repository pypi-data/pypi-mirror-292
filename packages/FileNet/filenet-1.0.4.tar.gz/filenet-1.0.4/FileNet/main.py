import os
import networkx as nx
import matplotlib.pyplot as plt
import pprint
import plotly.graph_objects as go
import platform

main_dict = {}
pp = pprint.PrettyPrinter(indent=4)
G = nx.DiGraph()

# start_path = '/Users/aditya.narayan/Desktop/test_dump'

def hello():
    print('FileNet successfully installed')

def get_os():
    os_name = platform.system()
    
    if os_name == "Darwin":
        return "macOS"
    elif os_name == "Windows":
        return "Windows"
    else:
        return "Other"

def draw2D(start_path, theme=4):
    '''
    FileNet draw2D is a library used to visualize the Root(Directory), Directory, Files and their connections.
    The functions take two parameters.
    1. start_path : Take path in str format, assigned path is considered as root dir.
    2. theme : Default theme=4, theme range can be from 1 to 4. 
    '''
    if get_os == "macOS":
        start_path = start_path
    if get_os == "Windows":
        start_path = start_path.replace("\\", "/")

    for count, (dirpath, dirnames, filenames) in enumerate(os.walk(start_path)):
        main_dict[f'{count}'] = {f'{dirpath.split('/')[-1]}':{'dir':[],'files':[]}}

        if dirnames:
            for dirname in dirnames:
                main_dict[f'{count}'][f'{dirpath.split('/')[-1]}']['dir'].append(dirname)
        
        if filenames:
            for filename in filenames:
                main_dict[f'{count}'][f'{dirpath.split('/')[-1]}']['files'].append(filename)

    # pp.pprint(main_dict)

    for i in range(len(main_dict)):
        if f'{i}' == 0:
            G.add_node(next(iter(main_dict[f'{i}'])))

            if main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['dir']:
                for dir in main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['dir']:
                    G.add_node(dir, color='blue')
                    G.add_edge(next(iter(main_dict[f'{i}'])), dir)

            if main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['files']:
                for file in main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['files']:
                    G.add_node(file, color='pink')
                    G.add_edge(next(iter(main_dict[f'{i}'])), file)

        else:
            if main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['dir']:
                for dir in main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['dir']:
                    G.add_node(dir, color='yellow')
                    G.add_edge(next(iter(main_dict[f'{i}'])), dir)

            if main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['files']:
                for file in main_dict[f'{i}'][next(iter(main_dict[f'{i}']))]['files']:
                    G.add_node(file, color='pink')
                    G.add_edge(next(iter(main_dict[f'{i}'])), file)


    for node in G.nodes:
        if 'color' not in G.nodes[node]:
            G.nodes[node]['color'] = 'gray' 

    colors = [G.nodes[node]['color'] for node in G.nodes]

    plt.figure(figsize=(12, 9))

    if theme == 1:
        pos = nx.spring_layout(G, seed=42, k=0.3, iterations=100)
    elif theme == 2: 
        pos = nx.circular_layout(G)
    elif theme == 3:
        pos = nx.kamada_kawai_layout(G,dist=(0.2,0.5))
    elif theme == 4:
        pos = nx.shell_layout(G, rotate=0)

    color_labels = {
        'Gray': 'Root (Directory)',
        'Yellow': 'Directory',
        'Pink': 'File'
    }
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', label=label, 
                                markersize=10, markerfacecolor=color) 
                    for color, label in color_labels.items()]
    plt.legend(handles=legend_handles, loc='best', title='Legend')

    nx.draw_networkx(G, pos, with_labels=True, node_color=colors, font_weight='bold', node_size=2000, font_size=10, edge_color='gray')
    plt.title(start_path.split('/')[-1]+' Connection Diagram')
    plt.text(0.0, -0.01, "NOTE :", transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.0, -0.05, "Press 'Q'/'q' to close FileNet window", transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')

    # return plt.show(block=False)
    print("Output Generated, check file with namd 'directory_layout.png'")
    return plt.savefig('directory_layout.png')


def draw3D(start_path):
    '''
    FileNet draw3D is a library used to visualize the Root(Directory), Directory, Files and their connections.
    The function takes one parameter.
    1. start_path : Take path in str format, assigned path is considered as root dir.
    '''

    if get_os() == "macOS":
        start_path = start_path
    elif get_os() == "Windows":
        start_path = start_path.replace("\\", "/")

    for count, (dirpath, dirnames, filenames) in enumerate(os.walk(start_path)):
        dir_name = os.path.basename(dirpath)

        # Add the directory as a node
        if dir_name not in G:
            if count == 0:
                G.add_node(dir_name, color='red', size=30)  # Root directory
            else:
                G.add_node(dir_name, color='yellow', size=20)  # Subdirectory

        # Add child directories and create edges
        for dirname in dirnames:
            if dirname not in G:
                G.add_node(dirname, color='yellow', size=20)  # Child directory
            G.add_edge(dir_name, dirname)

        # Add files and create edges
        for filename in filenames:
            if filename not in G:
                G.add_node(filename, color='pink', size=10)  # File
            G.add_edge(dir_name, filename)

    pos = nx.spring_layout(G, dim=3, seed=42)

    node_colors = [G.nodes[node].get('color', 'gray') for node in G.nodes]
    node_sizes = [G.nodes[node].get('size', 10) * 10 for node in G.nodes]

    edge_x = []
    edge_y = []
    edge_z = []
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None]) 
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=1, color='gray'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    node_z = []
    node_text = []
    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        node_text.append(node)

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        text=node_text,
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            color=node_colors,
            size=node_sizes,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=f'{start_path.split("/")[-1]} 3D Connection Diagram',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0,l=0,r=0,t=30),
                        annotations=[dict(
                            text="File Network Graph in 3D",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        scene=dict(
                            xaxis=dict(visible=False),
                            yaxis=dict(visible=False),
                            zaxis=dict(visible=False))
                    ))
    return fig.show()

def jsonPrint(start_path):
    '''
    FileNet draw2D is a library used to visualize the Root(Directory), Directory, Files and their connections.
    The functions take two parameters.
    Print JSON output of directory relations.
    1. start_path : Take path in str format, assigned path is considered as root dir.
    '''
    if get_os == "macOS":
        start_path = start_path
    if get_os == "Windows":
        start_path = start_path.replace("\\", "/")

    for count, (dirpath, dirnames, filenames) in enumerate(os.walk(start_path)):
        main_dict[f'{count}'] = {f'{dirpath.split('/')[-1]}':{'dir':[],'files':[]}}

        if dirnames:
            for dirname in dirnames:
                main_dict[f'{count}'][f'{dirpath.split('/')[-1]}']['dir'].append(dirname)
        
        if filenames:
            for filename in filenames:
                main_dict[f'{count}'][f'{dirpath.split('/')[-1]}']['files'].append(filename)

    pp.pprint(main_dict)


# draw2D(start_path,theme=1)
# draw3D(start_path)
# jsonPrint(start_path)