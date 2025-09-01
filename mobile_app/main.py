"""
GroomerAsist mobile app (Kivy)
- Offline persistence (JSON in app storage)
- History screen, export to user_data_dir and Downloads (if available)
"""

import json
import os
from datetime import datetime
from uuid import uuid4

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import DictProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation

KV = """
#:import dp kivy.metrics.dp
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
ScreenManager:
    transition: FadeTransition()
    InicioScreen:
    RegistroScreen:
    DetallesScreen:
    ResumenScreen:
    HistorialScreen:

<InicioScreen>:
    name: 'inicio'
    BoxLayout:
        id: rootbox
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(16)
        canvas.before:
            Color:
                rgba: 0.10, 0.12, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: '¿Dónde estás trabajando?'
            font_size: '20sp'
        Button:
            text: '🐾 Almitas Peludas'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.set_lugar('Almitas Peludas')
        Button:
            text: '🏢 Local'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.set_lugar('Local')
        Button:
            text: '� Historial'
            background_normal: ''
            background_color: 0.25, 0.35, 0.80, 1
            on_press: app.bump_button(self)
            on_release: app.ir_historial()

<RegistroScreen>:
    name: 'registro'
    BoxLayout:
        id: rootbox
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: 0.10, 0.12, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: titulo
            text: 'Registrando en ' + app.lugar
            font_size: '18sp'
        TextInput:
            id: nombre
            hint_text: 'Nombre del perro'
            multiline: False
        Button:
            text: 'Siguiente'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.set_nombre(nombre.text)

<DetallesScreen>:
    name: 'detalles'
    BoxLayout:
        id: rootbox
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.10, 0.12, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Detalles de ' + app.datos_perro.get('Nombre', '')
            font_size: '18sp'
        Button:
            text: 'Raza 🐕‍🦺'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.ask_texto('Raza', 'Ingresa la raza:')
        Button:
            text: 'Edad 🧴'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.ask_numero('Edad', 'Ingresa la edad:')
        Button:
            text: 'Nudos 🧶'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.ask_booleano('Nudos', '¿Tiene nudos?')
        Button:
            text: 'Uñas 💅'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.ask_booleano('Uñas', '¿Requiere corte de uñas?')
        Button:
            text: 'Estado general ❤️‍🩹'
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.ask_texto('Estado General', 'Describe el estado:')
        Button:
            text: 'Cobro 💵'
            background_normal: ''
            background_color: 0.30, 0.60, 0.25, 1
            on_press: app.bump_button(self)
            on_release: app.ask_monetario('Cobro', '¿Cuánto cobraste?')
        Widget:
        Button:
            text: 'Finalizar Registro'
            size_hint_y: None
            height: dp(48)
            background_normal: ''
            background_color: 0.25, 0.35, 0.80, 1
            on_press: app.bump_button(self)
            on_release: app.ir_resumen()

<ResumenScreen>:
    name: 'resumen'
    BoxLayout:
        id: rootbox
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.10, 0.12, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: '¡Registro Finalizado!'
            font_size: '20sp'
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: contenedor
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'Volver al inicio'
            size_hint_y: None
            height: dp(48)
            background_normal: ''
            background_color: 0.20, 0.55, 0.45, 1
            on_press: app.bump_button(self)
            on_release: app.resetear()
        Button:
            text: 'Ver historial'
            size_hint_y: None
            height: dp(48)
            background_normal: ''
            background_color: 0.25, 0.35, 0.80, 1
            on_press: app.bump_button(self)
            on_release: app.ir_historial()

<HistorialScreen>:
    name: 'historial'
    BoxLayout:
        id: rootbox
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.10, 0.12, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: titulo
            text: 'Historial de registros'
            font_size: '20sp'
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            spacing: dp(8)
            Button:
                text: 'Exportar JSON'
                background_normal: ''
                background_color: 0.20, 0.55, 0.45, 1
                on_press: app.bump_button(self)
                on_release: app.exportar_json()
            Button:
                text: 'Limpiar registros'
                background_normal: ''
                background_color: 0.85, 0.30, 0.30, 1
                on_press: app.bump_button(self)
                on_release: app.limpiar_registros()
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: lista
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: 'Volver'
            size_hint_y: None
            height: dp(48)
            background_normal: ''
            background_color: 0.25, 0.35, 0.80, 1
            on_press: app.bump_button(self)
            on_release: app.ir_inicio()
"""


class InicioScreen(Screen):
    pass


class RegistroScreen(Screen):
    pass


class DetallesScreen(Screen):
    pass


class ResumenScreen(Screen):
    pass


class HistorialScreen(Screen):
    pass


