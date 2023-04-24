import json
from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_scene import QDMGraphicsScene
from node_node import Node
from node_edge import Edge
from node_scene_history import SceneHistory


class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width = 32000 
        self.scene_height = 32000

        self.init_UI()
        self.history = SceneHistory(self)

    def init_UI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)


    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)        

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        self.edges.remove(edge)

    def clear(self):
        while len(self.nodes)>0:
            self.nodes[0].remove()

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            json.dump(self.serialize(), file,indent=4)
        print('saveing to', filename, 'was successfull.')

    def loadFromFile(self, filename):
        with open(filename, "r", encoding='utf-8') as file:
            # raw_data = file.read()
            data = json.load(file)
            self.deserialize(data)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())

        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges)
        ])
    
    def deserialize(self, data, hashmap={}):
        self.clear()

        hashmap = {}

        # create nodes
        for node_data in data['nodes']:
            Node(self).deserialize(node_data, hashmap)

        # create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap)

        
        return True