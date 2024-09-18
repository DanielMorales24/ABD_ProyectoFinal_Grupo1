import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox

# Función para la conexión a la base de datos
def connect_to_db():
    try:
        conn_str = (
            r"DRIVER={ODBC Driver 17 for SQL Server};"
            r"SERVER=DESKTOP-RCPI344;"  # Servidor
            r"DATABASE=Escuela;"  # Base de datos a seleccionar
            r"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str)
        messagebox.showinfo("Conexión", "Conexión a la base de datos establecida correctamente")
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {str(e)}")
        return None

class DatabaseManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Database Management System")
        self.root.geometry("900x600")

        # Inicializa la conexión como None
        self.conn = None
        self.cursor = None

        # Establecer estilos y menú
        self.set_styles()
        self.create_menu()

        # Crear frame principal donde se mostrarán las opciones
        self.main_frame = ttk.Frame(self.root, padding=10, style="Main.TFrame")
        self.main_frame.pack(fill='both', expand=True)

        # Mostrar mensaje de bienvenida
        self.display_welcome()

    def set_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        primary_color = "#2c3e50"
        secondary_color = "#ecf0f1"
        accent_color = "#3498db"
        button_color = "#2980b9"
        bg_color = "#34495e"
        self.style.configure("TFrame", background=primary_color)
        self.style.configure("Main.TFrame", background=bg_color)
        self.style.configure("TLabel", background=primary_color, foreground=secondary_color, font=("Arial", 12))
        self.style.configure("TButton", background=button_color, foreground=secondary_color, font=("Arial", 12, "bold"), padding=10)
        self.style.configure("Accent.TButton", background=accent_color, foreground=secondary_color, font=("Arial", 12, "bold"))
        self.root.option_add("*TButton*highlightThickness", 0)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú de conexión
        connection_menu = tk.Menu(menubar, tearoff=0)
        connection_menu.add_command(label="Conectar", command=self.connect_db)
        connection_menu.add_command(label="Desconectar", command=self.disconnect_db)
        menubar.add_cascade(label="Conexión", menu=connection_menu)

        table_menu = tk.Menu(menubar, tearoff=0)
        table_menu.add_command(label="Crear Tabla", command=self.create_table_window)
        table_menu.add_command(label="Mostrar Tablas", command=self.show_tables)
        menubar.add_cascade(label="Tablas", menu=table_menu)

        query_menu = tk.Menu(menubar, tearoff=0)
        query_menu.add_command(label="Ejecutar Consultas", command=self.query_execution_window)
        menubar.add_cascade(label="Consultas", menu=query_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Acerca de", command=self.about_message)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

    def display_welcome(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        welcome_label = ttk.Label(self.main_frame, text="Bienvenido al Sistema de Gestión de Bases de Datos", font=("Arial", 20, "bold"), background="#34495e", foreground="white")
        welcome_label.pack(pady=40)

    def connect_db(self):
        if not self.conn:
            self.conn = connect_to_db()
            if self.conn:
                self.cursor = self.conn.cursor()

    def disconnect_db(self):
        if self.conn:
            try:
                self.conn.close()
                messagebox.showinfo("Conexión", "Desconectado de la base de datos correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al desconectar: {str(e)}")
            finally:
                self.conn = None
                self.cursor = None
        else:
            messagebox.showwarning("Advertencia", "No hay ninguna conexión activa")

    def create_table_window(self):
        self.clear_frame()
        ttk.Label(self.main_frame, text="Crear Tabla", font=("Arial", 16, "bold"), background="#34495e", foreground="white").pack(pady=10)
        ttk.Label(self.main_frame, text="Nombre de la Tabla:").pack(anchor="w", padx=20)
        self.table_name_entry = ttk.Entry(self.main_frame)
        self.table_name_entry.pack(fill='x', padx=20, pady=5)
        ttk.Label(self.main_frame, text="Definiciones de Campos (nombre, tipo, restricciones):").pack(anchor="w", padx=20)
        self.fields_text = tk.Text(self.main_frame, height=5, font=("Arial", 12))
        self.fields_text.pack(fill='x', padx=20, pady=5)
        create_button = ttk.Button(self.main_frame, text="Crear Tabla", style="Accent.TButton", command=self.create_table)
        create_button.pack(pady=20)

    def create_table(self):
        if not self.conn:
            messagebox.showwarning("Advertencia", "Primero debes conectarte a la base de datos")
            return

        table_name = self.table_name_entry.get()
        fields = self.fields_text.get("1.0", tk.END)
        try:
            query = f"CREATE TABLE {table_name} ({fields.strip()})"
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Éxito", f"Tabla '{table_name}' creada con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la tabla: {str(e)}")

    def query_execution_window(self):
        self.clear_frame()
        ttk.Label(self.main_frame, text="Ejecutar Consulta", font=("Arial", 16, "bold"), background="#34495e", foreground="white").pack(pady=10)
        self.query_text = tk.Text(self.main_frame, height=5, font=("Arial", 12))
        self.query_text.pack(fill='x', padx=20, pady=10)
        execute_button = ttk.Button(self.main_frame, text="Ejecutar", style="Accent.TButton", command=self.execute_query)
        execute_button.pack(pady=20)
        
        # Tabla para mostrar resultados
        self.result_table = ttk.Treeview(self.main_frame, columns=(), show="headings")
        self.result_table.pack(fill="both", expand=True, padx=20, pady=10)

    def execute_query(self):
        if not self.conn:
            messagebox.showwarning("Advertencia", "Primero debes conectarte a la base de datos")
            return

        query = self.query_text.get("1.0", tk.END).strip()
        try:
            self.cursor.execute(query)
            # Si es una SELECT, mostrar los resultados
            if query.lower().startswith("select"):
                rows = self.cursor.fetchall()
                if rows:
                    # Limpia la tabla anterior
                    self.result_table.delete(*self.result_table.get_children())
                    # Define las columnas basadas en los nombres de columnas de la consulta
                    columns = [desc[0] for desc in self.cursor.description]
                    self.result_table["columns"] = columns
                    for col in columns:
                        self.result_table.heading(col, text=col)
                        self.result_table.column(col, minwidth=0, width=100)

                    # Agrega los datos a la tabla
                    for row in rows:
                        self.result_table.insert("", "end", values=row)
                else:
                    messagebox.showinfo("Resultado", "La consulta no devolvió ningún resultado.")
            else:
                # Si no es una SELECT, simplemente ejecutar y confirmar
                self.conn.commit()
                messagebox.showinfo("Éxito", "Consulta ejecutada con éxito")
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar la consulta: {str(e)}")

    def show_tables(self):
        if not self.conn:
            messagebox.showwarning("Advertencia", "Primero debes conectarte a la base de datos")
            return
        
        self.clear_frame()
        ttk.Label(self.main_frame, text="Tablas en la Base de Datos", font=("Arial", 16, "bold"), background="#34495e", foreground="white").pack(pady=10)
        
        try:
            self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = self.cursor.fetchall()
            if tables:
                for table in tables:
                    ttk.Label(self.main_frame, text=table[0], font=("Arial", 14), background="#34495e", foreground="white").pack(anchor="w", padx=20, pady=5)
            else:
                messagebox.showinfo("Resultado", "No hay tablas en la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener las tablas: {str(e)}")

    def about_message(self):
        messagebox.showinfo("Acerca de", "Sistema de Gestión de Bases de Datos\nDesarrollado por [Tu Nombre]")

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseManagerApp(root)
    root.mainloop()
