import csv
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime
import re
from fpdf import FPDF
import threading


class AprendizRegistro:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Registro de Aprendices Sena Sede Manare")
        self.root.iconbitmap("logo-del-sena-ico.ico")
        self.conn = sqlite3.connect('tu_base_de_datos.db')
        self.pagina_actual = 1
        self.registros_por_pagina = 10  # Cantidad de registros a mostrar por página
        

        # Establecer el estilo
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12), foreground="black")
        self.style.configure("TButton", font=("Arial", 12), padding=10)
        self.style.configure("TCombobox", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))
        self.style.configure("TFrame", background="lightgrey")

        # Crear un contenedor principal
        self.canvas = tk.Canvas(self.root, background="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Agregar scrollbar vertical que controle el canvas
        self.scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configurar la scrollbar para el canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Crear un frame dentro del canvas
        self.scrollable_frame = tk.Frame(self.canvas)

        # Agregar el frame dentro del canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configurar que la scrollbar aparezca solo cuando sea necesario
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Variables
        self.nombre_entry_var = tk.StringVar()
        self.nueva_titulada_entry_var = tk.StringVar()
        self.titulada_var = tk.StringVar()
        self.eliminar_titulada_var = tk.StringVar()
        self.buscar_titulada_var = tk.StringVar()
        self.fecha_inicio_var = tk.StringVar()
        self.fecha_fin_var = tk.StringVar()
        self.eliminar_aprendiz_var = tk.StringVar()
        self.historial_acciones = []

        # Frame principal
        self.main_frame = tk.Frame(self.scrollable_frame, background="lightgrey")
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configurar la ventana para que se ajuste automáticamente
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


        # Crear el Combobox y asignarlo a self.aprendiz_combobox
        self.aprendiz_combobox = ttk.Combobox(self.root, state="readonly")
        self.aprendiz_combobox.pack()
        
        # Asegúrate de llamar a actualizar_aprendices_combobox después de crear el Combobox
        self.actualizar_aprendices_combobox()

        # Crear los widgets
        self.crear_widgets()

        # Pie de marca
        self.crear_marca()

        # Iniciar el loop principal de la ventana
        self.root.mainloop()


        # Crear las tablas si no existen
        self.crear_tablas()

        

    def crear_tablas(self):
        # Crear las tablas
        self.conn.execute('''
            CREATE TABLE aprendices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                titulada TEXT NOT NULL,
                fecha_registro DATE NOT NULL
            )
        ''')
    
        self.conn.execute('''
            CREATE TABLE tituladas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_titulada TEXT NOT NULL
            )
        ''')
    
        self.conn.commit()


    def validar_nombre(self, nombre):
        """
        Valida que el nombre solo contenga letras y espacios.
        Retorna True si es válido, False en caso contrario.
        """
        if all(char.isalpha() or char.isspace() for char in nombre):
            return True
        return False

    def validar_fecha(self, fecha):
        """
        Valida que la fecha esté en el formato correcto (YYYY-MM-DD).
        Retorna True si es válida, False en caso contrario.
        """
        try:
            datetime.datetime.strptime(fecha, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def obtener_aprendices(self):
        try:
            return self.conn.execute('SELECT id, nombre, titulada, fecha_registro FROM aprendices').fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener aprendices: {e}")
            return []

    def actualizar_aprendices(self):
        """Actualizar la lista de aprendices en el Treeview."""
        aprendices = self.obtener_aprendices()  # Obtener datos desde la base de datos
        self.eliminar_aprendiz_option['values'] = [aprendiz[1] for aprendiz in aprendices]  # Actualiza el combobox para eliminar aprendices

        # Limpiar el Treeview antes de insertar nuevos datos
        self.resultado_tree.delete(*self.resultado_tree.get_children())

        # Insertar nuevos datos
        for aprendiz in aprendices:
            self.resultado_tree.insert("", tk.END, values=aprendiz)

    def actualizar_treeview(self):
        """Actualizar el TreeView con los aprendices registrados."""
        self.treeview.delete(*self.treeview.get_children())  # Limpiar el TreeView
        aprendices = self.conn.execute("""
            SELECT aprendices.nombre, tituladas.nombre_titulada, aprendices.fecha_registro
            FROM aprendices
            JOIN tituladas ON aprendices.titulada = tituladas.id
        """).fetchall()

        for aprendiz in aprendices:
            self.treeview.insert("", "end", values=(aprendiz[0], aprendiz[1], aprendiz[2]))

    def mostrar_pagina(self, pagina):
        """Mostrar registros en función de la paginación."""
        self.pagina_actual = pagina  # Actualizar la página actual
        inicio, limite = self.calcular_limites_pagina(pagina)  # Cambia a usar la nueva función

        try:
            # Consultar los datos de aprendices para la página actual
            cursor = self.conn.cursor()
            cursor.execute("SELECT nombre, titulada, fecha_registro FROM aprendices LIMIT ?, ?", (inicio, limite))
            rows = cursor.fetchall()

            # Limpiar el TreeView antes de mostrar nuevos resultados
            self.resultado_tree.delete(*self.resultado_tree.get_children())

            # Insertar los registros en el TreeView
            for row in rows:
                self.resultado_tree.insert("", "end", values=row)

            # Actualizar los botones de navegación
            self.actualizar_botones_navegacion()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo mostrar la página: {e}")

    def calcular_limites_pagina(self, pagina_actual):
        inicio = (pagina_actual - 1) * self.registros_por_pagina
        return inicio, self.registros_por_pagina




    def pagina_anterior(self):
        """Muestra la página anterior."""
        if self.pagina_actual > 1:
            self.mostrar_pagina(self.pagina_actual - 1)

    def siguiente_pagina(self):
        """Muestra la siguiente página."""
        total_aprendices = len(self.obtener_aprendices())
        if self.pagina_actual * self.registros_por_pagina < total_aprendices:
            self.mostrar_pagina(self.pagina_actual + 1)

    def crear_widgets(self):
        # Sección 1: Registro de Aprendices
        registro_frame = tk.LabelFrame(self.main_frame, text="Registro de Aprendices", background="lightgrey", font=("Arial", 14))
        registro_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        registro_frame.grid_columnconfigure(1, weight=1)  # Permitir que la columna 1 se expanda
        tk.Label(registro_frame, text="Nombre del Aprendiz:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nombre_entry = tk.Entry(registro_frame, textvariable=self.nombre_entry_var)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(registro_frame, text="Titulada:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.titulada_option = ttk.Combobox(registro_frame, textvariable=self.titulada_var)
        self.titulada_option.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(registro_frame, text="Registrar Aprendiz", command=self.registrar_aprendiz).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # Sección 2: Gestión de Tituladas
        tituladas_frame = tk.LabelFrame(self.main_frame, text="Gestión de Tituladas", background="lightgrey", font=("Arial", 14))
        tituladas_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tituladas_frame.grid_columnconfigure(1, weight=1)

        tk.Label(tituladas_frame, text="Nueva Titulada:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.nueva_titulada_entry = tk.Entry(tituladas_frame, textvariable=self.nueva_titulada_entry_var)
        self.nueva_titulada_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(tituladas_frame, text="Agregar Titulada", command=self.agregar_titulada).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Label(tituladas_frame, text="Nombre de la Titulada a Eliminar:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.eliminar_titulada_entry = tk.Entry(tituladas_frame, textvariable=self.eliminar_titulada_var)
        self.eliminar_titulada_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(tituladas_frame, text="Eliminar Titulada", command=self.eliminar_titulada).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        # Sección 3: Buscar Aprendices
        buscar_frame = tk.LabelFrame(self.main_frame, text="Buscar Aprendices", background="lightgrey", font=("Arial", 14))
        buscar_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        buscar_frame.grid_columnconfigure(1, weight=1)

        tk.Label(buscar_frame, text="Buscar por Titulada:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.buscar_titulada_option = ttk.Combobox(buscar_frame, textvariable=self.buscar_titulada_var)
        self.buscar_titulada_option.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(buscar_frame, text="Buscar", command=self.buscar_por_titulada).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        # 4. Área de resultados con Scrollbar (Text widget)
        tk.Label(buscar_frame, text="Resultados:").grid(row=2, column=0, padx=5, pady=5)

        # Frame para el área de resultados con Scrollbar
        resultado_frame = tk.Frame(buscar_frame, background="lightgrey")
        resultado_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        resultado_frame.grid_columnconfigure(0, weight=1)

        # Crear un Text con Scrollbar
        self.resultado_titulada_text = tk.Text(resultado_frame, height=5, width=40)
        scrollbar_text = tk.Scrollbar(resultado_frame, command=self.resultado_titulada_text.yview)
        self.resultado_titulada_text.config(yscrollcommand=scrollbar_text.set)

        self.resultado_titulada_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_text.pack(side=tk.RIGHT, fill=tk.Y)

        # Sección 5: Buscar Aprendices por Fecha
        fecha_frame = tk.LabelFrame(self.main_frame, text="Buscar Aprendices por Fecha", background="lightgrey", font=("Arial", 14))
        fecha_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        fecha_frame.grid_columnconfigure(1, weight=1)

        tk.Label(fecha_frame, text="Fecha Inicio (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.fecha_inicio_entry = tk.Entry(fecha_frame, textvariable=self.fecha_inicio_var)
        self.fecha_inicio_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(fecha_frame, text="Fecha Fin (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.fecha_fin_entry = tk.Entry(fecha_frame, textvariable=self.fecha_fin_var)
        self.fecha_fin_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(fecha_frame, text="Buscar por Fecha", command=self.buscar_por_fecha).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # Sección 6: Eliminar Aprendiz
        eliminar_frame = tk.LabelFrame(self.main_frame, text="Eliminar Aprendiz", background="lightgrey", font=("Arial", 14))
        eliminar_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        eliminar_frame.grid_columnconfigure(1, weight=1)

        

        tk.Button(eliminar_frame, text="Eliminar Aprendiz", command=self.eliminar_aprendiz).grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        # Sección 7: Listado de Aprendices
        listado_frame = tk.LabelFrame(self.main_frame, text="Listado de Aprendices", background="lightgrey", font=("Arial", 14))
        listado_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew")

        columnas = ("Nombre", "Titulada", "Fecha de Registro")
        self.resultado_tree = ttk.Treeview(listado_frame, columns=columnas, show="headings")
        for col in columnas:
            self.resultado_tree.heading(col, text=col)

        # Scrollbar para el Treeview
        scrollbar_tree = tk.Scrollbar(listado_frame, orient="vertical", command=self.resultado_tree.yview)
        self.resultado_tree.configure(yscrollcommand=scrollbar_tree.set)

        # Empaquetar Treeview y su Scrollbar
        self.resultado_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)

        self.boton_anterior = tk.Button(self.main_frame, text="Anterior", command=self.pagina_anterior)
        self.boton_anterior.grid(row=6, column=0, padx=5, pady=10, sticky="ew")

        self.boton_siguiente = tk.Button(self.main_frame, text="Siguiente", command=self.siguiente_pagina)
        self.boton_siguiente.grid(row=6, column=1, padx=5, pady=10, sticky="ew")

        # Al iniciar la aplicación, muestra la primera página
        self.mostrar_pagina(1)

        # Sección 8: Exportar a CSV y PDF
        exportar_frame = tk.LabelFrame(self.main_frame, text="Exportar Datos", background="lightgrey", font=("Arial", 14))
        exportar_frame.grid(row=7, column=0, padx=10, pady=10, sticky="nsew")

        tk.Button(exportar_frame, text="Exportar a CSV", command=self.exportar_a_csv).grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        tk.Button(exportar_frame, text="Generar PDF", command=self.generar_pdf).grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Sección 9: Historial y estadísticas
        estadisticas_frame = tk.LabelFrame(self.main_frame, text="Historial y Estadísticas", background="lightgrey", font=("Arial", 14))
        estadisticas_frame.grid(row=8, column=0, padx=10, pady=10, sticky="nsew")

        tk.Button(estadisticas_frame, text="Ver Historial", command=self.ver_historial).grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        tk.Button(estadisticas_frame, text="Ver Estadísticas", command=self.mostrar_estadisticas).grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        # Ajustar el tamaño de la ventana
        self.root.geometry("880x600")
        self.root.configure(bg="lightgrey")

    def crear_marca(self):
        marca_frame = tk.Frame(self.scrollable_frame, bg="#d3d3d3")
        marca_frame.pack(side=tk.BOTTOM, fill="x")
        tk.Label(marca_frame, text="Fabian Daniel Hurtado Riscanebo © 2024", bg="#d3d3d3", font=("Arial", 10, "bold")).pack(pady=10)

    def seccion_frame(self, titulo, row):
        tk.Label(self.main_frame, text=titulo, font=("Arial", 12, "bold"), bg="#d3d3d3").grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")




    # Aquí irían las implementaciones de las funciones restantes como registrar_aprendiz, agregar_titulada, etc.


    def registrar_aprendiz(self):
        nombre = self.nombre_entry_var.get()
        titulada = self.titulada_var.get()
        
        if not nombre.strip():
            messagebox.showerror("Error", "El nombre no puede estar vacío o contener solo espacios.")
            return
        # Validar nombre y titulada
        if not nombre or not self.validar_nombre(nombre):
            messagebox.showerror("Error", "El nombre del aprendiz no es válido.")
            return
        if not titulada:
            messagebox.showerror("Error", "Por favor selecciona una titulada.")
            return

        # Guardar la fecha actual explícitamente
        fecha_registro = datetime.datetime.now().strftime("%Y-%m-%d")

        try:
            with self.conn:
                self.conn.execute('''
                    INSERT INTO aprendices (nombre, titulada, fecha_registro) 
                    VALUES (?, ?, ?)
                ''', (nombre, titulada, fecha_registro))
            messagebox.showinfo("Éxito", "Aprendiz registrado exitosamente.")
            self.actualizar_aprendices()
            self.actualizar_aprendices_combobox() # Actualizar el Combobox aquí
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo registrar el aprendiz: {e}")




    def agregar_titulada(self):
        nombre_titulada = self.nueva_titulada_entry_var.get()
        
        
        if not nombre_titulada or not self.validar_nombre(nombre_titulada):
           messagebox.showwarning("Advertencia", "El nombre de la titulada no puede estar vacío.")
           return
        if not nombre_titulada.strip():
            messagebox.showerror("Error", "El nombre no puede estar vacío o contener solo espacios.")
            return
        try:
            with self.conn:
                with self.conn:
                    self.conn.execute("INSERT INTO tituladas (nombre_titulada) VALUES (?)", (nombre_titulada,))
                    messagebox.showinfo("Éxito", "Titulada agregada exitosamente.")
                    self.nueva_titulada_entry_var.set("")  # Limpiar el Entry después de agregar
                    self.actualizar_tituladas_combobox()  # Actualizar el combobox de tituladas
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo agregar la titulada: {e}")


    def eliminar_titulada(self):
        titulada_seleccionada = self.eliminar_titulada_entry.get()  

        if titulada_seleccionada:
            # Lógica para eliminar la titulada de la base de datos o lista
            self.conn.execute("DELETE FROM tituladas WHERE nombre_titulada=?", (titulada_seleccionada,))
            self.conn.commit()
            self.actualizar_tituladas_combobox()  # Actualizar después de eliminar
            messagebox.showinfo("Eliminar Titulada", f"La titulada '{titulada_seleccionada}' ha sido eliminada.")
        else:
            messagebox.showerror("Error", "Debe ingresar un nombre de titulada para eliminar.")
   


    def eliminar_aprendiz(self):
        
        try:
            # Obtener el aprendiz seleccionado en el TreeView
            selected_item = self.resultado_tree.selection()[0]
            valores = self.resultado_tree.item(selected_item, 'values')
            nombre_aprendiz = valores[0]  # Asumimos que el nombre es el primer valor

            # Confirmar eliminación
            respuesta = messagebox.askyesno("Eliminar", f"¿seleccione el aprendiz para eliminar")
            respuesta = messagebox.askyesno("Eliminar", f"¿Estás seguro de que deseas eliminar a {nombre_aprendiz}?")
            if respuesta:
                # Eliminar el aprendiz de la base de datos
                with self.conn:
                    self.conn.execute('DELETE FROM aprendices WHERE nombre = ?', (nombre_aprendiz,))
                messagebox.showinfo("Éxito", "Aprendiz eliminado exitosamente.")
            
                # Actualizar la lista de aprendices automáticamente
                self.actualizar_aprendices()  # Actualiza la lista
                self.actualizar_aprendices_combobox()  # Actualizar el Combobox aquí
        except IndexError:
            messagebox.showerror("Error", "Por favor, selecciona un aprendiz para eliminar.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el aprendiz: {e}")


    def actualizar_tituladas(self):
        """Actualizar las opciones del Combobox con las tituladas en la base de datos."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre FROM tituladas")  # Asegúrate de que la tabla se llame 'tituladas'
        tituladas = [row[0] for row in cursor.fetchall()]

        # Limpiar las opciones actuales del Combobox y luego agregar las nuevas opciones
        self.titulada_combobox['values'] = tituladas
        if tituladas:
            self.titulada_combobox.current(0)  # Seleccionar la primera titulada por defecto (opcional)

    def actualizar_tituladas_combobox(self):
        """Actualizar el combobox de tituladas con los datos de la base de datos."""
        try:
            # Obtener las tituladas de la base de datos
            tituladas = self.conn.execute("SELECT nombre_titulada FROM tituladas").fetchall()
            # Limpiar el combobox actual
            self.titulada_option['values'] = [titulada[0] for titulada in tituladas]
            # Si hay tituladas, seleccionar la primera por defecto
            if tituladas:
                self.titulada_option.current(0)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar tituladas: {e}")



    def actualizar_aprendices(self):
        """Actualizar la lista de aprendices en el TreeView."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre, titulada, fecha_registro FROM aprendices")
        rows = cursor.fetchall()

        # Limpiar el TreeView antes de agregar nuevos datos
        self.resultado_tree.delete(*self.resultado_tree.get_children())

        # Insertar los registros actualizados en el TreeView
        for row in rows:
            self.resultado_tree.insert("", "end", values=row)

    def actualizar_aprendices_combobox(self):
        """Actualizar las opciones del Combobox con los aprendices en la base de datos."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre FROM aprendices")
        aprendices = [row[0] for row in cursor.fetchall()]

        # Limpiar las opciones actuales del Combobox y luego agregar los nuevos aprendices
        self.aprendiz_combobox['values'] = aprendices

        try:
            # Solo intenta seleccionar el primer elemento si hay aprendices
            if aprendices:
                self.aprendiz_combobox.current(0)  # Seleccionar el primer aprendiz por defecto (opcional)
            else:
                self.aprendiz_combobox.set("")  # Asegurarse de que esté vacío si no hay aprendices
        except IndexError:
            # Manejar el caso en el que no hay aprendices
             messagebox.showinfo("Información", "No hay aprendices registrados.")



    def buscar_por_titulada(self):
        titulada_a_buscar = self.buscar_titulada_var.get()
    
        if not titulada_a_buscar:
            messagebox.showwarning("Advertencia", "Seleccione una titulada para buscar.")
            return

        try:
            # Buscar aprendices por titulada
            aprendices = self.conn.execute('SELECT nombre FROM aprendices WHERE titulada = ?', (titulada_a_buscar,)).fetchall()
            self.resultado_titulada_text.delete(1.0, tk.END)  # Limpiar el área de texto

            if aprendices:
                for aprendiz in aprendices:
                    self.resultado_titulada_text.insert(tk.END, f"{aprendiz[0]}\n")
            else:
                self.resultado_titulada_text.insert(tk.END, "No se encontraron aprendices.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo buscar los aprendices: {e}")

        

    def buscar_por_fecha(self):
        fecha_inicio = self.fecha_inicio_entry.get()
        fecha_fin = self.fecha_fin_entry.get()

        try:
            # Validar formato de las fechas
            datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d")
            datetime.datetime.strptime(fecha_fin, "%Y-%m-%d")

            if not self.validar_fechas(fecha_inicio, fecha_fin):
                return

            # Buscar aprendices por rango de fechas
            aprendices = self.conn.execute(
                'SELECT nombre, fecha_registro FROM aprendices WHERE fecha_registro BETWEEN ? AND ?',
                (fecha_inicio, fecha_fin)).fetchall()
            
            # Muestra la primera página de los resultados
            self.mostrar_pagina(1)

            # Limpiar el Treeview antes de mostrar nuevos resultados
            self.resultado_tree.delete(*self.resultado_tree.get_children())

            for aprendiz in aprendices:
                self.resultado_tree.insert("", "end", values=(aprendiz[0], aprendiz[1]))

        except ValueError:
            messagebox.showerror("Error", "Las fechas deben estar en el formato YYYY-MM-DD.")


    def validar_fechas(self, fecha_inicio, fecha_fin):
        """Validar que las fechas no sean en el futuro y que la fecha de inicio no sea mayor a la de fin."""
        hoy = datetime.date.today()
        
        try:
            fecha_inicio_dt = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin_dt = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()

            if fecha_inicio_dt > hoy or fecha_fin_dt > hoy:
                messagebox.showerror("Error", "Las fechas no pueden ser en el futuro.")
                return False
            
            if fecha_inicio_dt > fecha_fin_dt:
                messagebox.showerror("Error", "La fecha de inicio no puede ser mayor que la fecha de fin.")
                return False
            
        except ValueError:
            messagebox.showerror("Error", "Las fechas deben estar en el formato YYYY-MM-DD.")
            return False
        
        return True
    

    def registrar_salida_titulada(self):
        titulada_a_buscar = self.buscar_titulada_var.get()
        
        if not titulada_a_buscar:
            messagebox.showwarning("Advertencia", "Seleccione una titulada para registrar salidas.")
            return

        try:
            with self.conn:
                self.conn.execute('DELETE FROM aprendices WHERE titulada = ?', (titulada_a_buscar,))
            messagebox.showinfo("Registro", "Salidas registradas exitosamente para la titulada seleccionada.")
            self.buscar_por_titulada()  # Actualizar la lista de aprendices
            self.registrar_accion("Registrar Salidas", {"titulada": titulada_a_buscar})  # Registrar acción
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar salidas: {e}")

    def mostrar_pagina(self, pagina):
        """Mostrar registros en función de la paginación."""
        self.pagina_actual = pagina  # Actualizar la página actual
        inicio = (pagina - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        
        # Consultar los datos de aprendices para la página actual
        cursor = self.conn.cursor()
        cursor.execute("SELECT nombre, titulada, fecha_registro FROM aprendices LIMIT ?, ?", (inicio, self.registros_por_pagina))
        rows = cursor.fetchall()

        # Limpiar el TreeView antes de mostrar nuevos resultados
        self.resultado_tree.delete(*self.resultado_tree.get_children())

        # Insertar los registros en el TreeView
        for row in rows:
            self.resultado_tree.insert("", "end", values=row)

        # Actualizar los botones de navegación
        self.actualizar_botones_navegacion()

    def siguiente_pagina(self):
        self.mostrar_pagina(self.pagina_actual + 1)

    def pagina_anterior(self):
        self.mostrar_pagina(max(1, self.pagina_actual - 1))

    def actualizar_botones_navegacion(self):
        total_registros = self.conn.execute("SELECT COUNT(*) FROM aprendices").fetchone()[0]
        total_paginas = (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina  # Cálculo de total de páginas

        # Habilitar o deshabilitar botones de navegación
        self.boton_anterior.config(state=tk.NORMAL if self.pagina_actual > 1 else tk.DISABLED)
        self.boton_siguiente.config(state=tk.NORMAL if self.pagina_actual < total_paginas else tk.DISABLED)


    def filtrar_treeview(self, event):
        """Filtrar registros en el TreeView basados en la búsqueda."""
        query = self.entrada_busqueda.get().lower()
        encontrado = False
        for fila in self.treeview.get_children():
            valores = self.treeview.item(fila)["values"]
            if query in str(valores).lower():
                self.treeview.selection_set(fila)
                encontrado = True
            else:
                self.treeview.selection_remove(fila)

        if not encontrado:
            messagebox.showinfo("Sin coincidencias", "No se encontraron resultados para la búsqueda.")


    def generar_pdf(self):
        try:
            # Consultar los datos de aprendices
            cursor = self.conn.cursor()
            cursor.execute("SELECT nombre, titulada, fecha_registro FROM aprendices")
            rows = cursor.fetchall()

            # Crear un objeto PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Títulos
            pdf.cell(200, 10, txt="Listado de Aprendices", ln=True, align='C')
            pdf.ln(10)

            # Encabezados
            pdf.cell(60, 10, "Nombre", 1)
            pdf.cell(60, 10, "Titulada", 1)
            pdf.cell(60, 10, "Fecha de Registro", 1)
            pdf.ln()

            # Datos
            for row in rows:
                pdf.cell(60, 10, row[0], 1)
                pdf.cell(60, 10, row[1], 1)
                pdf.cell(60, 10, row[2], 1)
                pdf.ln()

            # Guardar el archivo
            pdf.output("aprendices.pdf")
            messagebox.showinfo("Generar PDF", "El archivo PDF ha sido generado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {e}")


    def exportar_a_csv(self):
        try:
            # Consultar los datos de aprendices
            cursor = self.conn.cursor()
            cursor.execute("SELECT nombre, titulada, fecha_registro FROM aprendices")
            rows = cursor.fetchall()

            # Crear archivo CSV
            with open('aprendices.csv', 'w', newline='', encoding='utf-8') as csvfile:
               writer = csv.writer(csvfile)
               writer.writerow(['Nombre', 'Titulada', 'Fecha de Registro'])  # Encabezados
               writer.writerows(rows)  # Escribir datos

            messagebox.showinfo("Exportar CSV", "Los datos han sido exportados correctamente a 'aprendices.csv'.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV: {e}")

    def realizar_respaldo(self):
        """Realiza un respaldo de los datos de manera periódica."""
        threading.Timer(3600, self.realizar_respaldo).start()  # Realiza un respaldo cada hora

        try:
            cursor = self.conn.cursor()
            with open('respaldo.csv', 'w') as archivo:
                for fila in cursor.execute('SELECT * FROM aprendices'):
                    archivo.write(','.join(map(str, fila)) + '\n')
            messagebox.showinfo("Respaldo completado", "El respaldo de la base de datos se ha realizado correctamente.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al realizar el respaldo: {e}")


    def mostrar_estadisticas(self):
        """Mostrar estadísticas del número de aprendices registrados."""
        total_aprendices = len(self.resultado_tree.get_children())  # Contar los elementos en el TreeView
        messagebox.showinfo("Estadísticas", f"Total de aprendices registrados: {total_aprendices}")


    def registrar_accion(self, accion, datos):
        """Registrar una acción realizada en el historial."""
        self.historial_acciones.append({"accion": accion, "datos": datos, "fecha": datetime.datetime.now()})

    def ver_historial(self):
        """Ver el historial de acciones realizadas."""
        if not self.historial_acciones:
            messagebox.showinfo("Historial", "No hay acciones registradas.")
            return

        historial_texto = "\n".join([f"{registro['fecha']}: {registro['accion']} - {registro['datos']}" for registro in self.historial_acciones])
        messagebox.showinfo("Historial de Acciones", historial_texto)


    # Ejemplo para verificar los registros en la base de datos
    def verificar_registro(self):
        try:
            registros = self.conn.execute("SELECT * FROM aprendices").fetchall()
            print("Registros actuales en la base de datos:")
            for registro in registros:
                print(registro)
        except sqlite3.Error as e:
            print(f"Error al verificar registros: {e}")

    def verificar_datos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre, titulada, fecha_registro FROM aprendices")
        rows = cursor.fetchall()
        for row in rows:
            print(row)  # Imprimir resultados en la consola para depuración 

    def inicializar_interfaz(self):
        # Inicializar otros elementos...
    
        # Inicializar el Combobox de aprendices
        self.aprendiz_combobox = ttk.Combobox(self.root, state="readonly")
        self.aprendiz_combobox.pack()

        # Actualizar las opciones del Combobox al iniciar la aplicación
        self.actualizar_aprendices_combobox()

 

if __name__ == "__main__":
    app = AprendizRegistro()
    app.verificar_registro()  # Verificar si los aprendices están registrados en la base de datos
    app.root.mainloop()