"""
GroomerAsist mobile app (Kivy)
- Offline persistence (JSON in app storage)
- History screen, export to user_data_dir and Downloads (if available)
"""

import json
import os
from datetime import datetime
from uuid import uuid4
from typing import Any, cast
from kivy.utils import platform as core_platform
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import BooleanProperty

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import DictProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager as KivyScreenManager
from kivy.animation import Animation

KV = """
#:import dp kivy.metrics.dp
#:import FadeTransition kivy.uix.screenmanager.FadeTransition

<Primary@Button>:
    background_normal: ''
    background_color: 0.85, 0.10, 0.15, 1
    color: 1, 1, 1, 1
    font_size: '14sp' if app.compacto else '15sp'
    height: dp(40) if app.compacto else dp(46)
    size_hint_y: None

<Outline@Button>:
    background_normal: ''
    background_color: 0, 0, 0, 0
    color: 0.95, 0.95, 0.96, 1
    font_size: '14sp' if app.compacto else '15sp'
    canvas.before:
        Color:
            rgba: 0.85, 0.10, 0.15, 1
        Line:
            rounded_rectangle: (self.x+1, self.y+1, self.width-2, self.height-2, dp(12))
            width: 1.2
    on_press:
        self.opacity = 0.9
    on_release:
        self.opacity = 1

<Chip@Button>:
    background_normal: ''
    background_color: 0.16, 0.16, 0.18, 1
    color: 0.98, 0.98, 0.99, 1
    font_size: '12sp' if app.compacto else '13sp'
    size_hint_y: None
    height: dp(32) if app.compacto else dp(36)
    padding: dp(10) if app.compacto else dp(12), 0
    canvas.before:
        Color:
            rgba: 0.16, 0.16, 0.18, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12),]
    on_press:
        self.opacity = 0.9
    on_release:
        self.opacity = 1

<BrandBar@BoxLayout>:
    size_hint_y: None
    height: dp(44) if app.compacto else dp(52)
    spacing: dp(8)
    padding: dp(4), 0
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0
        Rectangle:
            pos: self.pos
            size: self.size
    Image:
        source: app.logo_path
        size_hint_x: None
        width: dp(34) if app.compacto else dp(42)
        allow_stretch: True
        keep_ratio: True
        opacity: 1 if app.logo_path else 0
    Label:
        markup: True
        text: '[b]GroomerAsist[/b]'
        color: 1,1,1,1
        font_size: '18sp' if app.compacto else '20sp'

ScreenManager:
    transition: FadeTransition()
    InicioScreen:
    RegistroScreen:
    DetallesScreen:
    ResumenScreen:
    HistorialScreen:

<InicioScreen>:
    name: 'inicio'
    on_pre_enter: app.anim_screen(self)
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12) if app.compacto else dp(18)
        spacing: dp(10) if app.compacto else dp(14)
        canvas.before:
            Color:
                rgba: 0.02, 0.02, 0.03, 1
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.35, 0.00, 0.03, 1
            Rectangle:
                pos: self.x, self.top - (dp(3) if app.compacto else dp(4))
                size: self.width, (dp(3) if app.compacto else dp(4))
        BrandBar:
        Label:
            text: '¿Dónde estás trabajando?'
            font_size: '20sp'
            color: 1,1,1,1
            size_hint_y: None
            height: dp(36) if app.compacto else dp(40)
        BoxLayout:
            spacing: dp(8) if app.compacto else dp(10)
            size_hint_y: None
            height: dp(78) if app.compacto else dp(86)
            orientation: 'vertical' if self.width < dp(520) else 'horizontal'
            Outline:
                text: '🐾  Almitas Peludas'
                on_press: app.bump_button(self)
                on_release: app.set_lugar('Almitas Peludas')
            Outline:
                text: '🏢  Local'
                on_press: app.bump_button(self)
                on_release: app.set_lugar('Local')
        Widget:
        BoxLayout:
            size_hint_y: None
            height: dp(40) if app.compacto else dp(46)
            spacing: dp(8)
            Outline:
                text: '📜  Ver historial'
                on_press: app.bump_button(self)
                on_release: app.ir_historial()
            Chip:
                text: 'Compacto'
                on_release: app.set_compacto()

<RegistroScreen>:
    name: 'registro'
    on_pre_enter: app.anim_screen(self)
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12) if app.compacto else dp(18)
        spacing: dp(10) if app.compacto else dp(12)
        canvas.before:
            Color:
                rgba: 0.02, 0.02, 0.03, 1
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.35, 0.00, 0.03, 1
            Rectangle:
                pos: self.x, self.top - dp(4)
                size: self.width, dp(4)
        BrandBar:
        Label:
            id: titulo
            text: 'Registrando en ' + app.lugar
            font_size: '18sp'
            color: 1,1,1,1
            size_hint_y: None
            height: dp(30) if app.compacto else dp(34)
        BoxLayout:
            spacing: dp(8) if app.compacto else dp(10)
            size_hint_y: None
            height: dp(36) if app.compacto else dp(40)
            orientation: 'vertical' if self.width < dp(520) else 'horizontal'
            TextInput:
                id: nombre
                hint_text: 'Nombre del perro'
                multiline: False
            TextInput:
                id: cliente
                hint_text: 'Cliente (opcional)'
                multiline: False
        BoxLayout:
            size_hint_y: None
            height: dp(36)
            spacing: dp(8)
            Chip:
                text: 'Raza'
                on_release: app.ask_raza_popup()
            Chip:
                text: 'Edad'
                on_release: app.ask_numero('Edad', 'Ingresa la edad:')
            Chip:
                text: 'Nudos'
                on_release: app.ask_booleano('Nudos', '¿Tiene nudos?')
            Chip:
                text: 'Uñas'
                on_release: app.ask_booleano('Uñas', '¿Requiere corte de uñas?')
        BoxLayout:
            size_hint_y: None
            height: dp(36)
            spacing: dp(8)
            Chip:
                text: 'Ansioso'
                on_release: app.ask_booleano('Ansioso', '¿Llegó ansioso o asustado?')
            Chip:
                text: 'Reco. Vet'
                on_release: app.ask_booleano('Recomendación Vet', '¿Recomendar visita al veterinario?')
            Chip:
                text: 'Estado'
                on_release: app.ask_texto('Estado General', 'Describe el estado:')
        BoxLayout:
            size_hint_y: None
            height: dp(36)
            spacing: dp(8)
            Chip:
                text: 'Servicio'
                on_release: app.ask_texto('Servicio', '¿Qué servicio realizaste?')
            Chip:
                text: 'Productos'
                on_release: app.ask_texto('Productos', '¿Qué productos usaste?')
            Chip:
                text: 'Cobro'
                on_release: app.ask_monetario('Cobro', '¿Cuánto cobraste?')
            Chip:
                text: 'Foto'
                on_release: app.tomar_foto()
        BoxLayout:
            size_hint_y: None
            height: dp(46)
            spacing: dp(10)
            Outline:
                text: '🔍 Buscar historial'
                on_press: app.bump_button(self)
                on_release: app.buscar_historial(nombre.text)
            Primary:
                text: 'Continuar'
                on_press: app.bump_button(self)
                on_release: app.set_nombre(nombre.text, cliente.text)

<DetallesScreen>:
    name: 'detalles'
    on_pre_enter: app.anim_screen(self)
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(8)
        canvas.before:
            Color:
                rgba: 0.02, 0.02, 0.03, 1
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.35, 0.00, 0.03, 1
            Rectangle:
                pos: self.x, self.top - dp(4)
                size: self.width, dp(4)
    BrandBar:
        Label:
            text: 'Detalles de ' + app.datos_perro.get('Nombre', '')
            font_size: '18sp'
            color: 1,1,1,1
            size_hint_y: None
            height: dp(34)
        GridLayout:
            cols: 1 if self.width < dp(520) else 2
            size_hint_y: None
            height: dp(68) if app.compacto else dp(76)
            row_default_height: dp(32) if app.compacto else dp(36)
            row_force_default: True
            spacing: dp(8)
            Chip:
                text: 'Raza'
                on_release: app.ask_texto('Raza', 'Ingresa la raza:')
            Chip:
                text: 'Edad'
                on_release: app.ask_numero('Edad', 'Ingresa la edad:')
            Chip:
                text: 'Nudos'
                on_release: app.ask_booleano('Nudos', '¿Tiene nudos?')
            Chip:
                text: 'Uñas'
                on_release: app.ask_booleano('Uñas', '¿Requiere corte de uñas?')
            Chip:
                text: 'Ansioso'
                on_release: app.ask_booleano('Ansioso', '¿Llegó ansioso o asustado?')
            Chip:
                text: 'Reco. Vet'
                on_release: app.ask_booleano('Recomendación Vet', '¿Recomendar visita al veterinario?')
        GridLayout:
            cols: 1 if self.width < dp(520) else 2
            size_hint_y: None
            height: dp(68) if app.compacto else dp(76)
            row_default_height: dp(32) if app.compacto else dp(36)
            row_force_default: True
            spacing: dp(8)
            Chip:
                text: 'Estado'
                on_release: app.ask_texto('Estado General', 'Describe el estado:')
            Chip:
                text: 'Servicio'
                on_release: app.ask_texto('Servicio', '¿Qué servicio realizaste?')
            Chip:
                text: 'Productos'
                on_release: app.ask_texto('Productos', '¿Qué productos usaste?')
            Chip:
                text: 'Cobro'
                on_release: app.ask_monetario('Cobro', '¿Cuánto cobraste?')
        BoxLayout:
            size_hint_y: None
            height: dp(40) if app.compacto else dp(46)
            spacing: dp(8) if app.compacto else dp(10)
            Outline:
                text: '📷 Foto (después)'
                on_press: app.bump_button(self)
                on_release: app.tomar_foto()
            Primary:
                text: 'Finalizar registro'
                on_press: app.bump_button(self)
                on_release: app.ir_resumen()

<ResumenScreen>:
    name: 'resumen'
    on_pre_enter: app.anim_screen(self)
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12) if app.compacto else dp(18)
        spacing: dp(8) if app.compacto else dp(10)
        canvas.before:
            Color:
                rgba: 0.02, 0.02, 0.03, 1
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.35, 0.00, 0.03, 1
            Rectangle:
                pos: self.x, self.top - dp(4)
                size: self.width, dp(4)
        BrandBar:
        Label:
            text: 'Registro listo'
            font_size: '20sp'
            color: 1,1,1,1
            size_hint_y: None
            height: dp(32) if app.compacto else dp(36)
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: contenedor
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(2)
        BoxLayout:
            size_hint_y: None
            height: dp(40) if app.compacto else dp(46)
            spacing: dp(8) if app.compacto else dp(10)
            Primary:
                text: '📋 Cliente'
                on_press: app.bump_button(self)
                on_release: app.generar_para_cliente()
            Primary:
                text: '📈 Historial'
                on_press: app.bump_button(self)
                on_release: app.generar_para_historial()
        BoxLayout:
            size_hint_y: None
            height: dp(40) if app.compacto else dp(46)
            spacing: dp(8) if app.compacto else dp(10)
            Outline:
                text: '⟵ Inicio'
                on_release: app.resetear()
            Outline:
                text: 'Ver historial'
                on_release: app.ir_historial()

<HistorialScreen>:
    name: 'historial'
    on_pre_enter: app.anim_screen(self)
    BoxLayout:
        orientation: 'vertical'
        padding: dp(12) if app.compacto else dp(18)
        spacing: dp(8) if app.compacto else dp(10)
        canvas.before:
            Color:
                rgba: 0.02, 0.02, 0.03, 1
            Rectangle:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.35, 0.00, 0.03, 1
            Rectangle:
                pos: self.x, self.top - dp(4)
                size: self.width, dp(4)
        BrandBar:
        Label:
            id: titulo
            text: 'Historial de registros'
            font_size: '20sp'
            color: 1,1,1,1
            size_hint_y: None
            height: dp(30) if app.compacto else dp(34)
        BoxLayout:
            size_hint_y: None
            height: dp(36) if app.compacto else dp(40)
            spacing: dp(6) if app.compacto else dp(8)
            TextInput:
                id: buscador
                hint_text: 'Buscar por mascota o cliente'
                multiline: False
            Outline:
                text: 'Buscar'
                on_press: app.bump_button(self)
                on_release: app.filtrar_historial(buscador.text)
        BoxLayout:
            size_hint_y: None
            height: dp(40) if app.compacto else dp(46)
            spacing: dp(8) if app.compacto else dp(10)
            Outline:
                text: 'Exportar JSON'
                on_press: app.bump_button(self)
                on_release: app.exportar_json()
            Outline:
                text: 'Limpiar'
                on_press: app.bump_button(self)
                on_release: app.limpiar_registros()
            Outline:
                text: 'Sincronizar'
                on_press: app.bump_button(self)
                on_release: app.sync_nube()
        BoxLayout:
            size_hint_y: None
            height: dp(40) if app.compacto else dp(46)
            spacing: dp(8) if app.compacto else dp(10)
            Outline:
                text: 'Exportar TXT'
                on_press: app.bump_button(self)
                on_release: app.exportar_txt()
            Outline:
                text: 'Exportar CSV'
                on_press: app.bump_button(self)
                on_release: app.exportar_csv()
        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: lista
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(2)
        Outline:
            text: '⟵ Volver'
            size_hint_y: None
            height: dp(40) if app.compacto else dp(46)
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
    compacto = BooleanProperty(False)
    logo_path = StringProperty("")

    def build(self):
        root = Builder.load_string(KV)
        # Local DB file path
        self.db_path = os.path.join(self.user_data_dir, "registros.json")
        self._asegurar_db()
        self._registro_guardado = False
        # Buscar logo en carpeta del proyecto
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            candidatos = [
                os.path.join(base_dir, "logo.png"),
                os.path.join(base_dir, "icon.png"),
                os.path.join(base_dir, "assets", "logo.png"),
            ]
            for c in candidatos:
                if os.path.exists(c):
                    self.logo_path = c
                    break
        except Exception:
            self.logo_path = ""
        return root

    def on_start(self):
        # En Android, pedir permisos en tiempo de ejecución.
        if core_platform == 'android':
            self._request_android_permissions()
        # Ajuste inicial de modo compacto según ancho de ventana
        try:
            self.compacto = Window.width < dp(520)
            Window.bind(size=self._on_window_size)
        except Exception:
            pass

    def _on_window_size(self, *_args):
        try:
            self.compacto = Window.width < dp(520)
        except Exception:
            return

    def set_compacto(self):
        self.compacto = not self.compacto

    @property
    def sm(self) -> KivyScreenManager:
        # Helper to satisfy type checker (self.root is set after build)
        return cast(KivyScreenManager, self.root)

    def set_lugar(self, lugar):
        self.datos_perro = {"Lugar": lugar}
        self._registro_guardado = False
        self.lugar = lugar
        self.sm.current = "registro"

    def set_nombre(self, nombre, cliente=""):
        if not nombre:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            Popup(title="Error", content=Label(text="Ingresa el nombre del perro"), size_hint=(0.8, 0.3)).open()
            return
        self.datos_perro["Nombre"] = nombre
        if cliente:
            self.datos_perro["Cliente"] = cliente
        self.sm.current = "detalles"

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
        btn.bind(on_release=guardar)  # type: ignore[attr-defined]
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
        btn.bind(on_release=guardar)  # type: ignore[attr-defined]
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
        btn_si.bind(on_release=lambda _btn: set_valor(True, _btn))  # type: ignore[attr-defined]
        btn_no.bind(on_release=lambda _btn: set_valor(False, _btn))  # type: ignore[attr-defined]
        pop.open()

    def ask_raza_popup(self):
        from kivy.uix.popup import Popup
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.button import Button
        razas = [
            "Caniche", "Bulldog", "Labrador", "Golden", "Shih Tzu",
            "Yorkshire", "Pug", "Mestizo (?)"
        ]
        grid = GridLayout(cols=2, padding=12, spacing=8, size_hint=(1, 1))
        for r in razas:
            b = Button(text=r)
            b.bind(on_release=lambda btn, rr=r: self._set_raza(rr))  # type: ignore[attr-defined]
            grid.add_widget(b)
        self._popup_raza = Popup(title="Elegir raza", content=grid, size_hint=(0.85, 0.7))
        self._popup_raza.open()

    def _set_raza(self, raza):
        self.datos_perro["Raza"] = raza
        try:
            self._popup_raza.dismiss()
        except Exception:
            pass

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
        btn.bind(on_release=guardar)  # type: ignore[attr-defined]
        pop.open()

    def tomar_foto(self):
        # Intentar usar plyer.camera; en Windows puede no estar disponible.
        ruta = os.path.join(self.user_data_dir, f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        try:
            from plyer import camera as _camera  # type: ignore
            if _camera:
                _camera.take_picture(filename=ruta, on_complete=lambda p: self._foto_guardada(p))  # type: ignore[misc]
            else:
                raise RuntimeError("camera not available")
        except Exception:
            # Fallback: marcar como tomada
            self.datos_perro["Foto"] = "Sí"
            self._popup_msg("Foto", "Captura no disponible en este entorno; marcado como 'Sí'.")

    def _foto_guardada(self, path):
        if path:
            self.datos_perro["Foto"] = "Sí"
            self.datos_perro["FotoPath"] = path
            self._popup_msg("Foto", f"Foto guardada en:\n{path}")
        else:
            self._popup_msg("Foto", "No se pudo guardar la foto.")

    def ir_resumen(self):
        cont = self.sm.get_screen("resumen").ids.contenedor
        cont.clear_widgets()
        from kivy.uix.label import Label
        for k, v in self.datos_perro.items():
            if k == "Cobro":
                texto = f"{k}: {self._fmt_monto(v)}"
            else:
                texto = f"{k}: {v}"
            cont.add_widget(Label(text=texto, size_hint_y=None, height="28dp", color=(1,1,1,1)))
        self._guardar_registro_actual()
        self.sm.current = "resumen"

    def resetear(self):
        self.datos_perro = {}
        self.lugar = ""
        self._registro_guardado = False
        self.sm.current = "inicio"

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
        # Haptic feedback en Android
        if core_platform == 'android':
            try:
                from plyer import vibrator  # type: ignore
                vib = getattr(vibrator, 'vibrate', None)
                if callable(vib):
                    vib(0.02)  # vibración muy breve
            except Exception:
                pass

    def _request_android_permissions(self):
        try:
            from android.permissions import request_permissions, Permission  # type: ignore
            perms = [
                getattr(Permission, 'CAMERA', None),
                # Android 13+
                getattr(Permission, 'READ_MEDIA_IMAGES', None),
                # Compat en APIs anteriores
                getattr(Permission, 'READ_EXTERNAL_STORAGE', None),
                getattr(Permission, 'WRITE_EXTERNAL_STORAGE', None),
                getattr(Permission, 'VIBRATE', None),
            ]
            perms = [p for p in perms if p]
            if perms:
                request_permissions(perms)
        except Exception:
            pass

    # ---------- History & export ----------
    def ir_historial(self):
        self._refrescar_historial()
        self.sm.current = "historial"

    def ir_inicio(self):
        self.sm.current = "inicio"

    def buscar_historial(self, nombre):
        self._refrescar_historial()
        self.sm.current = "historial"
        if nombre:
            self.filtrar_historial(nombre)

    def _refrescar_historial(self):
        pantalla = self.sm.get_screen("historial")
        lista = pantalla.ids.lista
        lista.clear_widgets()
        from kivy.uix.label import Label
        registros = self._leer_registros()
        pantalla.ids.titulo.text = f"Historial de registros ({len(registros)})"
        if not registros:
            lista.add_widget(Label(text="Sin registros", size_hint_y=None, height="28dp", color=(1,1,1,1)))
            return
        for r in reversed(registros):
            nombre = r.get("Nombre", "(Sin nombre)")
            ts = r.get("timestamp", "")
            cobro = r.get("Cobro")
            extra = f" - {self._fmt_monto(cobro)}" if cobro is not None else ""
            detalle = f"{ts} - {nombre}{extra}"
            lista.add_widget(Label(text=detalle, size_hint_y=None, height="28dp", color=(1,1,1,1)))

    def filtrar_historial(self, query):
        q = (query or "").strip().lower()
        pantalla = self.sm.get_screen("historial")
        lista = pantalla.ids.lista
        lista.clear_widgets()
        from kivy.uix.label import Label
        registros = self._leer_registros()
        filtrados = []
        for r in registros:
            nombre = (r.get("Nombre", "") or "").lower()
            cliente = (r.get("Cliente", "") or "").lower()
            if q in nombre or q in cliente:
                filtrados.append(r)
        if not filtrados:
            lista.add_widget(Label(text="Sin coincidencias", size_hint_y=None, height="28dp", color=(1,1,1,1)))
            return
        for r in reversed(filtrados):
            nombre = r.get("Nombre", "(Sin nombre)")
            ts = r.get("timestamp", "")
            cobro = r.get("Cobro")
            extra = f" - {self._fmt_monto(cobro)}" if cobro is not None else ""
            detalle = f"{ts} - {nombre}{extra}"
            lista.add_widget(Label(text=detalle, size_hint_y=None, height="28dp", color=(1,1,1,1)))

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
            from plyer import storagepath as _storagepath
            _get = getattr(_storagepath, 'get_downloads_dir', None)
            downloads = _get() if callable(_get) else None
            downloads_path = None
            try:
                # Prefer string path
                if isinstance(downloads, str):
                    downloads_path = downloads
                elif downloads is not None:
                    # Try to get filesystem path
                    downloads_path = os.fspath(downloads)  # type: ignore[arg-type]
            except Exception:
                downloads_path = None
            if downloads_path:
                ruta_descargas = os.path.join(downloads_path, nombre)
                with open(ruta_local, "rb") as src, open(ruta_descargas, "wb") as dst:
                    dst.write(src.read())
                rutas.append(ruta_descargas)
        except Exception:
            pass
        msg = "\n".join([f"• {r}" for r in rutas])
        self._popup_msg("Exportar", f"Archivo(s) exportado(s):\n{msg}")

    def exportar_txt(self):
        registros = self._leer_registros()
        if not registros:
            self._popup_msg("Exportar", "No hay registros para exportar.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"export_{ts}.txt"
        ruta_local = os.path.join(self.user_data_dir, nombre)
        # Construir texto legible
        lineas = []
        for r in registros:
            nombre_p = r.get("Nombre", "(Sin nombre)")
            cliente = r.get("Cliente", "")
            lugar = r.get("Lugar", "")
            tsr = r.get("timestamp", "")
            cobro = r.get("Cobro")
            cobro_txt = self._fmt_monto(cobro) if cobro is not None else "-"
            linea = (
                f"[{tsr}] {nombre_p}"
                + (f" / {cliente}" if cliente else "")
                + (f" @ {lugar}" if lugar else "")
                + f" | Cobro: {cobro_txt}"
            )
            lineas.append(linea)
        with open(ruta_local, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
        rutas = [ruta_local]
        try:
            from plyer import storagepath as _storagepath
            _get = getattr(_storagepath, 'get_downloads_dir', None)
            downloads = _get() if callable(_get) else None
            downloads_path = None
            try:
                if isinstance(downloads, str):
                    downloads_path = downloads
                elif downloads is not None:
                    downloads_path = os.fspath(downloads)  # type: ignore[arg-type]
            except Exception:
                downloads_path = None
            if downloads_path:
                ruta_descargas = os.path.join(downloads_path, nombre)
                with open(ruta_local, "rb") as src, open(ruta_descargas, "wb") as dst:
                    dst.write(src.read())
                rutas.append(ruta_descargas)
        except Exception:
            pass
        msg = "\n".join([f"• {r}" for r in rutas])
        self._popup_msg("Exportar", f"Archivo(s) exportado(s):\n{msg}")

    def exportar_csv(self):
        import csv
        registros = self._leer_registros()
        if not registros:
            self._popup_msg("Exportar", "No hay registros para exportar.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"export_{ts}.csv"
        ruta_local = os.path.join(self.user_data_dir, nombre)
        headers = [
            "Fecha", "Lugar", "Cliente", "Nombre", "Raza", "Edad",
            "Nudos", "Uñas", "Ansioso", "Recomendación Vet", "Estado General",
            "Servicio", "Productos", "Cobro", "Foto"
        ]
        with open(ruta_local, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers, delimiter=';')
            writer.writeheader()
            for r in registros:
                fila = {
                    "Fecha": r.get("timestamp", ""),
                    "Lugar": r.get("Lugar", ""),
                    "Cliente": r.get("Cliente", ""),
                    "Nombre": r.get("Nombre", ""),
                    "Raza": r.get("Raza", ""),
                    "Edad": r.get("Edad", ""),
                    "Nudos": r.get("Nudos", ""),
                    "Uñas": r.get("Uñas", ""),
                    "Ansioso": r.get("Ansioso", ""),
                    "Recomendación Vet": r.get("Recomendación Vet", ""),
                    "Estado General": r.get("Estado General", ""),
                    "Servicio": r.get("Servicio", ""),
                    "Productos": r.get("Productos", ""),
                    "Cobro": r.get("Cobro", ""),
                    "Foto": r.get("Foto", ""),
                }
                writer.writerow(fila)
        rutas = [ruta_local]
        try:
            from plyer import storagepath as _storagepath
            _get = getattr(_storagepath, 'get_downloads_dir', None)
            downloads = _get() if callable(_get) else None
            downloads_path = None
            try:
                if isinstance(downloads, str):
                    downloads_path = downloads
                elif downloads is not None:
                    downloads_path = os.fspath(downloads)  # type: ignore[arg-type]
            except Exception:
                downloads_path = None
            if downloads_path:
                ruta_descargas = os.path.join(downloads_path, nombre)
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

    # ---------- Reportes & Sync ----------
    def generar_para_cliente(self):
        cobro = self.datos_perro.get("Cobro", 0) or 0
        try:
            puntos = int(float(cobro) * 1.35)
        except Exception:
            puntos = 0
        nombre = self.datos_perro.get("Nombre", "")
        lugar = self.datos_perro.get("Lugar", self.lugar)
        fecha = datetime.now().strftime("%d/%m/%Y")
        obs_partes = []
        if self.datos_perro.get("Uñas") == "Sí":
            obs_partes.append("uñas un poquito largas")
        if self.datos_perro.get("Nudos") == "Sí":
            obs_partes.append("nudos leves")
        if self.datos_perro.get("Ansioso") == "Sí":
            obs_partes.append("llegó un poco ansioso")
        obs_texto = ", ".join(obs_partes) if obs_partes else "¡Se portó muy bien!"
        recomendacion = "Para evitar nudos detrás de las orejas, cepilla cada 3 días."
        servicio = self.datos_perro.get("Servicio", "Servicio de grooming")
        msg = (
            f"🐾 Resumen de la sesión de {nombre} - {lugar} 🐾\n"
            f"Fecha: {fecha}\n\n"
            f"Servicio: {servicio}.\n\n"
            f"Observaciones: {obs_texto}.\n\n"
            f"Recomendación: {recomendacion}\n\n"
            f"Puntos de Bienestar ganados: ¡Sumaste {puntos:,} puntos!"
        )
        self._copy_and_notify(msg)

    def generar_para_historial(self):
        ts_now = datetime.now()
        id_serv = ts_now.strftime("%Y%m%d-%H%M")
        lugar = self.datos_perro.get("Lugar", self.lugar)
        cliente = self.datos_perro.get("Cliente", "")
        nombre = self.datos_perro.get("Nombre", "")
        raza = self.datos_perro.get("Raza", "?")
        servicio = self.datos_perro.get("Servicio", "")
        productos = self.datos_perro.get("Productos", "")
        cobro = self.datos_perro.get("Cobro", 0) or 0
        try:
            cobro_n = float(cobro)
        except Exception:
            cobro_n = 0.0
        costo_viaje = float(self.datos_perro.get("Costo Viaje", 0) or 0)
        ganancia = max(cobro_n - costo_viaje, 0)
        puntos = int(cobro_n * 1.35)
        tags = []
        if self.datos_perro.get("Uñas") == "Sí":
            tags.append("UÑAS_LARGAS")
        if self.datos_perro.get("Nudos") == "Sí":
            tags.append("NUDOS")
        if self.datos_perro.get("Ansioso") == "Sí":
            tags.append("ANSIoso")
        visita_vet = self.datos_perro.get("Recomendación Vet", "No")
        if visita_vet == "Sí":
            tags.append("RECOMENDACION_VET")
        notas = self.datos_perro.get("Estado General", "")
        foto = "Si" if self.datos_perro.get("Foto") == "Sí" else "No"
        doc = (
            "--- REGISTRO DE SERVICIO ---\n"
            f"ID_Servicio: {id_serv}\n"
            f"Modo: {lugar}\n"
            f"Cliente: {cliente}\n"
            f"Mascota: {nombre} ({raza})\n"
            f"Tags_Entrada: {', '.join(tags) if tags else 'NINGUNO'}\n"
            f"Servicio: {servicio}\n"
            f"Productos: {productos}\n"
            f"Precio_Total: {int(cobro_n)}\n"
            f"Costo_Viaje: {int(costo_viaje)}\n"
            f"Ganancia_Neta: {int(ganancia)}\n"
            f"Puntos_Generados: {int(puntos)}\n"
            f"Notas_Privadas: {notas}\n"
            f"Foto: {foto}\n"
        )
        self._copy_and_notify(doc)

    def _copy_and_notify(self, text):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            self._popup_msg("Copiado", "Texto generado y copiado al portapapeles.")
        except Exception:
            self._popup_msg("Generado", text)

    def sync_nube(self):
        # Placeholder de sincronización Offline-First
        self._popup_msg("Sincronizar", "Pendiente: integración con Odoo cuando decidas hacerlo.")

    # ---------- Visual helpers ----------
    def anim_screen(self, widget):
        try:
            widget.opacity = 0
            Animation(opacity=1.0, duration=0.25).start(widget)
        except Exception:
            pass

    def _fmt_monto(self, valor):
        try:
            n = float(valor)
            # Formato $ 12.345,67 (estilo es-AR simple)
            txt = f"$ {n:,.2f}"
            return txt.replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return str(valor)


if __name__ == '__main__':
    GroomerMobileApp().run()
