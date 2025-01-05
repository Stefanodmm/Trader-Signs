import sys  # Importar sys para salir de la aplicación
import os  # Importar os para verificar la existencia del archivo
import json  # Importar json para manejar el archivo de configuración
import PyQt5
from PyQt5 import QtWidgets, QtCore
from qtwidgets import Toggle
import subprocess
import requests
from macd_calculo import calcular_macd  # Importar la función calcular_macd
from rsi_calculo import calcular_rsi  # Importar la función calcular_rsi
from bb_calculo import calcular_bollinger  # Importar la función calcular_bollinger
from vrvp_calculo import calcular_vrvp

# Validar imports
try:
    import sys  # Importar sys para salir de la aplicación
    import os  # Importar os para verificar la existencia del archivo
    import json  # Importar json para manejar el archivo de configuración
    import PyQt5
    from PyQt5 import QtWidgets, QtCore
    from qtwidgets import Toggle
    import subprocess
    from macd_calculo import calcular_macd
    from rsi_calculo import calcular_rsi
    from bb_calculo import calcular_bollinger
    from vrvp_calculo import calcular_vrvp
    
except ImportError as e:
    # Mostrar ventana de advertencia si falta algún import
    app = QtWidgets.QApplication(sys.argv)
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText("Faltan algunos imports necesarios.")
    msg.setInformativeText(f"Error de importación: {str(e)}")
    msg.setWindowTitle("Error de Importación")
    msg.exec_()
    sys.exit(1)  # Salir de la aplicación

# Ruta del archivo de configuración
config_file = 'config.json'

# Verificar si el archivo de configuración existe
if not os.path.exists(config_file):
    # Crear un archivo de configuración con valores predeterminados
    default_config = {
        "RSI": {"periodo": 14, "temporalidad": "1d", "tiempo_espera": 5},
        "MACD": {"rapido": 12, "lento": 26, "signal": 9, "temporalidad": "1d", "tiempo_espera": 5},
        "B.Bolinger": {"periodo": 20, "desviacion": 2, "temporalidad": "1d", "tiempo_espera": 5},
        "VRVP": {"periodo": 14, "temporalidad": "1d", "tiempo_espera": 5}
    }
    with open(config_file, 'w') as f:
        json.dump(default_config, f, indent=4)
    print(f"Archivo de configuración '{config_file}' creado con valores predeterminados.")

