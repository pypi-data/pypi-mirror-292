import pandas as pd
import networkx as nx


class GraphBuilder:
    def __init__(self):
        """
        Initializes an empty graph.
        """
        self.graph = nx.Graph()

    def build_graph(self, df):
        """
        Builds a graph from the DataFrame containing the concepts and relationships.

        Args:
            df (pd.DataFrame): DataFrame containing the nodes and edges.

        Returns:
            nx.Graph: A NetworkX graph object.
        """
        nodes = pd.concat([df['node_1'], df['node_2']], axis=0).unique()
        for node in nodes:
            self.graph.add_node(str(node))

        for _, row in df.iterrows():
            self.graph.add_edge(
                str(row["node_1"]),
                str(row["node_2"]),
                title=row["edge"],
                weight=row['count'] / 4
            )
        return self.graph

    def add_contextual_proximity(self, df):
        """
        Adds edges based on contextual proximity between nodes.

        Args:
            df (pd.DataFrame): DataFrame containing the nodes and chunk metadata.

        Returns:
            pd.DataFrame: DataFrame with additional edges based on proximity.
        """
        dfg_long = pd.melt(
            df, id_vars=["chunk_id"], value_vars=["node_1", "node_2"], value_name="node"
        )
        dfg_wide = pd.merge(dfg_long, dfg_long, on="chunk_id", suffixes=("_1", "_2"))
        self_loops_drop = dfg_wide[dfg_wide["node_1"] == dfg_wide["node_2"]].index
        dfg_wide.drop(index=self_loops_drop, inplace=True)
        dfg_wide["edge"] = "contextual proximity"
        return dfg_wide[dfg_wide["count"] != 1]

    def detect_communities(self):
        """
        Detects communities within the graph using the Girvan-Newman algorithm.

        Returns:
            list: A list of communities, each community is a list of nodes.
        """
        communities_generator = nx.community.girvan_newman(self.graph)
        return sorted(map(sorted, next(communities_generator)))
