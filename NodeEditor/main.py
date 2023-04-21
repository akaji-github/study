import sys
from PyQt5.QtWidgets import *

from node_editor_window import NodeEditorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    wnd = NodeEditorWindow(width=800, height=600)
    
    sys.exit(app.exec_())
