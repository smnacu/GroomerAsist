# -*- coding: utf-8 -*-
"""Almitas Peludas App

This application serves as a Customer Relationship Management (CRM) tool
for a pet grooming business, "Almitas Peludas". It allows for registering pets
and their owners, logging visits with specific details, and managing sales.

Its core feature is a "Marketing Copilot" that provides actionable opportunities
based on the stored data.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Listbox, Scrollbar, Toplevel
import json
import datetime
import re

class AlmitasPeludasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Almitas Peludas CRM")
        self.geometry("600x700")

        # File paths for data persistence
        self.data_file = "almitas_data.json"
        self.content_file = "content_library.json"
        self.templates_file = "templates.json"

        # Load data from files
        self.lista_de_perros = self.cargar_datos(self.data_file)
        self.lista_de_contenido = self.cargar_datos(self.content_file)
        self.lista_de_plantillas = self.cargar_datos(self.templates_file)

        # Session data
        self.datos_perro_actual = {}
        self.frame_actual = None
        self.oportunidades_actuales = {}

        self.mostrar_inicio()

    def cargar_datos(self, filepath):
        """Loads data from a JSON file. Returns an empty list if it fails."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def guardar_datos(self, data, filepath):
        """Saves data to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def limpiar_pantalla(self):
        """Destroys the current frame to show a new one."""
        if self.frame_actual:
            self.frame_actual.destroy()

    # --- Main UI Navigation ---
    def mostrar_inicio(self):
        """Displays the main menu of the application."""
        self.limpiar_pantalla()
        self.frame_actual = tk.Frame(self)
        self.frame_actual.pack(pady=40, fill="both", expand=True)
        tk.Label(self.frame_actual, text="Almitas Peludas CRM", font=("Arial", 22, "bold")).pack(pady=20)

        tk.Button(self.frame_actual, text="✨ Ver Panel de Oportunidades", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", command=self.mostrar_panel_oportunidades).pack(pady=20, ipadx=20, ipady=15)
        tk.Button(self.frame_actual, text="🐾 Registrar Visita", font=("Arial", 14), command=self.seleccionar_lugar_para_registro).pack(pady=10, ipadx=20, ipady=10)

        tk.Label(self.frame_actual, text="--- Herramientas de Gestión ---", font=("Arial", 12, "italic")).pack(pady=(20, 5))
        tk.Button(self.frame_actual, text="📚 Gestionar Contenido", font=("Arial", 14), command=self.mostrar_gestor_contenido).pack(pady=10, ipadx=20, ipady=10)
        tk.Button(self.frame_actual, text="✏️ Gestionar Plantillas", font=("Arial", 14), command=self.mostrar_gestor_plantillas).pack(pady=10, ipadx=20, ipady=10)

    # --- Opportunities Panel ---
    def mostrar_panel_oportunidades(self):
        """Displays the main opportunities panel with tabs."""
        self.limpiar_pantalla()
        self.frame_actual = tk.Frame(self)
        self.frame_actual.pack(pady=20, fill="both", expand=True)
        tk.Label(self.frame_actual, text="Panel de Oportunidades", font=("Arial", 18, "bold")).pack(pady=10)

        notebook = ttk.Notebook(self.frame_actual)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)

        f1 = ttk.Frame(notebook); notebook.add(f1, text='Recordatorios 🗓️')
        self.crear_pestaña_oportunidad(f1, "recordatorios")

        f2 = ttk.Frame(notebook); notebook.add(f2, text='Campañas 🎯')
        self.crear_pestaña_campañas(f2)

        f3 = ttk.Frame(notebook); notebook.add(f3, text='Contenido de Valor 💡')
        self.crear_pestaña_oportunidad(f3, "contenido")

        tk.Button(self.frame_actual, text="Refrescar Sugerencias", command=self.refrescar_oportunidades).pack(side=tk.LEFT, padx=20, pady=10)
        tk.Button(self.frame_actual, text="Volver al Inicio", command=self.mostrar_inicio).pack(side=tk.RIGHT, padx=20, pady=10)

        self.refrescar_oportunidades()

    def crear_pestaña_oportunidad(self, parent, tipo):
        """Creates a generic tab with a listbox and a generate button."""
        list_frame = tk.Frame(parent); list_frame.pack(pady=10, padx=10, fill="both", expand=True)
        scrollbar = Scrollbar(list_frame); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 12)); listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        setattr(self, f"listbox_{tipo}", listbox)
        tk.Button(parent, text="Generar Mensaje para Selección", font=("Arial", 12, "bold"), command=lambda: self.generar_mensaje(tipo)).pack(pady=10)

    def crear_pestaña_campañas(self, parent):
        """Creates the specific campaigns tab with an extra button."""
        list_frame = tk.Frame(parent); list_frame.pack(pady=10, padx=10, fill="both", expand=True)
        scrollbar = Scrollbar(list_frame); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox = Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 12)); listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        setattr(self, "listbox_campañas", listbox)
        btn_frame = tk.Frame(parent); btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Generar Mensaje", font=("Arial", 12, "bold"), command=lambda: self.generar_mensaje("campañas")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Crear Campaña por Tags", font=("Arial", 12), command=self.crear_campaña_por_tags).pack(side=tk.LEFT, padx=10)

    def refrescar_oportunidades(self):
        """Main function to find and display all opportunities."""
        self.oportunidades_actuales = {"recordatorios": [], "campañas": [], "contenido": []}
        self.poblar_listbox("recordatorios", self.buscar_recordatorios_servicio() + self.buscar_recordatorios_producto())
        self.poblar_listbox("campañas", self.buscar_clientes_inactivos() + self.buscar_cumpleaños())
        self.poblar_listbox("contenido", self.sugerir_contenido_general())

    def poblar_listbox(self, tipo, oportunidades):
        """Clears and populates a listbox with opportunities."""
        listbox = getattr(self, f"listbox_{tipo}")
        listbox.delete(0, tk.END)
        self.oportunidades_actuales[tipo] = oportunidades
        if not oportunidades:
            listbox.insert(tk.END, "No hay sugerencias por ahora.")
            return
        for i, op in enumerate(oportunidades):
            listbox.insert(tk.END, op['texto_display'])
            listbox.itemconfig(i, {'bg': '#f0f0f0' if i % 2 == 0 else 'white'})

    # --- Opportunity Logic Functions ---
    def parse_duracion(self, duracion_str):
        """Parses a string like '6 weeks' into a timedelta object."""
        if not isinstance(duracion_str, str): return None
        num_match = re.search(r'\d+', duracion_str)
        if not num_match: return None
        num = int(num_match.group(0))
        if "semana" in duracion_str: return datetime.timedelta(weeks=num)
        if "mes" in duracion_str: return datetime.timedelta(days=num * 30)
        if "dia" in duracion_str: return datetime.timedelta(days=num)
        return None

    def buscar_recordatorios_servicio(self):
        ops = []; hoy = datetime.date.today()
        for p in self.lista_de_perros:
            if not p.get("Frecuencia Visita") or not p.get("Visitas"): continue
            delta = self.parse_duracion(p["Frecuencia Visita"])
            if not delta: continue
            ultima_visita = max(v['Fecha'] for v in p['Visitas'])
            prox_visita = datetime.datetime.fromisoformat(ultima_visita).date() + delta
            if hoy >= prox_visita - datetime.timedelta(weeks=1):
                ops.append({"tipo": "recordatorio_servicio", "texto_display": f"Visita para {p['Nombre']} (prox. {prox_visita.strftime('%d-%m')})", "mascota": p})
        return ops

    def buscar_recordatorios_producto(self):
        ops = []; hoy = datetime.date.today()
        for p in self.lista_de_perros:
            if not p.get("Visitas"): continue
            for v in p["Visitas"]:
                for prod in v.get("Productos Comprados", []):
                    delta = self.parse_duracion(prod.get("Duracion Estimada"))
                    if not delta: continue
                    fin_prod = datetime.datetime.fromisoformat(v['Fecha']).date() + delta
                    if hoy >= fin_prod - datetime.timedelta(days=7):
                        ops.append({"tipo": "recordatorio_producto", "texto_display": f"Reponer '{prod['Nombre Producto']}' a {p['Nombre']}", "mascota": p, "producto": prod})
        return ops

    def buscar_clientes_inactivos(self, meses=3):
        ops = []; limite = datetime.date.today() - datetime.timedelta(days=meses * 30)
        for p in self.lista_de_perros:
            if not p.get("Visitas"): continue
            ultima_visita = datetime.datetime.fromisoformat(max(v['Fecha'] for v in p['Visitas'])).date()
            if ultima_visita < limite:
                ops.append({"tipo": "campaña_inactividad", "texto_display": f"Reactivar a {p['Nombre']} (últ. visita {ultima_visita.strftime('%d-%m-%Y')})", "mascota": p})
        return ops

    def buscar_cumpleaños(self):
        ops = []; mes_actual_num = datetime.date.today().month
        meses_es = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
        for p in self.lista_de_perros:
            cumple = p.get("Cumpleaños", "").lower()
            if any(mes in cumple for mes in [str(mes_actual_num), meses_es[mes_actual_num - 1]]):
                 ops.append({"tipo": "campaña_cumpleaños", "texto_display": f"Felicitar a {p['Nombre']} por su cumple!", "mascota": p})
        return ops

    def crear_campaña_por_tags(self):
        tag = simpledialog.askstring("Campaña por Tag", "Ingresa el tag a buscar:", parent=self)
        if not tag: return
        ops = []
        for p in self.lista_de_perros:
            for v in p.get("Visitas", []):
                if any(tag.lower() in str(t).lower() for t in v.get("Tags de Visita", [])):
                    ops.append({"tipo": "campaña_tags", "texto_display": f"Campaña '{tag}' para {p['Nombre']}", "mascota": p, "tag_encontrado": tag})
                    break
        self.poblar_listbox("campañas", ops)
        messagebox.showinfo("Búsqueda Completa", f"Se encontraron {len(ops)} mascotas con el tag '{tag}'.")

    def sugerir_contenido_general(self):
        if not self.lista_de_contenido: return []
        return [{"tipo": "contenido_general", "texto_display": f"Enviar a todos: '{c['titulo']}'", "contenido": c} for c in self.lista_de_contenido]

    # --- Message Generation ---
    def generar_mensaje(self, tipo):
        """Generates a message based on the selected opportunity and a template."""
        listbox = getattr(self, f"listbox_{tipo}")
        try:
            selected_index = listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("Error", "Por favor, selecciona una oportunidad de la lista.")
            return

        oportunidad = self.oportunidades_actuales[tipo][selected_index]
        template_name = oportunidad['tipo']

        # For "contenido_general", all pets get the same content, so we need a different flow
        if template_name == 'contenido_general':
             self.generar_mensaje_contenido_general(oportunidad)
             return

        template_obj = next((t for t in self.lista_de_plantillas if t.get("nombre") == template_name), None)
        if not template_obj:
            messagebox.showerror("Error", f"No se encontró una plantilla con el nombre '{template_name}'.\nPor favor, créala en 'Gestionar Plantillas'.")
            return

        template_text = template_obj['texto']
        final_message = self.poblar_plantilla(template_text, oportunidad)
        self.mostrar_mensaje_final(final_message, f"Mensaje para {oportunidad['mascota'].get('Nombre')}")

    def generar_mensaje_contenido_general(self, oportunidad):
        """Special handler for 'send to all' content opportunities."""
        template_name = "contenido_general"
        template_obj = next((t for t in self.lista_de_plantillas if t.get("nombre") == template_name), None)
        if not template_obj:
            messagebox.showerror("Error", f"No se encontró la plantilla '{template_name}'.")
            return

        full_text = f"--- CAMPAÑA DE CONTENIDO: {oportunidad['contenido']['titulo']} ---\n"
        full_text += "--- Enviar un mensaje a cada uno de los siguientes clientes ---\n\n"

        for perro in self.lista_de_perros:
             oportunidad_individual = {"mascota": perro, "contenido": oportunidad["contenido"]}
             msg = self.poblar_plantilla(template_obj['texto'], oportunidad_individual)
             full_text += f"Para: {perro.get('Nombre del Dueño', 'N/A')} (Mascota: {perro.get('Nombre')})\n"
             full_text += f"Mensaje: {msg}\n"
             full_text += "------------------------------------------------------\n"

        self.mostrar_mensaje_final(full_text, "Campaña de Contenido General")

    def poblar_plantilla(self, template_text, oportunidad):
        """Replaces placeholders in a template with actual data."""
        final_message = template_text
        if "mascota" in oportunidad:
            mascota = oportunidad['mascota']
            final_message = final_message.replace("[NombreMascota]", mascota.get("Nombre", ""))
            final_message = final_message.replace("[NombreDueño]", mascota.get("Nombre del Dueño", "dueño/a"))
            if mascota.get("Visitas"):
                ultima_visita = max(mascota["Visitas"], key=lambda v: v["Fecha"])
                final_message = final_message.replace("[FechaUltimaVisita]", ultima_visita.get("Fecha", ""))
        if "producto" in oportunidad:
            final_message = final_message.replace("[ProductoComprado]", oportunidad["producto"].get("Nombre Producto", ""))
        if "contenido" in oportunidad:
            final_message = final_message.replace("[TituloContenido]", oportunidad["contenido"].get("titulo", ""))
            final_message = final_message.replace("[TextoContenido]", oportunidad["contenido"].get("texto", ""))
        return final_message

    def mostrar_mensaje_final(self, message, title="Mensaje Generado"):
        """Displays the final message in a new, copy-friendly window."""
        dialog = Toplevel(self); dialog.title(title); dialog.geometry("450x350")
        tk.Label(dialog, text="Copia el siguiente mensaje:", font=("Arial", 12)).pack(pady=10)
        text_widget = tk.Text(dialog, wrap=tk.WORD, font=("Arial", 11), height=10); text_widget.pack(pady=5, padx=10, fill="both", expand=True)
        text_widget.insert("1.0", message); text_widget.config(state="disabled")
        tk.Button(dialog, text="Cerrar", command=dialog.destroy).pack(pady=10)
        dialog.transient(self); dialog.grab_set(); self.wait_window(dialog)

    # --- Registration and Data Entry Flow ---
    def seleccionar_lugar_para_registro(self):
        self.limpiar_pantalla(); self.frame_actual=tk.Frame(self); self.frame_actual.pack(pady=50)
        tk.Label(self.frame_actual,text="¿Dónde estás trabajando?",font=("Arial",16)).pack(pady=20)
        tk.Button(self.frame_actual,text="🐾 Almitas Peludas",font=("Arial",14),command=lambda:self.mostrar_registro_perro("Almitas Peludas")).pack(pady=10,ipadx=20,ipady=10)
        tk.Button(self.frame_actual,text="🏢 Local",font=("Arial",14),command=lambda:self.mostrar_registro_perro("Local")).pack(pady=10,ipadx=20,ipady=10)
        tk.Button(self.frame_actual,text="Volver al Inicio",command=self.mostrar_inicio).pack(pady=30)

    def mostrar_registro_perro(self,lugar):
        self.limpiar_pantalla(); self.datos_perro_actual={"Lugar":lugar}; self.frame_actual=tk.Frame(self); self.frame_actual.pack(pady=50)
        tk.Label(self.frame_actual,text=f"Registrando en {lugar}",font=("Arial",16)).pack(pady=10)
        tk.Label(self.frame_actual,text="Nombre del perro:",font=("Arial",12)).pack(); self.nombre_entry=tk.Entry(self.frame_actual,font=("Arial",12)); self.nombre_entry.pack(pady=5)
        tk.Button(self.frame_actual,text="Siguiente",command=self.mostrar_detalles).pack(pady=20,ipadx=10,ipady=5)

    def mostrar_detalles(self):
        nombre=self.nombre_entry.get();
        if not nombre: messagebox.showerror("Error","Ingresa el nombre."); return
        self.datos_perro_actual["Nombre"]=nombre; self.limpiar_pantalla(); self.frame_actual=tk.Frame(self); self.frame_actual.pack(pady=20)
        tk.Label(self.frame_actual,text=f"Detalles de {nombre}",font=("Arial",16)).pack(pady=10)

        tk.Label(self.frame_actual,text="--- Datos Permanentes ---",font=("Arial",10,"italic")).pack(pady=5)
        perm_buttons = [("Nombre del Dueño 🧑", "Nombre del Dueño"), ("Raza 🐕‍🦺", "Raza"), ("Edad 👴", "Edad"),
                        ("Cumpleaños 🎂", "Cumpleaños"), ("Frecuencia Visita 🗓️", "Frecuencia Visita"), ("Tags Permanentes 🏷️", "Tags Permanentes")]
        for text, tipo in perm_buttons:
            tk.Button(self.frame_actual,text=text,command=lambda t=tipo:self.actualizar_dato(t)).pack(pady=2,fill=tk.X,padx=50)

        tk.Label(self.frame_actual,text="--- Datos de esta Visita ---",font=("Arial",10,"italic")).pack(pady=(15,5))
        visit_buttons = [("Nudos 🧶","Nudos"),("Uñas 💅","Uñas"),("Estado general ❤️‍🩹","Estado General"),("Tags de Visita 📝","Tags de Visita")]
        for text, tipo in visit_buttons:
            tk.Button(self.frame_actual,text=text,command=lambda t=tipo:self.actualizar_dato(t)).pack(pady=2,fill=tk.X,padx=50)

        tk.Button(self.frame_actual,text="Venta de Producto 🛍️",command=self.registrar_venta_producto).pack(pady=2,fill=tk.X,padx=50)
        tk.Button(self.frame_actual,text="Finalizar Registro",command=self.finalizar_registro, font=("Arial", 12, "bold")).pack(pady=15,ipadx=15,ipady=7)

    def registrar_venta_producto(self):
        nombre_p=simpledialog.askstring("Venta","Nombre del producto:",parent=self);
        if not nombre_p: return
        duracion=simpledialog.askstring("Venta",f"Duración para '{nombre_p}':",parent=self) or "N/A"
        self.datos_perro_actual.setdefault("productos_vendidos_temp",[]).append({"Nombre Producto":nombre_p,"Duracion Estimada":duracion})
        messagebox.showinfo("Venta Registrada",f"Producto '{nombre_p}' añadido.")

    def actualizar_dato(self, tipo):
        valor=None
        prompts = {
            "Nombre del Dueño": "Nombre del dueño:", "Raza": "Ingresa la raza:", "Edad": "Ingresa la edad (en años):",
            "Cumpleaños": "Ingresa la fecha o mes (ej: '14 de Julio'):", "Frecuencia Visita": "Ingresa la frecuencia (ej: '6 semanas'):",
            "Tags Permanentes": "Tags permanentes separados por coma:", "Estado General": "Describe el estado general:",
            "Tags de Visita": "Tags de esta visita separados por coma:"
        }
        if tipo == "Edad": valor = simpledialog.askinteger(tipo, prompts[tipo], parent=self)
        elif tipo in ["Nudos", "Uñas"]: valor = "Sí" if messagebox.askyesno(tipo, f"¿{tipo}?", parent=self) else "No"
        elif tipo in ["Tags Permanentes", "Tags de Visita"]:
            tags_str = simpledialog.askstring(tipo, prompts[tipo], parent=self)
            if tags_str: valor = [tag.strip() for tag in tags_str.split(',')]
        else: valor = simpledialog.askstring(tipo, prompts.get(tipo, "Ingresa el dato:"), parent=self)

        if valor in (None, ""): return
        self.datos_perro_actual[tipo]=valor
        messagebox.showinfo("Dato registrado",f"{tipo}: {valor}")

    def finalizar_registro(self):
        nombre_mascota=self.datos_perro_actual.get("Nombre")
        if not nombre_mascota: messagebox.showerror("Error","No se encontró el nombre."); return

        perm_keys = ["Nombre del Dueño", "Raza", "Edad", "Cumpleaños", "Frecuencia Visita", "Tags Permanentes"]
        datos_permanentes={k:self.datos_perro_actual.get(k) for k in perm_keys if self.datos_perro_actual.get(k) is not None}

        visit_keys = ["Lugar", "Nudos", "Uñas", "Estado General", "Tags de Visita"]
        datos_visita={k:self.datos_perro_actual.get(k) for k in visit_keys if self.datos_perro_actual.get(k) is not None}
        datos_visita["Fecha"]=datetime.date.today().isoformat()
        datos_visita["Productos Comprados"]=self.datos_perro_actual.get("productos_vendidos_temp",[])

        mascota_existente=next((m for m in self.lista_de_perros if m.get("Nombre") == nombre_mascota), None)
        if mascota_existente:
            mascota_existente.update(datos_permanentes)
            mascota_existente.setdefault("Visitas",[]).append(datos_visita)
            mensaje=f"Nueva visita añadida para {nombre_mascota}."
        else:
            nuevo_registro={"Nombre":nombre_mascota,"Visitas":[datos_visita],**datos_permanentes}
            self.lista_de_perros.append(nuevo_registro)
            mensaje=f"Nueva mascota registrada: {nombre_mascota}."

        self.guardar_datos(self.lista_de_perros, self.data_file)

        self.limpiar_pantalla(); self.frame_actual=tk.Frame(self); self.frame_actual.pack(pady=50)
        tk.Label(self.frame_actual,text="¡Registro Guardado!",font=("Arial",16,"bold")).pack(pady=20)
        tk.Label(self.frame_actual,text=mensaje,font=("Arial",12)).pack(pady=10)
        resumen_txt = "\n".join([f"{k}: {v}" for k,v in datos_visita.items() if v])
        tk.Label(self.frame_actual,text=f"Resumen de la visita:\n{resumen_txt}",font=("Arial",10),justify=tk.LEFT).pack(pady=5)
        tk.Button(self.frame_actual,text="Registrar Otro",command=self.mostrar_inicio).pack(pady=20,ipadx=10,ipady=5)

    # --- Management Screens (Content and Templates) ---
    def mostrar_gestor_contenido(self):
        self._mostrar_gestor_base("Contenido", self.lista_de_contenido, self.content_file, self.refrescar_lista_contenido, self.editar_contenido, self.eliminar_contenido, self.añadir_contenido)
    def mostrar_gestor_plantillas(self):
        self._mostrar_gestor_base("Plantillas", self.lista_de_plantillas, self.templates_file, self.refrescar_lista_plantillas, self.editar_plantilla, self.eliminar_plantilla, self.añadir_plantilla)

    def _mostrar_gestor_base(self, nombre, lista, filepath, refresher, editor, eliminator, adder):
        self.limpiar_pantalla(); self.frame_actual=tk.Frame(self); self.frame_actual.pack(pady=20,fill="both",expand=True)
        tk.Label(self.frame_actual,text=f"Biblioteca de {nombre}",font=("Arial",16,"bold")).pack()
        list_frame=tk.Frame(self.frame_actual); list_frame.pack(pady=10,fill="both",expand=True); scrollbar=Scrollbar(list_frame); scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        listbox=Listbox(list_frame,yscrollcommand=scrollbar.set,font=("Arial",12)); listbox.pack(side=tk.LEFT,fill="both",expand=True); scrollbar.config(command=listbox.yview)
        setattr(self, f"{nombre.lower()}_listbox", listbox)
        refresher()
        btn_frame=tk.Frame(self.frame_actual); btn_frame.pack(pady=10)
        tk.Button(btn_frame,text="Añadir",command=adder).pack(side=tk.LEFT,padx=10)
        tk.Button(btn_frame,text="Editar",command=editor).pack(side=tk.LEFT,padx=10)
        tk.Button(btn_frame,text="Eliminar",command=eliminator).pack(side=tk.LEFT,padx=10)
        tk.Button(self.frame_actual,text="Volver",command=self.mostrar_inicio).pack(pady=10)

    def refrescar_lista_contenido(self): self.contenido_listbox.delete(0,tk.END); [self.contenido_listbox.insert(tk.END,i.get("titulo")) for i in self.lista_de_contenido]
    def refrescar_lista_plantillas(self): self.plantillas_listbox.delete(0,tk.END); [self.plantillas_listbox.insert(tk.END,i.get("nombre")) for i in self.lista_de_plantillas]

    def añadir_contenido(self): self._editar_o_añadir_item(self.lista_de_contenido, self.content_file, self.refrescar_lista_contenido, "contenido")
    def editar_contenido(self): self._editar_o_añadir_item(self.lista_de_contenido, self.content_file, self.refrescar_lista_contenido, "contenido", self.contenido_listbox)
    def eliminar_contenido(self): self._eliminar_item(self.lista_de_contenido, self.content_file, self.refrescar_lista_contenido, "contenido", self.contenido_listbox)

    def añadir_plantilla(self): self._editar_o_añadir_item(self.lista_de_plantillas, self.templates_file, self.refrescar_lista_plantillas, "plantilla")
    def editar_plantilla(self): self._editar_o_añadir_item(self.lista_de_plantillas, self.templates_file, self.refrescar_lista_plantillas, "plantilla", self.plantillas_listbox)
    def eliminar_plantilla(self): self._eliminar_item(self.lista_de_plantillas, self.templates_file, self.refrescar_lista_plantillas, "plantilla", self.plantillas_listbox)

    def _editar_o_añadir_item(self, data_list, filepath, refresher, item_type, listbox=None):
        index = None
        if listbox: # Modo edición
            try: index = listbox.curselection()[0]
            except IndexError: messagebox.showwarning("Error", "Selecciona un item para editar."); return
            item = data_list[index]
        else: # Modo añadir
            item = {}

        if item_type == "contenido":
            key1, key2, prompt2 = "titulo", "texto", "Texto del consejo:"
        else: # plantilla
            key1, key2, prompt2 = "nombre", "texto", "Texto de la plantilla (usa [NombreMascota], etc.):\n\nVariables: [NombreMascota], [NombreDueño], [FechaUltimaVisita], [ProductoComprado], [TituloContenido], [TextoContenido]"

        val1 = simpledialog.askstring(f"Editar {item_type}", f"{key1.capitalize()}:", initialvalue=item.get(key1, ""), parent=self)
        if not val1: return
        val2 = self.ask_multiline_string(f"Editar {item_type}", prompt2, initialvalue=item.get(key2, ""))
        if not val2: return

        new_item = {key1: val1, key2: val2}
        if index is not None: data_list[index] = new_item
        else: data_list.append(new_item)

        self.guardar_datos(data_list, filepath); refresher()

    def _eliminar_item(self, data_list, filepath, refresher, item_type, listbox):
        try: index = listbox.curselection()[0]
        except IndexError: messagebox.showwarning("Error", f"Selecciona un {item_type} para eliminar."); return
        key = "titulo" if item_type == "contenido" else "nombre"
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{data_list[index].get(key)}'?"):
            del data_list[index]
            self.guardar_datos(data_list, filepath); refresher()

    def ask_multiline_string(self, title, prompt, initialvalue=""):
        dialog = Toplevel(self); dialog.title(title); dialog.geometry("450x350");
        tk.Label(dialog, text=prompt, justify=tk.LEFT).pack(pady=5)
        text_widget = tk.Text(dialog, wrap=tk.WORD, font=("Arial", 11)); text_widget.pack(pady=5, padx=10, fill="both", expand=True)
        text_widget.insert("1.0", initialvalue)
        result = None
        def on_ok():
            nonlocal result
            result = text_widget.get("1.0", tk.END).strip()
            dialog.destroy()
        ok_btn = tk.Button(dialog, text="OK", command=on_ok); ok_btn.pack(pady=10)
        dialog.transient(self); dialog.grab_set(); self.wait_window(dialog)
        return result

if __name__ == "__main__":
    app = AlmitasPeludasApp()
    app.mainloop()