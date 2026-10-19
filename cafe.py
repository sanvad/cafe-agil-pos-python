import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os


# ==========================================
# 1. MODELO: DATOS Y REGLAS DE NEGOCIO
# ==========================================

class CafeModel:
    MAX_CANTIDAD_POR_PRODUCTO = 50

    def __init__(self):
        self.catalogo = {
            "Café Espresso": {"categoria": "Bebida", "precio": 2200},
            "Café Americano": {"categoria": "Bebida", "precio": 2500},
            "Cappuccino": {"categoria": "Bebida", "precio": 3100},
            "Latte": {"categoria": "Bebida", "precio": 3200},
            "Té Verde": {"categoria": "Bebida", "precio": 2000},
            "Sandwich Ave": {"categoria": "Alimento", "precio": 4500},
            "Croissant": {"categoria": "Alimento", "precio": 2800},
            "Muffin Choco": {"categoria": "Alimento", "precio": 2300},
            "Slice Tarta": {"categoria": "Alimento", "precio": 3500},
        }
        self.pedido_actual = []

    def agregar_producto(self, nombre_producto, cantidad):
        if not isinstance(nombre_producto, str) or nombre_producto not in self.catalogo:
            raise ValueError("El producto seleccionado no existe en el catálogo.")

        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise ValueError("La cantidad debe ser un número entero.")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        if cantidad > self.MAX_CANTIDAD_POR_PRODUCTO:
            raise ValueError(
                f"La cantidad máxima por operación es "
                f"{self.MAX_CANTIDAD_POR_PRODUCTO}."
            )

        precio = self.catalogo[nombre_producto]["precio"]

        for item in self.pedido_actual:
            if item["producto"] == nombre_producto:
                nueva_cantidad = item["cantidad"] + cantidad
                if nueva_cantidad > self.MAX_CANTIDAD_POR_PRODUCTO:
                    raise ValueError(
                        f"La cantidad total de {nombre_producto} no puede "
                        f"superar {self.MAX_CANTIDAD_POR_PRODUCTO} unidades."
                    )
                item["cantidad"] = nueva_cantidad
                item["subtotal"] = nueva_cantidad * precio
                return

        self.pedido_actual.append({
            "producto": nombre_producto,
            "precio": precio,
            "cantidad": cantidad,
            "subtotal": cantidad * precio,
        })

    def eliminar_producto(self, indice):
        if isinstance(indice, bool) or not isinstance(indice, int):
            raise IndexError("Índice de producto no válido.")
        if not 0 <= indice < len(self.pedido_actual):
            raise IndexError("Ítem no encontrado en el pedido.")
        del self.pedido_actual[indice]

    def calcular_total(self):
        return sum(item["subtotal"] for item in self.pedido_actual)

    def vaciar_pedido(self):
        self.pedido_actual.clear()

    def registrar_venta(self, archivo_ventas="ventas_cafe.csv"):
        """Guarda los detalles de la venta en CSV antes de vaciar el pedido."""
        if not self.pedido_actual:
            raise ValueError("No se puede registrar una venta sin productos.")

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = self.calcular_total()
        archivo_existe = os.path.exists(archivo_ventas)

        try:
            with open(archivo_ventas, "a", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)

                if not archivo_existe or os.path.getsize(archivo_ventas) == 0:
                    escritor.writerow([
                        "fecha",
                        "producto",
                        "precio_unitario",
                        "cantidad",
                        "subtotal",
                        "total_venta",
                    ])

                for item in self.pedido_actual:
                    escritor.writerow([
                        fecha,
                        item["producto"],
                        item["precio"],
                        item["cantidad"],
                        item["subtotal"],
                        total,
                    ])
        except OSError as error:
            raise OSError(f"No se pudo guardar la venta: {error}") from error

        self.vaciar_pedido()
        return total


# ==========================================
# 2. VISTA: INTERFAZ GRÁFICA
# ==========================================

