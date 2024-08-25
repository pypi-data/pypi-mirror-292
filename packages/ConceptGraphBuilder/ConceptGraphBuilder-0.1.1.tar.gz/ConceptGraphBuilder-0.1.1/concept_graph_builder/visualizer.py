import seaborn as sns
from pyvis.network import Network
import random
import pandas as pd


class GraphVisualizer:
    def __init__(self, graph):
        """
        Initializes the GraphVisualizer with a NetworkX graph.
        """
        self.graph = graph

    def assign_colors(self, communities, palette="hls"):
        """
        Assigns colors to nodes based on their communities.

        Args:
            communities (list): A list of communities (each community is a list of nodes).
            palette (str): The color palette to use.

        Returns:
            pd.DataFrame: DataFrame containing nodes with their assigned colors and groups.
        """
        p = sns.color_palette(palette, len(communities)).as_hex()
        random.shuffle(p)
        rows = []
        group = 0
        for community in communities:
            color = p.pop()
            group += 1
            for node in community:
                rows.append({"node": node, "color": color, "group": group})
        return pd.DataFrame(rows)

    def add_node_attributes(self, colors_df):
        """
        Adds color and group attributes to nodes in the graph.

        Args:
            colors_df (pd.DataFrame): DataFrame containing nodes with their assigned colors and groups.
        """
        for _, row in colors_df.iterrows():
            self.graph.nodes[row['node']]['group'] = row['group']
            self.graph.nodes[row['node']]['color'] = row['color']
            self.graph.nodes[row['node']]['size'] = self.graph.degree[row['node']]

    def visualize_graph(self, output_file="graph.html"):
        """
        Visualizes the graph using PyVis and outputs it as an HTML file.

        Args:
            output_file (str): The output HTML file name.
        """
        net = Network(
            notebook=False,
            cdn_resources="remote",
            height="900px",
            width="100%",
        )
        net.from_nx(self.graph)
        net.show(output_file, notebook=False)
