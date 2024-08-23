from qtpy import QtWidgets

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.file_edit = QLineEdit()
        layout.addWidget(self.file_edit)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.openFileDialog)
        layout.addWidget(self.browse_button)

        self.setLayout(layout)

    def openFileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.file_edit.setText(file_path)
