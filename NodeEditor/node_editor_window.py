from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_scene import Scene
from node_node import Node
from node_edge import Edge, EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT
from node_graphics_view import QDMGraphicsView

class NodeEditorWindow(QWidget):
    
    def __init__(self, parent=None, window_width=1600, window_height=900):
        super().__init__(parent)

        self.styleSheet_filename = 'qss/nodestyle.qss'
        self.loadStyleSheet(self.styleSheet_filename)

        self.init_UI(window_width, window_height)

    def init_UI(self, window_width, window_height):
        self.setGeometry(0, 0, window_width, window_height)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # create grapchics scene
        # self.grScene = QGraphicsScene()
        # self.grScene = QDMGraphicsScene()
        self.scene = Scene()
        # self.grScene = self.scene.grScene

        self.addNodes()

        # create grapchics view
        # self.view = QGraphicsView(self)
        # self.view.setScene(self.grScene)
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle('Node Editor')
        self.show()


        # self.addDebutContent()

    def addNodes(self):
        node1 = Node(self.scene, "My Awesome Nodes 1", inputs=[0, 2, 3], outputs=[1])
        node2 = Node(self.scene, "My Awesome Nodes 2", inputs=[0, 4, 5], outputs=[1])
        node3 = Node(self.scene, "My Awesome Nodes 3", inputs=[0, 0, 2], outputs=[1])
        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -150)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[0], edge_type=EDGE_TYPE_BEZIER)
        edge1 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=EDGE_TYPE_BEZIER)

    def addDebutContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.grScene.addText("This is my Awesome test!", QFont('Arial'))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))


        widget1 = QPushButton("Hello World")
        proxy1 = self.grScene.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)

        widget2 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)


        line = self.grScene.addLine(-100, -100, 400, -200, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsSelectable)
        line.setFlag(QGraphicsItem.ItemIsMovable)

    def loadStyleSheet(self, filename):
        print('STYLE loading', filename)
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))



