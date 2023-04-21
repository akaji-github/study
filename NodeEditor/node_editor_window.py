import os

from PyQt5.QtWidgets import *
from node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self, width=800, height=600):
        super().__init__()

        self.init_UI(width, height)

        self.filename = None

    def createAct(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act

    def init_UI(self, width=800, height=600):
        menubar = self.menuBar()

        # initialize menu
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.createAct('&New', 'Ctrl+N', 'Create new graph', self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Open', 'Ctrl+O', 'Create new graph', self.onFileOpen))
        fileMenu.addAction(self.createAct('&Save', 'Ctrl+S', 'Create new graph', self.onFileSave))
        fileMenu.addAction(self.createAct('Save &as', 'Ctrl+shift+S', 'Create new graph', self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Exit', 'Ctrl+Q', 'Exit application', self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createAct('&Undo', 'Ctrl+Z', 'Undo last operation', self.onEditUndo))
        editMenu.addAction(self.createAct('&Redo', 'Ctrl+Shift+Z', 'Redo last operation', self.onEditRedo))
        fileMenu.addSeparator()
        editMenu.addAction(self.createAct('&Delete', 'Del', 'Delete selected item', self.onEditDelete))

        nodeeditor = NodeEditorWidget(self)
        self.setCentralWidget(nodeeditor)

        # stuts bar
        self.statusBar().showMessage('')
        self.status_mouse_pos = QLabel('')
        self.statusBar().addPermanentWidget(self.status_mouse_pos)
        nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)
          
        
        # set window properties
        self.setGeometry(0, 0, width, height)
        self.setWindowTitle('Node Editor')
        self.show()

    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText("Scene Pos:[%d, %d]" % (x, y))

    def onFileNew(self):
        self.centralWidget().scene.clear()

    def onFileOpen(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
        if fname == "":
            return
        
        if os.path.isfile(fname):
            self.centralWidget().scene.loadFromFile(fname)

    def onFileSave(self):
        print('On File Save Clicked')
        if self.filename is None: return self.onFileSaveAs()
        self.centralWidget().scene.saveToFile(self.filename)
        self.statusBar().showMessage('Successfully saved %s' % self.filename)

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')
        if fname == "":
            return        
        self.filename = fname
        self.onFileSave()

    def onEditUndo(self):
        self.centralWidget().scene.history.undo()
        
    def onEditRedo(self):
        self.centralWidget().scene.history.redo()
        
    def onEditDelete(self):
        self.centralWidget().scene.grScene.views()[0].deleteSelected()