class GroomerMobileApp(App):
    datos_perro = DictProperty({})
    lugar = StringProperty("")
    db_path = StringProperty("")

    def build(self):
        root = Builder.load_string(KV)
        # Local DB file path
        self.db_path = os.path.join(self.user_data_dir, "registros.json")
        self._asegurar_db()
        self._registro_guardado = False
        return root

    def set_lugar(self, lugar):
        self.datos_perro = {"Lugar": lugar}
        self._registro_guardado = False
        self.lugar = lugar
        self.root.current = "registro"

    def set_nombre(self, nombre):
        if not nombre:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            Popup(title="Error", content=Label(text="Ingresa el nombre del perro"), size_hint=(0.8, 0.3)).open()
            return
        self.datos_perro["Nombre"] = nombre
        self.root.current = "detalles"

    # Simple input popups
    def ask_texto(self, clave, mensaje):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        ti = TextInput(hint_text=mensaje, multiline=False)
        btn = Button(text="Guardar")
        layout.add_widget(ti)
        layout.add_widget(btn)
        pop = Popup(title=clave, content=layout, size_hint=(0.8, 0.4))
        def guardar(_):
            valor = ti.text.strip()
            if valor:
                self.datos_perro[clave] = valor
            pop.dismiss()
        btn.bind(on_release=guardar)
        pop.open()

    def ask_numero(self, clave, mensaje):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        ti = TextInput(hint_text=mensaje, multiline=False, input_filter="int")
        btn = Button(text="Guardar")
        layout.add_widget(ti)
        layout.add_widget(btn)
        pop = Popup(title=clave, content=layout, size_hint=(0.8, 0.4))
        def guardar(_):
            if ti.text.strip():
                self.datos_perro[clave] = int(ti.text.strip())
            pop.dismiss()
        btn.bind(on_release=guardar)
        pop.open()

    def ask_booleano(self, clave, mensaje):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        btn_si = Button(text="Sí")
        btn_no = Button(text="No")
        layout.add_widget(Button(text=mensaje, size_hint_y=None, height="40dp", disabled=True))
        layout.add_widget(btn_si)
        layout.add_widget(btn_no)
        pop = Popup(title=clave, content=layout, size_hint=(0.8, 0.4))
        def set_valor(v, _):
            self.datos_perro[clave] = "Sí" if v else "No"
            pop.dismiss()
        btn_si.bind(on_release=lambda _btn: set_valor(True, _btn))
        btn_no.bind(on_release=lambda _btn: set_valor(False, _btn))
        pop.open()

    def ask_monetario(self, clave, mensaje):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.textinput import TextInput
        from kivy.uix.button import Button
        layout = BoxLayout(orientation="vertical", padding=12, spacing=8)
        ti = TextInput(hint_text=mensaje + " (ej: 15000)", multiline=False, input_filter="float")
        btn = Button(text="Guardar", background_normal='', background_color=(0.20, 0.55, 0.45, 1))
        layout.add_widget(ti)
        layout.add_widget(btn)
        pop = Popup(title=clave, content=layout, size_hint=(0.8, 0.4))
        def guardar(_):
            txt = ti.text.strip().replace(',', '.')
            try:
                valor = round(float(txt), 2)
                self.datos_perro[clave] = valor
            except Exception:
                self._popup_msg("Formato inválido", "Ingresa un número válido, por ejemplo 15000 o 15000.50")
            pop.dismiss()
        btn.bind(on_release=guardar)
        pop.open()

    def ir_resumen(self):
        cont = self.root.get_screen("resumen").ids.contenedor
        cont.clear_widgets()
        from kivy.uix.label import Label
        for k, v in self.datos_perro.items():
            cont.add_widget(Label(text=f"{k}: {v}", size_hint_y=None, height="28dp"))
        self._guardar_registro_actual()
        self.root.current = "resumen"

    def resetear(self):
        self.datos_perro = {}
        self.lugar = ""
        self._registro_guardado = False
        self.root.current = "inicio"

    # ---------- Offline persistence ----------
    def _asegurar_db(self):
        os.makedirs(self.user_data_dir, exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False)

    def _leer_registros(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _escribir_registros(self, registros):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
        return True

    def _guardar_registro_actual(self):
        if not self.datos_perro:
            return
        if getattr(self, "_registro_guardado", False):
            return
        registro = dict(self.datos_perro)
        registro["id"] = str(uuid4())
        registro["timestamp"] = datetime.now().isoformat(timespec="seconds")
        registros = self._leer_registros()
        registros.append(registro)
        self._escribir_registros(registros)
        self._registro_guardado = True

    # ---------- Animations ----------
    def bump_button(self, btn):
        try:
            Animation.cancel_all(btn)
        except Exception:
            pass
        a1 = Animation(opacity=0.8, duration=0.06)
        a2 = Animation(opacity=1.0, duration=0.08)
        (a1 + a2).start(btn)

    # ---------- History & export ----------
    def ir_historial(self):
        self._refrescar_historial()
        self.root.current = "historial"

    def ir_inicio(self):
        self.root.current = "inicio"

    def _refrescar_historial(self):
        pantalla = self.root.get_screen("historial")
        lista = pantalla.ids.lista
        lista.clear_widgets()
        from kivy.uix.label import Label
        registros = self._leer_registros()
        pantalla.ids.titulo.text = f"Historial de registros ({len(registros)})"
        if not registros:
            lista.add_widget(Label(text="Sin registros", size_hint_y=None, height="28dp"))
            return
        for r in reversed(registros):
            nombre = r.get("Nombre", "(Sin nombre)")
            ts = r.get("timestamp", "")
            detalle = f"{ts} - {nombre}"
            lista.add_widget(Label(text=detalle, size_hint_y=None, height="28dp"))

    def exportar_json(self):
        registros = self._leer_registros()
        if not registros:
            self._popup_msg("Exportar", "No hay registros para exportar.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"export_{ts}.json"
        ruta_local = os.path.join(self.user_data_dir, nombre)
        with open(ruta_local, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
        rutas = [ruta_local]
        try:
            from plyer import storagepath
            downloads = storagepath.get_downloads_dir()
            if downloads:
                ruta_descargas = os.path.join(downloads, nombre)
                with open(ruta_local, "rb") as src, open(ruta_descargas, "wb") as dst:
                    dst.write(src.read())
                rutas.append(ruta_descargas)
        except Exception:
            pass
        msg = "\n".join([f"• {r}" for r in rutas])
        self._popup_msg("Exportar", f"Archivo(s) exportado(s):\n{msg}")

    def limpiar_registros(self):
        self._escribir_registros([])
        self._refrescar_historial()
        self._popup_msg("Limpiar", "Registros eliminados.")

    def _popup_msg(self, titulo, texto):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        Popup(title=titulo, content=Label(text=texto), size_hint=(0.9, 0.4)).open()


if __name__ == '__main__':
    GroomerMobileApp().run()
