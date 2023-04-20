import sys
from PyQt5.QtWidgets import *

from node_editor_window import NodeEditorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    wnd = NodeEditorWindow(window_width=1600, window_height=900)
    
    sys.exit(app.exec_())
