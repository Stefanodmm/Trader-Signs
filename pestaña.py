import sys  # Importar sys para salir de la aplicación
import PyQt5
from PyQt5 import QtWidgets, QtCore
from qtwidgets import Toggle

# Validar imports
try:
    import PyQt5
    from PyQt5 import QtWidgets, QtCore
    from qtwidgets import Toggle
except ImportError as e:
    # Mostrar ventana de advertencia si falta algún import
    app = QtWidgets.QApplication(sys.argv)
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText("Faltan algunos imports necesarios.")
    msg.setInformativeText(str(e))
    msg.setWindowTitle("Error de Importación")
    msg.exec_()
    sys.exit(1)  # Salir de la aplicación

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Crear un contenedor y un layout vertical
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # Agregar el texto "Señales a usar:" centrado
        titulo = QtWidgets.QLabel("Señales a usar:")
        titulo.setAlignment(QtCore.Qt.AlignCenter)  # Centrar el texto
        layout.addWidget(titulo)  # Agregar el título al layout

        # Nombres de los indicadores
        nombres = ["RSI", "MACD", "B.Bolinger", "VRVP"]

        # Crear Toggles con etiquetas
        for nombre in nombres:
            h_layout = QtWidgets.QHBoxLayout()  # Layout horizontal para cada toggle y su etiqueta
            toggle = Toggle()
            toggle.setFixedSize(40, 30)  # Ajustar el tamaño del toggle
            label = QtWidgets.QLabel(nombre)  # Crear la etiqueta

            h_layout.addWidget(label)  # Agregar la etiqueta al layout horizontal
            h_layout.addWidget(toggle)  # Agregar el toggle al layout horizontal
            layout.addLayout(h_layout)  # Agregar el layout horizontal al layout vertical

        # Crear un layout horizontal para los botones
        button_layout = QtWidgets.QHBoxLayout()
        btn_ajustes = QtWidgets.QPushButton("Ajustes")
        btn_iniciar = QtWidgets.QPushButton("Iniciar")

        button_layout.addWidget(btn_ajustes)  # Agregar el botón de ajustes
        button_layout.addWidget(btn_iniciar)  # Agregar el botón de iniciar

        layout.addLayout(button_layout)  # Agregar el layout de botones al layout vertical

        container.setLayout(layout)
        self.setCentralWidget(container)

app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()