class CafeView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Café Ágil - Sistema de Gestión de Pedidos")
        self.geometry("900x620")
        self.minsize(800, 550)
        self.configure(bg="#F5F5F7")

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Header.TFrame", background="#3A2E2B")
        self.style.configure(
            "Title.TLabel",
            font=("Helvetica", 16, "bold"),
            foreground="#FFFFFF",
            background="#3A2E2B",
        )
        self.style.configure(
            "Section.TLabelframe",
            font=("Helvetica", 11, "bold"),
        )

        self._crear_interfaz()

    def _crear_interfaz(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=15)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Café Ágil — Punto de Venta Digital",
            style="Title.TLabel",
        ).pack(side=tk.LEFT)

        contenedor = ttk.Frame(self, padding=15)
        contenedor.pack(fill=tk.BOTH, expand=True)

        col_izquierda = ttk.LabelFrame(
            contenedor,
            text=" Catálogo de Productos ",
            style="Section.TLabelframe",
            padding=10,
        )
        col_izquierda.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10)
        )

        ttk.Label(
            col_izquierda,
            text="Seleccione producto:",
            font=("Helvetica", 10),
        ).pack(anchor=tk.W, pady=(5, 2))

        self.combo_productos = ttk.Combobox(
            col_izquierda,
            state="readonly",
            font=("Helvetica", 10),
        )
        self.combo_productos.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            col_izquierda,
            text="Cantidad (1 a 50):",
            font=("Helvetica", 10),
        ).pack(anchor=tk.W, pady=(5, 2))

        self.spin_cantidad = ttk.Spinbox(
            col_izquierda,
            from_=1,
            to=50,
            increment=1,
            font=("Helvetica", 10),
        )
        self.spin_cantidad.set("1")
        self.spin_cantidad.pack(fill=tk.X, pady=(0, 15))

        self.btn_agregar = tk.Button(
            col_izquierda,
            text="Agregar al pedido",
            bg="#2E7D32",
            fg="white",
            font=("Helvetica", 10, "bold"),
            activebackground="#1B5E20",
            cursor="hand2",
        )
        self.btn_agregar.pack(fill=tk.X, ipady=5)

        col_derecha = ttk.LabelFrame(
            contenedor,
            text=" Pedido Actual ",
            style="Section.TLabelframe",
            padding=10,
        )
        col_derecha.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        columnas = ("producto", "precio", "cantidad", "subtotal")
        self.tree_pedido = ttk.Treeview(
            col_derecha,
            columns=columnas,
            show="headings",
            height=10,
        )
        self.tree_pedido.heading("producto", text="Producto")
        self.tree_pedido.heading("precio", text="Precio unitario")
        self.tree_pedido.heading("cantidad", text="Cant.")
        self.tree_pedido.heading("subtotal", text="Subtotal")

        self.tree_pedido.column("producto", width=155, anchor=tk.W)
        self.tree_pedido.column("precio", width=100, anchor=tk.E)
        self.tree_pedido.column("cantidad", width=55, anchor=tk.CENTER)
        self.tree_pedido.column("subtotal", width=100, anchor=tk.E)

        scrollbar = ttk.Scrollbar(
            col_derecha,
            orient=tk.VERTICAL,
            command=self.tree_pedido.yview,
        )
        self.tree_pedido.configure(yscrollcommand=scrollbar.set)
        self.tree_pedido.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(0, 10)
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))

        self.btn_eliminar = tk.Button(
            col_derecha,
            text="Eliminar ítem seleccionado",
            bg="#C62828",
            fg="white",
            font=("Helvetica", 9, "bold"),
            activebackground="#8E0000",
            cursor="hand2",
        )
        self.btn_eliminar.pack(anchor=tk.E, pady=(0, 10))

        panel_totales = ttk.Frame(col_derecha, padding=5)
        panel_totales.pack(fill=tk.X)

        self.lbl_total_var = tk.StringVar(value="TOTAL: $0")
        ttk.Label(
            panel_totales,
            textvariable=self.lbl_total_var,
            font=("Helvetica", 14, "bold"),
            foreground="#1A237E",
        ).pack(side=tk.LEFT)

        self.btn_registrar = tk.Button(
            panel_totales,
            text="Registrar venta",
            bg="#1565C0",
            fg="white",
            font=("Helvetica", 10, "bold"),
            activebackground="#0D47A1",
            cursor="hand2",
        )
        self.btn_registrar.pack(side=tk.RIGHT, ipady=5, ipadx=8)

        self.lbl_status = ttk.Label(
            self,
            text="Sistema listo. Inicie un pedido.",
            font=("Helvetica", 9, "italic"),
            padding=5,
        )
        self.lbl_status.pack(fill=tk.X, side=tk.BOTTOM)

    def actualizar_status(self, mensaje, es_error=False):
        color = "#C62828" if es_error else "#2E7D32"
        self.lbl_status.configure(text=mensaje, foreground=color)

    def mostrar_error(self, titulo, mensaje):
        messagebox.showerror(titulo, mensaje, parent=self)

    def mostrar_aviso(self, titulo, mensaje):
        messagebox.showwarning(titulo, mensaje, parent=self)

    def confirmar(self, titulo, mensaje):
        return messagebox.askyesno(titulo, mensaje, parent=self)

    def mostrar_info(self, titulo, mensaje):
        messagebox.showinfo(titulo, mensaje, parent=self)


