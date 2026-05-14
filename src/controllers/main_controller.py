# src/controllers/main_controller.py
from views.main_window import VentanaPrincipal
from models.chat_model import ModeloChat

# Ajusta el import según cómo colocaste los archivos (src.db.api o db.api)
from src.db.api import create_conversation, add_message, export_conversation_json, export_conversation_xml

class ControladorPrincipal:
    def __init__(self, usuario):
        self.usuario = usuario
        self.modelo = ModeloChat()
        self.vista = VentanaPrincipal(usuario)

        # Id de la conversación activa en la que se guardarán mensajes
        self.current_conversation_id = None

        # Conexiones de señales de la vista con métodos del controlador
        self.vista.enviar_pregunta.connect(self._procesar_pregunta)
        self.vista.solicitar_archivo.connect(self._cargar_archivo)

        # Nuevas señales de exportación desde la vista
        # (asegúrate de que VentanaPrincipal declare estas señales)
        self.vista.export_json_requested.connect(self._export_json)
        self.vista.export_xml_requested.connect(self._export_xml)

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
            # tu lógica existente que extrae texto y guarda en modelo
            resultado = self.modelo.cargar_archivo(ruta)
            # Crear una nueva conversación en la BD y guardarla en el controlador
            conv_id = create_conversation(file_name=ruta)
            self.current_conversation_id = conv_id

            # Actualizar la UI: mostrar nombre del archivo
            nombre = ruta.split("\\")[-1]  # Windows path, si usas posix usa '/'
            self.vista.set_loaded_file(nombre)

            # Mensaje de sistema en interfaz
            self.vista.agregar_mensaje("Sistema", resultado, "#a6e3a1")

            # (Opcional) almacenar mensaje inicial en BD
            try:
                add_message(conv_id, "sistema", f"Archivo cargado: {nombre}")
            except Exception as e:
                # No detener la app si falla la BD; loggear sería ideal
                print("Warning: no se pudo guardar mensaje en DB:", e)

    def _procesar_pregunta(self, pregunta):
        """Maneja la lógica de envío de preguntas a la IA."""
        # Guardar mensaje del usuario en la BD (crear conversación si no existe)
        if not self.current_conversation_id:
            # crear conversación sin archivo asociado
            self.current_conversation_id = create_conversation(file_name=None)

        try:
            add_message(self.current_conversation_id, "usuario", pregunta)
        except Exception as e:
            print("Warning: fallo al guardar mensaje de usuario:", e)

        # Obtener respuesta del modelo (tu implementación actual)
        respuesta = self.modelo.obtener_respuesta_ia(pregunta)

        # Guardar la respuesta en BD
        try:
            add_message(self.current_conversation_id, "modelo", respuesta)
        except Exception as e:
            print("Warning: fallo al guardar respuesta del modelo:", e)

        # Mostrar la respuesta en la UI
        self.vista.agregar_mensaje("AI Assistant", respuesta, "#fab387")

    def _export_json(self):
        """Manejador de exportar a JSON (invocado por la vista)."""
        if not self.current_conversation_id:
            self.vista.mostrar_error("No hay conversación activa para exportar.")
            return

        # La vista abre diálogo y devuelve la ruta elegida
        path = self.vista.get_save_path("json")
        if not path:
            return

        try:
            export_conversation_json(self.current_conversation_id, path)
            self.vista.mostrar_info(f"Conversación exportada a JSON:\n{path}")
        except Exception as e:
            self.vista.mostrar_error(f"No se pudo exportar: {e}")

    def _export_xml(self):
        """Manejador de exportar a XML (invocado por la vista)."""
        if not self.current_conversation_id:
            self.vista.mostrar_error("No hay conversación activa para exportar.")
            return

        path = self.vista.get_save_path("xml")
        if not path:
            return

        try:
            export_conversation_xml(self.current_conversation_id, path)
            self.vista.mostrar_info(f"Conversación exportada a XML:\n{path}")
        except Exception as e:
            self.vista.mostrar_error(f"No se pudo exportar: {e}")