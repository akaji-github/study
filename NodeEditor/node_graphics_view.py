from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge
from node_edge import Edge, EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT


DEBUG = True

MODE_NOOP = 1
MODE_EDGE_DRAG = 2

EDGE_DRAG_START_THRESHOLD = 10

class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene

        self.init_UI()

        self.setScene(self.grScene)

        self.mode = MODE_NOOP
        self.editingFlag = False

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [1, 10]

    def init_UI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.grScene.scene.history.storeHistory("Initialize")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.middleMouseBottonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseBottonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseBottonPress(event)
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.middleMouseBottonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseBottonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseBottonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseBottonPress(self, event):
        if DEBUG: print("MMB pressed")
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)
    
    def middleMouseBottonRelease(self, event):
        if DEBUG: print("MMB release")
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & -Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)


    def leftMouseBottonPress(self, event):

        item = self.getItemAtClick(event)

        self.last_mouse_button_click_scene_pos = self.mapToScene(event.pos())

        # if DEBUG: print('LMB Click on', item, self.debug_modifiers(event))

        # logic
        if hasattr(item, 'node') or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return
        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                return
            
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return res 
        
        super().mousePressEvent(event)
    
    def leftMouseBottonRelease(self, event):
        # get item which we clicked on
        item = self.getItemAtClick(event)

        # logic
        if hasattr(item, 'node') or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return
            
        if self.mode == MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return res 

        if self.dragMode() == QGraphicsView.RubberBandDrag:
            self.grScene.scene.history.storeHistory("Selection changed")

        super().mouseReleaseEvent(event)

    def rightMouseBottonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)
        if DEBUG: 

            if isinstance(item, QDMGraphicsEdge): 
                print('RMB DEBUG:', item.edge, 'connecting sockets:',
                       item.edge.start_socket, '<-->', item.edge.end_socket)

            if type(item) is QDMGraphicsSocket: 
                print('RMB DEBUG:', item.socket, 'has edge:', item.socket.edge)
                

            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes: print('    ', node)
                print('  Edges:')
                for edge in self.grScene.scene.edges: print('    ', edge)

    
    def rightMouseBottonRelease(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.grEdge.update()


        self.last_scene_mouse_position = self.mapToScene(event.pos())

        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()),
            int(self.last_scene_mouse_position.y())
        )
        super().mouseMoveEvent(event)

    def debug_modifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT"
        if event.modifiers() & Qt.ControlModifier: out += "CTRL"
        if event.modifiers() & Qt.AltModifier: out += "ALT"
        return out 
    
    def getItemAtClick(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj
    
    def edgeDragStart(self, item):
        if DEBUG: print('View::edgeDragStart ~ Start dragging edge')
        if DEBUG: print('View::edgeDragStart ~   assign start socket to', item.socket)
        self.previousEdge = item.socket.edge
        self.last_start_socket = item.socket
        self.dragEdge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        if DEBUG: print('View::edgeDragStart ~   dragEdge:', self.dragEdge)

            
    def edgeDragEnd(self, item):
        self.mode = MODE_NOOP

        if type(item) is QDMGraphicsSocket:
            if item.socket != self.last_start_socket:
                if DEBUG: print('View::edgeDragEnd ~   previous edge:', self.previousEdge)
                if item.socket.hasEdge():
                    item.socket.edge.remove()
                if DEBUG: print('View::edgeDragEnd ~   assign end socket')
                if self.previousEdge is not None: self.previousEdge.remove()
                if DEBUG: print('View::edgeDragEnd ~   previoous edge removed')
                self.dragEdge.start_socket = self.last_start_socket
                self.dragEdge.end_socket = item.socket
                self.dragEdge.start_socket.setConnectedEdge(self.dragEdge)
                self.dragEdge.end_socket.setConnectedEdge(self.dragEdge)
                if DEBUG: print('View::edgeDragEnd ~   assigned start & end sockets to drag edge')
                self.dragEdge.updatePositions()
                self.grScene.scene.history.storeHistory("Create new edge by dragging")
                return True
        
        if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
        self.dragEdge.remove()
        self.dragEdge = None
        if DEBUG: print('View::edgeDragEnd ~ about to set socket to preivous edge:', self.previousEdge)
        if self.previousEdge is not None:
            self.previousEdge.start_socket.edge = self.previousEdge
        if DEBUG: print('View::edgeDragEnd ~ everything done.')

    def distanceBetweenClickAndReleaseIsOff(self, event):
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_mouse_button_click_scene_pos        
        return (dist_scene.x()**2 + dist_scene.y()**2) > EDGE_DRAG_START_THRESHOLD**2
        
    def wheelEvent(self, event: QWheelEvent) -> None:
        # calculate our zoom factor
        zoomOutFactor = 1 / self.zoomInFactor
        
        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.saveToFile('graph.json.txt')
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.loadFromFile('graph.json.txt')
        # elif event.key() == Qt.Key_1:
        #     self.grScene.scene.history.storeHistory("Item A")
        # elif event.key() == Qt.Key_2:
        #     self.grScene.scene.history.storeHistory("Item B")
        # elif event.key() == Qt.Key_3:
        #     self.grScene.scene.history.storeHistory("Item C")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            # self.grScene.scene.history.redo()
        if event.key() == Qt.Key_H:
            print('HISTORY:     len(%d)' % len(self.grScene.scene.history.history_stack),
                  ' -- current_step', self.grScene.scene.history.history_current_step)
            ix = 0
            for item in self.grScene.scene.history.history_stack:
                print('@', ix, "--", item['desc'])
                ix += 1
        else:
            super().keyPressEvent(event)

    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()

        self.grScene.scene.history.storeHistory("Delete Selected")