# ==========================================
# 3. CONTROLADOR: COORDINA MODELO Y VISTA
# ==========================================

class CafeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self._cargar_catalogo_en_vista()
        self.view.btn_agregar.configure(command=self.agregar_item)
        self.view.btn_eliminar.configure(command=self.eliminar_item)
        self.view.btn_registrar.configure(command=self.registrar_venta)

    @staticmethod
    def formato_pesos(valor):
        return "$" + f"{valor:,}".replace(",", ".")

    def _cargar_catalogo_en_vista(self):
        opciones = [
            f"{nombre} ({self.formato_pesos(datos['precio'])})"
            for nombre, datos in self.model.catalogo.items()
        ]
        self.view.combo_productos["values"] = opciones
        if opciones:
            self.view.combo_productos.current(0)

    def agregar_item(self):
        combo_val = self.view.combo_productos.get()
        if not combo_val:
            self.view.mostrar_aviso(
                "Atención", "Seleccione un producto del catálogo."
            )
            return

        cantidad_texto = self.view.spin_cantidad.get().strip()
        if not cantidad_texto.isdigit():
            self.view.mostrar_error(
                "Cantidad inválida",
                "La cantidad debe ser un número entero positivo.",
            )
            return

        cantidad = int(cantidad_texto)
        # Extraer el nombre del producto, sin incluir el precio.
        nombre_producto = combo_val.split(" (", 1)[0]

        try:
            self.model.agregar_producto(nombre_producto, cantidad)
        except ValueError as error:
            self.view.mostrar_error("No se pudo agregar", str(error))
            self.view.actualizar_status(str(error), es_error=True)
            return

        self.refrescar_tabla_pedido()
        self.view.actualizar_status(
            f"Producto agregado: {nombre_producto} (x{cantidad})."
        )

    def eliminar_item(self):
        seleccion = self.view.tree_pedido.selection()
        if not seleccion:
            self.view.mostrar_aviso(
                "Atención", "Seleccione un ítem de la tabla para eliminar."
            )
            return

        # selection() devuelve una tupla de identificadores.
        indice = self.view.tree_pedido.index(seleccion[0])

        try:
            self.model.eliminar_producto(indice)
        except IndexError as error:
            self.view.mostrar_error("No se pudo eliminar", str(error))
            return

        self.refrescar_tabla_pedido()
        self.view.actualizar_status("Ítem eliminado del pedido.")

    def refrescar_tabla_pedido(self):
        for fila in self.view.tree_pedido.get_children():
            self.view.tree_pedido.delete(fila)

        for item in self.model.pedido_actual:
            self.view.tree_pedido.insert(
                "",
                tk.END,
                values=(
                    item["producto"],
                    self.formato_pesos(item["precio"]),
                    item["cantidad"],
                    self.formato_pesos(item["subtotal"]),
                ),
            )

        self.view.lbl_total_var.set(
            f"TOTAL: {self.formato_pesos(self.model.calcular_total())}"
        )

    def registrar_venta(self):
        if not self.model.pedido_actual:
            self.view.mostrar_aviso(
                "Pedido vacío",
                "No se puede registrar una venta sin productos.",
            )
            self.view.actualizar_status(
                "No se puede registrar una venta con el pedido vacío.",
                es_error=True,
            )
            return

        total = self.model.calcular_total()
        confirmar = self.view.confirmar(
            "Confirmar venta",
            "¿Desea confirmar la venta?\n\n"
            f"Total a cobrar: {self.formato_pesos(total)}",
        )
        if not confirmar:
            self.view.actualizar_status(
                "Venta cancelada; el pedido se conserva."
            )
            return

        try:
            total_registrado = self.model.registrar_venta()
        except (OSError, ValueError) as error:
            self.view.mostrar_error("No se pudo registrar la venta", str(error))
            self.view.actualizar_status(
                "No se pudo guardar la venta; el pedido se conserva.",
                es_error=True,
            )
            return

        self.refrescar_tabla_pedido()
        self.view.mostrar_info(
            "Venta registrada",
            "La venta se guardó en ventas_cafe.csv.\n"
            f"Total: {self.formato_pesos(total_registrado)}",
        )
        self.view.actualizar_status("Venta guardada correctamente.")


# ==========================================
# 4. PUNTO DE ENTRADA DE LA APLICACIÓN
# ==========================================

if __name__ == "__main__":
    modelo = CafeModel()
    vista = CafeView()
    controlador = CafeController(modelo, vista)
    vista.mainloop()
