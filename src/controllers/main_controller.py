from views.main_window import VentanaPrincipal
from models.chat_model import ModeloChat

class ControladorPrincipal:
    def __init__(self, usuario):
        self.usuario = usuario
        self.modelo = ModeloChat()
        self.vista = VentanaPrincipal(usuario)
        
        # Conexión de señales de la vista con métodos del controlador
        self.vista.enviar_pregunta.connect(self._procesar_pregunta)
        self.vista.solicitar_archivo.connect(self._cargar_archivo)

    def mostrar(self):
        """Muestra la ventana principal y carga el historial previo."""
        historial = self.modelo.obtener_historial()
        for item in historial:
            autor = item['autor']
            msg = item['mensaje']
            # Asignar colores según el autor
            colores = {"Sistema": "#a6e3a1", "Assistant": "#fab387", "Usuario": "#b4befe"}
            color = colores.get(autor, "#cdd6f4")
            self.vista.agregar_mensaje(autor, msg, color)
            
        self.vista.show()

    def _cargar_archivo(self):
        """Maneja la lógica de selección y carga de archivos."""
        ruta = self.vista.seleccionar_archivo()
        if ruta:
            resultado = self.modelo.cargar_archivo(ruta)
            self.vista.agregar_mensaje("Sistema", resultado, "#a6e3a1")

    def _procesar_pregunta(self, pregunta):
        """Maneja la lógica de envío de preguntas a la IA."""
        # Nota: La ventana ya agrega el mensaje del usuario visualmente al emitir la señal
        respuesta = self.modelo.obtener_respuesta_ia(pregunta)
        self.vista.agregar_mensaje("AI Assistant", respuesta, "#fab387")
