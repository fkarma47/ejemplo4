import tkinter as tk
from tkinter import ttk

class PrestamoRegistro:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de control de préstamos de artículos")

        ## Crear frame para la entrada de datos
        self.frame_datos = tk.Frame(self.root)
        self.frame_datos.pack(fill="x")

        ## Crear etiquetas y entradas para la información del artículo
        self.label_placa = tk.Label(self.frame_datos, text="Placa:")
        self.label_placa.pack(side="left")
        self.entry_placa = tk.Entry(self.frame_datos, width=10)
        self.entry_placa.pack(side="left")

        self.label_objeto = tk.Label(self.frame_datos, text="Objeto:")
        self.label_objeto.pack(side="left")
        self.entry_objeto = tk.Entry(self.frame_datos, width=20)
        self.entry_objeto.pack(side="left")

        self.label_rol = tk.Label(self.frame_datos, text="Rol:")
        self.label_rol.pack(side="left")
        self.entry_rol = tk.Entry(self.frame_datos, width=10)
        self.entry_rol.pack(side="left")

        self.label_documento = tk.Label(self.frame_datos, text="Documento:")
        self.label_documento.pack(side="left")
        self.entry_documento = tk.Entry(self.frame_datos, width=15)
        self.entry_documento.pack(side="left")

        self.label_titulada = tk.Label(self.frame_datos, text="Titulada:")
        self.label_titulada.pack(side="left")
        self.entry_titulada = tk.Entry(self.frame_datos, width=10)
        self.entry_titulada.pack(side="left")

        self.label_fecha = tk.Label(self.frame_datos, text="Fecha:")
        self.label_fecha.pack(side="left")
        self.entry_fecha = tk.Entry(self.frame_datos, width=10)
        self.entry_fecha.pack(side="left")

        ## Crear botón para agregar préstamo
        self.boton_agregar = tk.Button(self.frame_datos, text="Agregar registro", command=self.agregar_registro)
        self.boton_agregar.pack(side="left")

        ## Crear botón para eliminar registro
        self.boton_eliminar = tk.Button(self.frame_datos, text="Eliminar registro", command=self.eliminar_registro)
        self.boton_eliminar.pack(side="left")

        ## Crear botón para actualizar registro
        self.boton_actualizar = tk.Button(self.frame_datos, text="Actualizar registro", command=self.actualizar_registro)
        self.boton_actualizar.pack(side="left")

        ## Crear frame para la lista de préstamos
        self.frame_lista = tk.Frame(self.root)
        self.frame_lista.pack(fill="both", expand=True)

        ## Crear treeview para la lista de préstamos
        self.treeview = ttk.Treeview(self.frame_lista, columns=("Placa", "Objeto", "Rol", "Documento", "Titulada", "Fecha"))
        self.treeview.pack(fill="both", expand=True)

        ## Configurar columnas del treeview
        self.treeview.column("#0", width=0, stretch=tk.NO)
        self.treeview.column("Placa", anchor=tk.W, width=100)
        self.treeview.column("Objeto", anchor=tk.W, width=200)
        self.treeview.column("Rol", anchor=tk.W, width=100)
        self.treeview.column("Documento", anchor=tk.W, width=150)
        self.treeview.column("Titulada", anchor=tk.W, width=100)
        self.treeview.column("Fecha", anchor=tk.W, width=100)

        ## Crear encabezados del treeview
        self.treeview.heading("#0", text="", anchor=tk.W)
        self.treeview.heading("Placa", text="Placa", anchor=tk.W)
        self.treeview.heading("Objeto", text="Objeto", anchor=tk.W)
        self.treeview.heading("Rol", text="Rol", anchor=tk.W)
        self.treeview.heading("Documento", text="Documento", anchor=tk.W)
        self.treeview.heading("Titulada", text="Titulada", anchor=tk.W)
        self.treeview.heading("Fecha", text="Fecha", anchor=tk.W)

    def agregar_registro(self):
        ## Obtener datos de la entrada
        placa = self.entry_placa.get()
        objeto = self.entry_objeto.get()
        rol = self.entry_rol.get()
        documento = self.entry_documento.get()
        titulada = self.entry_titulada.get()
        fecha = self.entry_fecha.get()

        ## Agregar préstamo a la lista
        self.treeview.insert("", "end", values=(placa, objeto, rol, documento, titulada, fecha))

        ## Limpiar entradas
        self.entry_placa.delete(0, tk.END)
        self.entry_objeto.delete(0, tk.END)
        self.entry_rol.delete(0, tk.END)
        self.entry_documento.delete(0, tk.END)
        self.entry_titulada.delete(0, tk.END)
        self.entry_fecha.delete(0, tk.END)

    def eliminar_registro(self):
        ## Obtener el índice del registro seleccionado
        seleccionado = self.treeview.selection()
        if seleccionado:
            ## Eliminar el registro seleccionado
            self.treeview.delete(seleccionado)

    def actualizar_registro(self):
        ## Obtener el índice del registro seleccionado
        seleccionado = self.treeview.selection()
        if seleccionado:
            ## Obtener los valores del registro seleccionado
            valores = self.treeview.item(seleccionado, "values")
            ## Actualizar los valores del registro seleccionado
            self.entry_placa.delete(0, tk.END)
            self.entry_placa.insert(0, valores[0])
            self.entry_objeto.delete(0, tk.END)
            self.entry_objeto.insert(0, valores[1])
            self.entry_rol.delete(0, tk.END)
            self.entry_rol.insert(0, valores[2])
            self.entry_documento.delete(0, tk.END)
            self.entry_documento.insert(0, valores[3])
            self.entry_titulada.delete(0, tk.END)
            self.entry_titulada.insert(0, valores[4])
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, valores[5])

if __name__ == "__main__":
    root = tk.Tk()
    app = PrestamoRegistro(root)
    root.mainloop()