class InfoWindow(QtWidgets.QWidget):
    def __init__(self, active_signals):
        super().__init__()
        self.setWindowTitle("Información en Tiempo Real")
        self.setGeometry(100, 100, 600, 200)  # Tamaño de la ventana

        layout = QtWidgets.QVBoxLayout()
        self.text_area = QtWidgets.QTextEdit()
        self.text_area.setReadOnly(True)  # Hacer el área de texto de solo lectura
        layout.addWidget(self.text_area)

        self.setLayout(layout)
        self.active_signals = active_signals  # Guardar señales activas
        self.timer = QtCore.QTimer(self)  # Crear un temporizador
        self.timer.timeout.connect(self.update_info)  # Conectar el temporizador a la función de actualización

        # Obtener el tiempo de espera de las señales activas
        self.tiempo_espera = self.obtener_tiempo_espera()
        if self.tiempo_espera:
            self.timer.start(self.tiempo_espera * 1000)  # Actualizar cada tiempo de espera en milisegundos
        else:
            self.timer.start(1000)  # Valor por defecto si no hay señales activas

        self.update_info()  # Llamar a la función de actualización inicialmente

    def obtener_tiempo_espera(self):
        tiempos = []
        for signal in self.active_signals:
            with open(config_file) as f:
                config = json.load(f)
            
            # Verificar si la señal existe en la configuración
            if signal not in config:
                raise KeyError(f"La señal '{signal}' no se encuentra en la configuración.")
            
            tiempos.append(config[signal]["tiempo_espera"])
        
        # Verificar si todos los tiempos de espera son iguales
        if len(set(tiempos)) == 1:
            return tiempos[0]  # Retornar el tiempo de espera si son iguales
        return None  # Retornar None si no son iguales

    def determinar_recomendacion_general(self, recomendaciones):
        """Determina la recomendación general basada en las recomendaciones individuales."""
        if recomendaciones:
            if all(r == "Comprar" for r in recomendaciones):
                return "Comprar"
            elif all(r == "Vender" for r in recomendaciones):
                return "Vender"
            else:
                return "Mantener"
        return "Sin recomendaciones"

    def update_info(self):
        info_text = "Señales activas:\n"
        recomendaciones = []  # Lista para almacenar recomendaciones de cada señal
        recomendaciones_individuales = []  # Lista para recomendaciones individuales

        # Evaluar cada señal activa
        for signal in self.active_signals:
            if signal == "RSI":
                rsi = calcular_rsi()  # Llamar a la función calcular_rsi
                info_text += f"RSI: {rsi:.2f} | "
                if rsi < 30:
                    recomendaciones.append("Comprar")
                    recomendaciones_individuales.append("RSI recomienda: Comprar")
                elif rsi > 70:
                    recomendaciones.append("Vender")
                    recomendaciones_individuales.append("RSI recomienda: Vender")
                else:
                    recomendaciones.append("Mantener")
                    recomendaciones_individuales.append("RSI recomienda: Mantener")

            elif signal == "MACD":
                macd, signal_value = calcular_macd("BTCUSDT", "1m", 100)  # Llamar a la función calcular_macd
                info_text += f"MACD: {macd:.2f}, Signal: {signal_value:.2f} | "
                if macd > signal_value:
                    recomendaciones.append("Comprar")
                    recomendaciones_individuales.append("MACD recomienda: Comprar")
                elif macd < signal_value:
                    recomendaciones.append("Vender")
                    recomendaciones_individuales.append("MACD recomienda: Vender")
                else:
                    recomendaciones.append("Mantener")
                    recomendaciones_individuales.append("MACD recomienda: Mantener")

            elif signal == "B.Bolinger":
                media_movil, upper_band, lower_band, closes = calcular_bollinger()  # Llamar a la función calcular_bollinger
                close_price = closes[-1]  # Precio de cierre más reciente

                # Calcular la posición del precio de cierre en relación con las bandas
                if close_price > upper_band:
                    position_value = min(11, int((close_price - upper_band) / (upper_band - lower_band) * 10))  # Más alto que la banda superior
                elif close_price < lower_band:
                    position_value = max(-11, int((close_price - lower_band) / (upper_band - lower_band) * -10))  # Más bajo que la banda inferior
                else:
                    # Calcular la posición relativa entre las bandas
                    position_value = int((close_price - lower_band) / (upper_band - lower_band) * 10)  # Entre las bandas

                info_text += f"B.Bolinger: {position_value} (Banda Superior: {upper_band:.2f}, Banda Inferior: {lower_band:.2f}) | "  # Mostrar el valor de posición directamente

                # Determinar la recomendación basada en el valor de posición
                if position_value >= 10:  # Vender si el valor es 10 o 11
                    recomendaciones.append("Vender")
                    recomendaciones_individuales.append("B.Bolinger recomienda: Vender")
                elif position_value <= -10:  # Comprar si el valor es -10 o -11
                    recomendaciones.append("Comprar")
                    recomendaciones_individuales.append("B.Bolinger recomienda: Comprar")
                else:
                    recomendaciones.append("Mantener")
                    recomendaciones_individuales.append("B.Bolinger recomienda: Mantener")

            elif signal == "VRVP":
                vrvp_value = self.calcular_vrvp()
                info_text += f"VRVP: {vrvp_value:.2f} | "
                if vrvp_value > 0:  # Cambia esta condición según tu lógica
                    recomendaciones.append("Comprar")
                    recomendaciones_individuales.append("VRVP recomienda: Comprar")
                else:
                    recomendaciones.append("Vender")
                    recomendaciones_individuales.append("VRVP recomienda: Vender")

        # Verificar si todas las recomendaciones son iguales
        if recomendaciones:
            if all(r == "Comprar" for r in recomendaciones):
                recomendacion_general = "Comprar"
            elif all(r == "Vender" for r in recomendaciones):
                recomendacion_general = "Vender"
            else:
                recomendacion_general = "Mantener"
        else:
            recomendacion_general = "Sin recomendaciones."

        info_text += f"\nRecomendación general: {recomendacion_general}"

        # Agregar recomendaciones individuales
        info_text += "\nRecomendaciones individuales:\n" + "\n".join(recomendaciones_individuales)

        self.text_area.setText(info_text)

    def calcular_vrvp(self):
        # Implementar la lógica para calcular VRVP
        # Aquí puedes agregar la lógica para calcular el VRVP
        # Por ejemplo, puedes usar un valor ficticio o una lógica simple
        return 0  # Cambia esto por la lógica real de cálculo de VRVP

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.active_signals = []  # Lista para almacenar señales activas

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

            # Conectar la señal del toggle a un método
            toggle.toggled.connect(lambda checked, n=nombre: self.toggle_activated(checked, n))

            h_layout.addWidget(label)  # Agregar la etiqueta al layout horizontal
            h_layout.addWidget(toggle)  # Agregar el toggle al layout horizontal
            layout.addLayout(h_layout)  # Agregar el layout horizontal al layout vertical

        # Crear un layout horizontal para los botones
        button_layout = QtWidgets.QHBoxLayout()
        btn_ajustes = QtWidgets.QPushButton("Ajustes")
        btn_iniciar = QtWidgets.QPushButton("Iniciar")  # Botón de iniciar

        button_layout.addWidget(btn_ajustes)  # Agregar el botón de ajustes
        button_layout.addWidget(btn_iniciar)  # Agregar el botón de iniciar

        layout.addLayout(button_layout)  # Agregar el layout de botones al layout vertical

        # Conectar el botón de ajustes a un método
        btn_ajustes.clicked.connect(self.abrir_ajustes)  # Conectar el botón a la función
        btn_iniciar.clicked.connect(self.iniciar)  # Conectar el botón de iniciar

        container.setLayout(layout)
        self.setCentralWidget(container)

    def toggle_activated(self, checked, nombre):
        if checked:
            print(f"Toggle activado: {nombre}")
            self.active_signals.append(nombre)  # Agregar la señal activa
        else:
            if nombre in self.active_signals:
                self.active_signals.remove(nombre)  # Eliminar la señal si se desactiva

    def iniciar(self):
        # Abrir la ventana de información con las señales activas
        self.info_window = InfoWindow(self.active_signals)
        self.info_window.show()

    def abrir_ajustes(self):
        # Abrir el archivo de configuración en el Bloc de notas
        subprocess.Popen(['notepad.exe', 'config.json'])  # Esto abrirá el archivo en el Bloc de notas

app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()