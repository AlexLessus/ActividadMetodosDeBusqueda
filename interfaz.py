# -*- coding: utf-8 -*-
"""
===============================================================================
INSTITUTO TECNOLÓGICO DE CIUDAD GUZMÁN (ITCG) - TECNOLÓGICO NACIONAL DE MÉXICO
Materia: Inteligencia Artificial (Unidades 1 y 3)
Módulo: Interfaz Gráfica de Usuario Interactiva (InterfazGrafica)
===============================================================================

Este módulo implementa la interfaz gráfica completa y moderna con Tkinter y Pillow:
- Lienzo (Canvas) interactivo con soporte de Zoom, Paneo y Tooltips informativos.
- Renderizado sobre el mapa oficial del ITCG o en vista esquemática limpia.
- Animación interactiva paso a paso de los algoritmos de búsqueda.
- Resaltado visual del camino solución y de los nodos explorados en tiempo real.
- Panel completo de resultados, métricas (costo, nodos, tiempo) y justificación teórica.
- Tablas de traza de ejecución y explorador de las Listas Enlazadas en memoria.
===============================================================================
"""

import math
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, List, Tuple, Any
from PIL import Image, ImageTk

from grafo import GrafoListas
from nodo import NodoEstado, NodoAdyacente
from campus_data import cargar_grafo_itcg, EDIFICIOS_CAMPUS
from algoritmos import AlgoritmosBusqueda, ResultadoBusqueda


# Paleta de colores institucional y moderna
COLORES_TEMA = {
    "primario": "#1e3a8a",          # Azul TecNM profundo
    "secundario": "#0284c7",        # Cyan académico
    "fondo_oscuro": "#0f172a",      # Slate 900
    "encabezado": "#1e293b",        # Slate 800
    "texto_claro": "#f8fafc",       # Slate 50
    "arista_normal": "#94a3b8",     # Slate 400
    "arista_camino": "#22c55e",     # Verde éxito brillante
    "nodo_origen": "#10b981",       # Esmeralda
    "nodo_meta": "#ef4444",         # Rojo carmesí
    "nodo_explorado": "#facc15",    # Amarillo ámbar
    "nodo_actual": "#06b6d4",       # Cian activo
    "nodo_camino": "#22c55e",       # Verde ruta
}

# Colores por categoría de edificio en el ITCG
COLORES_CATEGORIAS = {
    "Laboratorios": "#0284c7",              # Azul cielo
    "Aulas": "#4f46e5",                     # Índigo
    "Sistemas y Computación": "#059669",    # Verde sistemas
    "Cubículos / Administrativo": "#7c3aed",# Violeta
    "Aulas / Administrativo": "#6366f1",    # Azul lavanda
    "Servicios": "#d97706",                 # Ámbar
    "Servicios / Administrativo": "#b45309",# Ámbar oscuro
    "Biblioteca / Posgrado": "#0891b2",     # Cian oscuro
    "Deportivo / Cultural": "#dc2626",      # Rojo
    "Eventos / Auditorios": "#e11d48",      # Rosa mexicano
    "Dirección / Gobierno": "#9333ea",      # Púrpura
    "Accesos": "#ea580c",                   # Naranja vial
    "General": "#64748b"                    # Gris pizarra
}


class InterfazGrafica:
    """
    Aplicación gráfica interactiva para la enseñanza de Métodos de Búsqueda
    en Inteligencia Artificial sobre el mapa del ITCG.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ITCG - Inteligencia Artificial: Métodos de Búsqueda sobre Grafos")
        self.root.geometry("1420x860")
        self.root.minsize(1100, 700)

        # Configuración de estilo visual
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self._configurar_estilos()

        # Cargar el grafo con estructura de Listas Enlazadas
        self.grafo: GrafoListas = cargar_grafo_itcg()

        # Estado de navegación y búsqueda
        self.origen_seleccionado: Optional[str] = "A"
        self.destino_seleccionado: Optional[str] = "Z"
        self.resultado_actual: Optional[ResultadoBusqueda] = None

        # Variables de zoom y paneo sobre el lienzo
        self.zoom: float = 1.0
        self.offset_x: float = 20.0
        self.offset_y: float = 20.0
        self.arrastre_prev_x: int = 0
        self.arrastre_prev_y: int = 0

        # Control de capas visuales
        self.var_mostrar_mapa = tk.BooleanVar(value=True)
        self.var_mostrar_pesos = tk.BooleanVar(value=True)
        self.var_mostrar_heuristicas = tk.BooleanVar(value=False)
        self.var_velocidad_animacion = tk.IntVar(value=300)  # milisegundos

        # Control de animación interactiva
        self.animacion_activa: bool = False
        self.paso_animacion_actual: int = 0
        self.tarea_after_animacion: Optional[str] = None
        self._bloqueo_evento_traza: bool = False

        # Imagen original del mapa y caché de renderizado
        self.ruta_imagen_mapa = os.path.join(os.path.dirname(__file__), "mapa_itcg.jpg")
        self.imagen_original_pil: Optional[Image.Image] = None
        self.imagen_tk_actual: Optional[ImageTk.PhotoImage] = None
        self.imagen_tk_cache: Optional[ImageTk.PhotoImage] = None
        self.zoom_cache_img: Optional[Tuple[int, int]] = None
        self._cargar_imagen_mapa()

        # Construir la interfaz de usuario
        self._crear_interfaz()

        # Dibujar el estado inicial del grafo
        self.root.update_idletasks()
        self.ajustar_vista_general()
        self.redibujar_lienzo()

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN Y ESTILOS
    # -------------------------------------------------------------------------
    def _configurar_estilos(self):
        """Define el tema visual de los componentes de Tkinter ttk."""
        self.style.configure(".", font=("Segoe UI", 9))
        self.style.configure(
            "Header.TFrame",
            background=COLORES_TEMA["encabezado"]
        )
        self.style.configure(
            "HeaderTitle.TLabel",
            background=COLORES_TEMA["encabezado"],
            foreground="#ffffff",
            font=("Segoe UI", 13, "bold")
        )
        self.style.configure(
            "HeaderSubtitle.TLabel",
            background=COLORES_TEMA["encabezado"],
            foreground="#93c5fd",
            font=("Segoe UI", 9)
        )
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 9, "bold"),
            background=COLORES_TEMA["primario"],
            foreground="#ffffff"
        )
        self.style.configure(
            "Accent.TButton",
            font=("Segoe UI", 9, "bold"),
            background="#059669",
            foreground="#ffffff"
        )
        self.style.configure("Card.TLabelframe", padding=8)
        self.style.configure("Card.TLabelframe.Label", font=("Segoe UI", 9, "bold"))

    def _cargar_imagen_mapa(self):
        """Carga la imagen oficial del campus para renderizar como fondo."""
        if os.path.exists(self.ruta_imagen_mapa):
            try:
                self.imagen_original_pil = Image.open(self.ruta_imagen_mapa)
            except Exception as e:
                print(f"[AVISO] No se pudo cargar imagen del mapa: {e}")
                self.imagen_original_pil = None
        else:
            self.imagen_original_pil = None

    # -------------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA JERARQUÍA DE WIDGETS
    # -------------------------------------------------------------------------
    def _crear_interfaz(self):
        """Construye todos los paneles, controles, lienzo y tablas."""
        # 1. Encabezado institucional superior
        self._crear_encabezado()

        # 2. Contenedor principal con separación horizontal
        contenedor_principal = ttk.Frame(self.root)
        contenedor_principal.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Panel izquierdo / central: Lienzo del mapa con barra de herramientas
        panel_mapa = ttk.Frame(contenedor_principal)
        panel_mapa.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._crear_barra_herramientas_mapa(panel_mapa)
        self._crear_lienzo_mapa(panel_mapa)

        # Panel derecho: Controles de búsqueda, animación, métricas y detalles
        panel_lateral = ttk.Frame(contenedor_principal, width=440)
        panel_lateral.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(6, 0))
        panel_lateral.pack_propagate(False)
        self._crear_panel_lateral(panel_lateral)

    def _crear_encabezado(self):
        """Crea el banner institucional en la parte superior."""
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(12, 8))
        header.pack(fill=tk.X)

        frame_titulos = ttk.Frame(header, style="Header.TFrame")
        frame_titulos.pack(side=tk.LEFT, fill=tk.Y)

        lbl_tec = ttk.Label(
            frame_titulos,
            text="TECNOLÓGICO NACIONAL DE MÉXICO  •  INSTITUTO TECNOLÓGICO DE CIUDAD GUZMÁN",
            style="HeaderSubtitle.TLabel"
        )
        lbl_tec.pack(anchor=tk.W)

        lbl_titulo = ttk.Label(
            frame_titulos,
            text="Simulador Académico de Algoritmos de Búsqueda sobre el Campus ITCG",
            style="HeaderTitle.TLabel"
        )
        lbl_titulo.pack(anchor=tk.W)

        # Insignia de estructura de datos
        frame_badge = ttk.Frame(header, style="Header.TFrame")
        frame_badge.pack(side=tk.RIGHT, padx=5)

        lbl_badge = tk.Label(
            frame_badge,
            text="Estructura: Listas Enlazadas Puras\n(NodoEstado -> NodoAdyacente)",
            bg="#0f172a",
            fg="#38bdf8",
            font=("Consolas", 8, "bold"),
            relief=tk.RIDGE,
            padx=8,
            pady=4
        )
        lbl_badge.pack()

    def _crear_barra_herramientas_mapa(self, padre: ttk.Frame):
        """Barra de botones y casillas para controlar la vista del lienzo."""
        barra = ttk.Frame(padre, padding=(2, 2, 2, 4))
        barra.pack(fill=tk.X)

        # Casillas de visualización
        chk_mapa = ttk.Checkbutton(
            barra,
            text="🗺 Mapa Oficial",
            variable=self.var_mostrar_mapa,
            command=self.redibujar_lienzo
        )
        chk_mapa.pack(side=tk.LEFT, padx=3)

        chk_pesos = ttk.Checkbutton(
            barra,
            text="📏 Pesos (m)",
            variable=self.var_mostrar_pesos,
            command=self.redibujar_lienzo
        )
        chk_pesos.pack(side=tk.LEFT, padx=3)

        chk_heur = ttk.Checkbutton(
            barra,
            text="🎯 Heurística h(n)",
            variable=self.var_mostrar_heuristicas,
            command=self.redibujar_lienzo
        )
        chk_heur.pack(side=tk.LEFT, padx=3)

        # Separador visual
        ttk.Separator(barra, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)

        # Botones de Zoom y Navegación
        btn_zoom_in = ttk.Button(barra, text="🔍+ Acercar", width=10, command=self.zoom_acercar)
        btn_zoom_in.pack(side=tk.LEFT, padx=2)

        btn_zoom_out = ttk.Button(barra, text="🔍- Alejar", width=10, command=self.zoom_alejar)
        btn_zoom_out.pack(side=tk.LEFT, padx=2)

        btn_ajustar = ttk.Button(barra, text="⟲ Ajustar Vista", width=12, command=self.ajustar_vista_general)
        btn_ajustar.pack(side=tk.LEFT, padx=2)

        # Leyenda de interacción rápida
        lbl_ayuda = ttk.Label(
            barra,
            text="Tip: Clic izquierdo = Seleccionar Origen/Meta | Arrastrar = Mover | Rueda = Zoom",
            foreground="#64748b",
            font=("Segoe UI", 8, "italic")
        )
        lbl_ayuda.pack(side=tk.RIGHT, padx=4)

    def _crear_lienzo_mapa(self, padre: ttk.Frame):
        """Crea el canvas interactivo donde se dibuja el campus y el grafo."""
        frame_canvas = ttk.Frame(padre, relief=tk.SUNKEN, borderwidth=1)
        frame_canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            frame_canvas,
            bg="#f1f5f9",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Eventos del mouse para interactividad
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_click_izquierdo)
        self.canvas.bind("<B1-Motion>", self._on_canvas_arrastre)
        self.canvas.bind("<ButtonPress-3>", self._on_canvas_click_derecho)
        self.canvas.bind("<MouseWheel>", self._on_canvas_mousewheel)  # Windows
        self.canvas.bind("<Motion>", self._on_canvas_hover)

        # Tooltip flotante para mostrar información al pasar el cursor
        self.tooltip = tk.Label(
            self.canvas,
            text="",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Segoe UI", 8),
            relief=tk.SOLID,
            borderwidth=1,
            padx=6,
            pady=3
        )

    def _crear_panel_lateral(self, padre: ttk.Frame):
        """Construye el panel lateral con controles, animación, resultados y tabs."""
        # 1. Panel de Configuración de Búsqueda
        self._crear_panel_configuracion(padre)

        # 2. Panel de Animación y Paso a Paso
        self._crear_panel_animacion(padre)

        # 3. Panel de Resumen de Resultados
        self._crear_panel_resultados(padre)

        # 4. Notebook con pestañas de Traza y Estructura en Memoria
        self._crear_notebook_detalles(padre)

    def _crear_panel_configuracion(self, padre: ttk.Frame):
        """Controles para seleccionar origen, destino y algoritmo."""
        lf = ttk.LabelFrame(padre, text="1. Configuración de la Búsqueda", style="Card.TLabelframe")
        lf.pack(fill=tk.X, pady=(0, 4))

        # Lista ordenada de nodos para los ComboBox
        todos_nodos = self.grafo.obtener_todos_los_nodos()
        self.lista_opciones_nodos = [
            f"[{n.informacion}] {n.nombre_completo}" for n in todos_nodos
        ]
        self.mapa_opcion_a_id = {
            f"[{n.informacion}] {n.nombre_completo}": n.informacion for n in todos_nodos
        }

        # Grid de selección
        f_selectores = ttk.Frame(lf)
        f_selectores.pack(fill=tk.X, pady=2)

        # Estado Inicial (Origen)
        ttk.Label(f_selectores, text="Origen:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.combo_origen = ttk.Combobox(
            f_selectores,
            values=self.lista_opciones_nodos,
            state="readonly",
            width=30
        )
        self.combo_origen.grid(row=0, column=1, sticky=tk.EW, padx=4, pady=2)
        self._seleccionar_combo_por_id(self.combo_origen, self.origen_seleccionado)
        self.combo_origen.bind("<<ComboboxSelected>>", self._on_cambio_origen)

        # Botón para intercambiar Origen y Destino
        btn_swap = ttk.Button(f_selectores, text="⇅ Intercambiar", width=12, command=self.intercambiar_origen_destino)
        btn_swap.grid(row=0, column=2, rowspan=2, padx=2, sticky=tk.NS)

        # Estado Meta (Destino)
        ttk.Label(f_selectores, text="Destino:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.combo_destino = ttk.Combobox(
            f_selectores,
            values=self.lista_opciones_nodos,
            state="readonly",
            width=30
        )
        self.combo_destino.grid(row=1, column=1, sticky=tk.EW, padx=4, pady=2)
        self._seleccionar_combo_por_id(self.combo_destino, self.destino_seleccionado)
        self.combo_destino.bind("<<ComboboxSelected>>", self._on_cambio_destino)

        f_selectores.columnconfigure(1, weight=1)

        # Selector de Algoritmo de Búsqueda
        f_algo = ttk.Frame(lf)
        f_algo.pack(fill=tk.X, pady=(4, 2))

        ttk.Label(f_algo, text="Algoritmo:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.algoritmos_disponibles = [
            "1. Búsqueda Primero en Anchura (BFS) - No informada",
            "2. Búsqueda Primero en Profundidad (DFS) - No informada",
            "3. Búsqueda Primero el Mejor (Greedy) - Informada f(n)=h(n)",
            "4. Algoritmo de Dijkstra - Informada por costo f(n)=g(n)",
            "5. Búsqueda Heurística A* - Informada f(n)=g(n)+h(n)",
            "6. Búsqueda Local (Hill Climbing / Escalada de Colinas)"
        ]
        self.combo_algoritmo = ttk.Combobox(
            f_algo,
            values=self.algoritmos_disponibles,
            state="readonly",
            width=38
        )
        self.combo_algoritmo.current(4)  # Por defecto A*
        self.combo_algoritmo.pack(fill=tk.X, pady=2)

        # Botones de Acción
        f_botones = ttk.Frame(lf)
        f_botones.pack(fill=tk.X, pady=(4, 0))

        self.btn_ejecutar = tk.Button(
            f_botones,
            text="▶ Ejecutar Búsqueda",
            bg=COLORES_TEMA["primario"],
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief=tk.RAISED,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self.ejecutar_busqueda
        )
        self.btn_ejecutar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.btn_limpiar = ttk.Button(
            f_botones,
            text="🔄 Limpiar",
            width=10,
            command=self.limpiar_busqueda
        )
        self.btn_limpiar.pack(side=tk.RIGHT, padx=(3, 0))

    def _crear_panel_animacion(self, padre: ttk.Frame):
        """Controles para reproducción interactiva paso a paso."""
        lf = ttk.LabelFrame(padre, text="2. Animación y Exploración Paso a Paso", style="Card.TLabelframe")
        lf.pack(fill=tk.X, pady=(0, 4))

        f_controles = ttk.Frame(lf)
        f_controles.pack(fill=tk.X)

        self.btn_paso_ant = ttk.Button(f_controles, text="⏮ Anterior", width=9, command=self.paso_anterior)
        self.btn_paso_ant.pack(side=tk.LEFT, padx=1)

        self.btn_reproducir = tk.Button(
            f_controles,
            text="▶ Animar",
            bg="#0284c7",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            relief=tk.RAISED,
            width=9,
            cursor="hand2",
            command=self.toggle_reproduccion_animacion
        )
        self.btn_reproducir.pack(side=tk.LEFT, padx=2)

        self.btn_paso_sig = ttk.Button(f_controles, text="⏭ Siguiente", width=9, command=self.paso_siguiente)
        self.btn_paso_sig.pack(side=tk.LEFT, padx=1)

        # Etiqueta de paso actual
        self.lbl_paso_contador = ttk.Label(
            f_controles,
            text="Paso: 0 / 0",
            font=("Segoe UI", 8, "bold"),
            foreground="#1e3a8a"
        )
        self.lbl_paso_contador.pack(side=tk.RIGHT, padx=4)

        # Control de velocidad y barra de progreso
        f_velocidad = ttk.Frame(lf)
        f_velocidad.pack(fill=tk.X, pady=(4, 0))

        ttk.Label(f_velocidad, text="Velocidad:", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        scale_vel = ttk.Scale(
            f_velocidad,
            from_=800,
            to=50,
            variable=self.var_velocidad_animacion,
            orient=tk.HORIZONTAL
        )
        scale_vel.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        self.progreso_animacion = ttk.Progressbar(lf, mode="determinate")
        self.progreso_animacion.pack(fill=tk.X, pady=(3, 0))

    def _crear_panel_resultados(self, padre: ttk.Frame):
        """Muestra métricas cuantitativas y cualitativas de la búsqueda."""
        lf = ttk.LabelFrame(padre, text="3. Resultados y Métricas de la Búsqueda", style="Card.TLabelframe")
        lf.pack(fill=tk.X, pady=(0, 4))

        # Estado del algoritmo (Insignia)
        self.lbl_estado_resultado = tk.Label(
            lf,
            text="Esperando ejecución...",
            bg="#e2e8f0",
            fg="#334155",
            font=("Segoe UI", 9, "bold"),
            pady=3,
            relief=tk.GROOVE
        )
        self.lbl_estado_resultado.pack(fill=tk.X, pady=(0, 4))

        # Cuadro de Camino Encontrado
        f_camino = ttk.Frame(lf)
        f_camino.pack(fill=tk.X, pady=1)

        ttk.Label(f_camino, text="Camino Solución:", font=("Segoe UI", 8, "bold")).pack(anchor=tk.W)
        self.txt_camino = tk.Text(
            f_camino,
            height=2,
            wrap=tk.WORD,
            font=("Consolas", 8, "bold"),
            bg="#f8fafc",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.txt_camino.pack(fill=tk.X, pady=1)
        self.txt_camino.insert(tk.END, "Selecciona Origen y Destino y presiona 'Ejecutar Búsqueda'")
        self.txt_camino.configure(state="disabled")

        # Métricas numéricas
        f_metricas = ttk.Frame(lf)
        f_metricas.pack(fill=tk.X, pady=2)

        self.lbl_costo_total = ttk.Label(
            f_metricas,
            text="Costo Total: -- m",
            font=("Segoe UI", 9, "bold"),
            foreground="#1e3a8a"
        )
        self.lbl_costo_total.grid(row=0, column=0, sticky=tk.W, padx=2)

        self.lbl_nodos_explorados = ttk.Label(
            f_metricas,
            text="Explorados: --",
            font=("Segoe UI", 9)
        )
        self.lbl_nodos_explorados.grid(row=0, column=1, sticky=tk.W, padx=6)

        self.lbl_tiempo_ejec = ttk.Label(
            f_metricas,
            text="Tiempo: -- ms",
            font=("Segoe UI", 8),
            foreground="#64748b"
        )
        self.lbl_tiempo_ejec.grid(row=0, column=2, sticky=tk.E, padx=2)

        f_metricas.columnconfigure(1, weight=1)

        # Explicación teórica / académica
        self.txt_explicacion = tk.Text(
            lf,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 8),
            bg="#f1f5f9",
            fg="#1e293b",
            relief=tk.FLAT
        )
        self.txt_explicacion.pack(fill=tk.X, pady=(2, 0))
        self.txt_explicacion.insert(tk.END, "Explicación teórica del algoritmo...")
        self.txt_explicacion.configure(state="disabled")

    def _crear_notebook_detalles(self, padre: ttk.Frame):
        """Pestañas con información técnica de traza, listas enlazadas y edificios."""
        self.notebook = ttk.Notebook(padre)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        # Pestaña 1: Traza de Exploración (Tabla de Pasos)
        frame_traza = ttk.Frame(self.notebook)
        self.notebook.add(frame_traza, text="Traza de Pasos")
        self._crear_tabla_traza(frame_traza)

        # Pestaña 2: Inspección de Listas Enlazadas en Memoria
        frame_listas = ttk.Frame(self.notebook)
        self.notebook.add(frame_listas, text="Listas Enlazadas")
        self._crear_vista_listas_enlazadas(frame_listas)

        # Pestaña 3: Ficha Técnica del Edificio Seleccionado
        frame_ficha = ttk.Frame(self.notebook)
        self.notebook.add(frame_ficha, text="Ficha Edificio")
        self._crear_vista_ficha_edificio(frame_ficha)

    def _crear_tabla_traza(self, padre: ttk.Frame):
        """Tabla Treeview para mostrar el avance paso a paso del algoritmo."""
        columnas = ("paso", "nodo", "accion", "g", "h", "f")
        self.tree_traza = ttk.Treeview(
            padre,
            columns=columnas,
            show="headings",
            height=6,
            selectmode="browse"
        )
        self.tree_traza.heading("paso", text="#")
        self.tree_traza.heading("nodo", text="Nodo")
        self.tree_traza.heading("accion", text="Acción / Evento")
        self.tree_traza.heading("g", text="g(n)")
        self.tree_traza.heading("h", text="h(n)")
        self.tree_traza.heading("f", text="f(n)")

        self.tree_traza.column("paso", width=30, anchor=tk.CENTER)
        self.tree_traza.column("nodo", width=50, anchor=tk.CENTER)
        self.tree_traza.column("accion", width=180, anchor=tk.W)
        self.tree_traza.column("g", width=45, anchor=tk.E)
        self.tree_traza.column("h", width=45, anchor=tk.E)
        self.tree_traza.column("f", width=45, anchor=tk.E)

        scroll_y = ttk.Scrollbar(padre, orient=tk.VERTICAL, command=self.tree_traza.yview)
        self.tree_traza.configure(yscrollcommand=scroll_y.set)

        self.tree_traza.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_traza.bind("<<TreeviewSelect>>", self._on_seleccionar_fila_traza)

    def _crear_vista_listas_enlazadas(self, padre: ttk.Frame):
        """Visor didáctico que inspecciona los punteros reales de las Listas Enlazadas."""
        f_sup = ttk.Frame(padre, padding=2)
        f_sup.pack(fill=tk.X)
        ttk.Label(f_sup, text="Nodo a inspeccionar:").pack(side=tk.LEFT, padx=2)

        self.combo_inspeccionar_nodo = ttk.Combobox(
            f_sup,
            values=[n.informacion for n in self.grafo.obtener_todos_los_nodos()],
            state="readonly",
            width=8
        )
        self.combo_inspeccionar_nodo.set("A")
        self.combo_inspeccionar_nodo.pack(side=tk.LEFT, padx=4)
        self.combo_inspeccionar_nodo.bind("<<ComboboxSelected>>", self._actualizar_visor_listas_enlazadas)

        self.txt_listas_enlazadas = tk.Text(
            padre,
            wrap=tk.NONE,
            font=("Consolas", 8),
            bg="#f8fafc",
            relief=tk.SUNKEN,
            borderwidth=1
        )
        scroll_y = ttk.Scrollbar(padre, orient=tk.VERTICAL, command=self.txt_listas_enlazadas.yview)
        scroll_x = ttk.Scrollbar(padre, orient=tk.HORIZONTAL, command=self.txt_listas_enlazadas.xview)
        self.txt_listas_enlazadas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_listas_enlazadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._actualizar_visor_listas_enlazadas()

    def _crear_vista_ficha_edificio(self, padre: ttk.Frame):
        """Muestra detalles y datos del edificio que el usuario seleccione."""
        self.txt_ficha_edificio = tk.Text(
            padre,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#ffffff",
            relief=tk.SUNKEN,
            borderwidth=1,
            padx=8,
            pady=8
        )
        self.txt_ficha_edificio.pack(fill=tk.BOTH, expand=True)
        self._mostrar_ficha_edificio(self.origen_seleccionado)

    # -------------------------------------------------------------------------
    # TRANSFORMACIONES ESPACIALES Y MANEJO DEL CANVAS
    # -------------------------------------------------------------------------
    def plano_a_canvas(self, x: float, y: float) -> Tuple[float, float]:
        """Convierte coordenadas del plano del campus (X, Y) a coordenadas del lienzo con zoom y paneo."""
        cx = x * self.zoom + self.offset_x
        cy = y * self.zoom + self.offset_y
        return cx, cy

    def canvas_a_plano(self, cx: float, cy: float) -> Tuple[float, float]:
        """Convierte coordenadas del lienzo a coordenadas espaciales del plano del campus."""
        x = (cx - self.offset_x) / self.zoom
        y = (cy - self.offset_y) / self.zoom
        return x, y

    def zoom_acercar(self):
        """Aumenta el factor de escala visual."""
        self.zoom = min(self.zoom * 1.25, 3.5)
        self.redibujar_lienzo()

    def zoom_alejar(self):
        """Disminuye el factor de escala visual."""
        self.zoom = max(self.zoom / 1.25, 0.4)
        self.redibujar_lienzo()

    def ajustar_vista_general(self):
        """Centra y escala el campus completo para que quepa en el tamaño actual del canvas."""
        ancho_canvas = self.canvas.winfo_width()
        alto_canvas = self.canvas.winfo_height()

        if ancho_canvas <= 50 or alto_canvas <= 50:
            ancho_canvas = 900
            alto_canvas = 620

        # El mapa mide originalmente 1024 x 500 en la sección gráfica del campus
        escala_x = (ancho_canvas - 40) / 1024.0
        escala_y = (alto_canvas - 40) / 520.0
        self.zoom = min(escala_x, escala_y, 1.2)
        self.zoom = max(self.zoom, 0.5)

        # Centrar
        ancho_render = 1024.0 * self.zoom
        alto_render = 500.0 * self.zoom
        self.offset_x = (ancho_canvas - ancho_render) / 2.0
        self.offset_y = (alto_canvas - alto_render) / 2.0

        self.redibujar_lienzo()

    # -------------------------------------------------------------------------
    # RENDERIZADO DEL GRAFO Y DEL MAPA
    # -------------------------------------------------------------------------
    def redibujar_lienzo(self):
        """
        Dibuja todas las capas gráficas en el Canvas:
        1. Imagen de fondo del mapa oficial del ITCG (si está habilitada).
        2. Aristas de la red peatonal con sus distancias métricas (pesos).
        3. Aristas del camino solución (resaltadas en verde/amarillo).
        4. Nodos de los edificios con códigos y colores por categoría.
        5. Marcadores especiales para Origen, Destino y Paso de Animación actual.
        """
        self.canvas.delete("all")

        # 1. Capa de Fondo (Mapa Oficial con caché de redimensionamiento)
        if self.var_mostrar_mapa.get() and self.imagen_original_pil is not None:
            ancho_dest = max(10, int(self.imagen_original_pil.width * self.zoom))
            alto_dest = max(10, int(self.imagen_original_pil.height * self.zoom))
            
            # Solo redimensionar si el nivel de zoom ha cambiado (evita congelar la UI en animación)
            if self.imagen_tk_cache is None or self.zoom_cache_img != (ancho_dest, alto_dest):
                try:
                    img_resample = self.imagen_original_pil.resize((ancho_dest, alto_dest), Image.Resampling.BILINEAR)
                    self.imagen_tk_cache = ImageTk.PhotoImage(img_resample)
                    self.zoom_cache_img = (ancho_dest, alto_dest)
                except Exception as e:
                    print(f"[ERROR] Error al renderizar imagen de fondo: {e}")

            if self.imagen_tk_cache is not None:
                self.canvas.create_image(
                    self.offset_x,
                    self.offset_y,
                    anchor=tk.NW,
                    image=self.imagen_tk_cache,
                    tags="fondo_mapa"
                )

        # Obtener datos de estado de búsqueda
        nodos_camino_set = set(self.resultado_actual.camino) if self.resultado_actual and self.resultado_actual.exito else set()
        aristas_camino_set = set()
        if self.resultado_actual and self.resultado_actual.exito:
            for i in range(len(self.resultado_actual.camino) - 1):
                u = self.resultado_actual.camino[i]
                v = self.resultado_actual.camino[i + 1]
                aristas_camino_set.add(tuple(sorted([u, v])))

        # 2. Capa de Aristas (Conexiones Peatonales)
        aristas = self.grafo.obtener_todas_las_aristas()
        for u_id, v_id, peso in aristas:
            nodo_u = self.grafo.buscar_nodo(u_id)
            nodo_v = self.grafo.buscar_nodo(v_id)
            if not nodo_u or not nodo_v:
                continue

            cx1, cy1 = self.plano_a_canvas(nodo_u.x, nodo_u.y)
            cx2, cy2 = self.plano_a_canvas(nodo_v.x, nodo_v.y)

            es_camino = tuple(sorted([u_id, v_id])) in aristas_camino_set

            if es_camino:
                # Arista de solución: Trazo grueso brillante con halo
                self.canvas.create_line(
                    cx1, cy1, cx2, cy2,
                    fill="#15803d",
                    width=7 * self.zoom,
                    capstyle=tk.ROUND,
                    tags="arista_halo"
                )
                self.canvas.create_line(
                    cx1, cy1, cx2, cy2,
                    fill=COLORES_TEMA["arista_camino"],
                    width=4 * self.zoom,
                    capstyle=tk.ROUND,
                    tags="arista_solucion"
                )
            else:
                # Arista normal
                color_linea = "#94a3b8" if self.var_mostrar_mapa.get() else "#cbd5e1"
                self.canvas.create_line(
                    cx1, cy1, cx2, cy2,
                    fill=color_linea,
                    width=2 * self.zoom,
                    dash=(3, 2) if self.var_mostrar_mapa.get() else (),
                    tags="arista_normal"
                )

            # Mostrar pesos numéricos en metros sobre el punto medio de la arista
            if self.var_mostrar_pesos.get():
                mx = (cx1 + cx2) / 2.0
                my = (cy1 + cy2) / 2.0
                # Desplazamiento leve perpendicular
                dx = cx2 - cx1
                dy = cy2 - cy1
                dist = math.hypot(dx, dy)
                if dist > 0:
                    mx += (-dy / dist) * 7
                    my += (dx / dist) * 7

                self.canvas.create_text(
                    mx, my,
                    text=f"{peso:.0f}m",
                    font=("Segoe UI", max(6, int(7 * self.zoom)), "bold"),
                    fill="#1e293b",
                    tags="etiqueta_peso"
                )

        # 3. Capa de Nodos (Edificios del campus)
        radio_base = 13.0 * self.zoom
        todos_los_nodos = self.grafo.obtener_todos_los_nodos()

        # Nodos explorados durante la animación o búsqueda
        nodos_explorados_actual = []
        nodo_en_foco_anim = None
        if self.resultado_actual and self.resultado_actual.pasos:
            if self.paso_animacion_actual > 0 and self.paso_animacion_actual <= len(self.resultado_actual.pasos):
                paso_info = self.resultado_actual.pasos[self.paso_animacion_actual - 1]
                nodos_explorados_actual = paso_info.get("visitados", [])
                nodo_en_foco_anim = paso_info.get("nodo_actual")
            else:
                nodos_explorados_actual = self.resultado_actual.nodos_explorados

        for nodo in todos_los_nodos:
            cx, cy = self.plano_a_canvas(nodo.x, nodo.y)
            r = radio_base

            es_origen = (nodo.informacion == self.origen_seleccionado)
            es_destino = (nodo.informacion == self.destino_seleccionado)
            es_camino = (nodo.informacion in nodos_camino_set)
            es_explorado = (nodo.informacion in nodos_explorados_actual)
            es_foco = (nodo.informacion == nodo_en_foco_anim)

            # Halo de resaltado para nodos especiales
            if es_foco:
                self.canvas.create_oval(
                    cx - r*1.6, cy - r*1.6, cx + r*1.6, cy + r*1.6,
                    fill="",
                    outline=COLORES_TEMA["nodo_actual"],
                    width=3,
                    tags="halo_foco"
                )
            elif es_origen:
                self.canvas.create_oval(
                    cx - r*1.5, cy - r*1.5, cx + r*1.5, cy + r*1.5,
                    fill="",
                    outline=COLORES_TEMA["nodo_origen"],
                    width=3,
                    tags="halo_origen"
                )
            elif es_destino:
                self.canvas.create_oval(
                    cx - r*1.5, cy - r*1.5, cx + r*1.5, cy + r*1.5,
                    fill="",
                    outline=COLORES_TEMA["nodo_meta"],
                    width=3,
                    tags="halo_meta"
                )

            # Determinación del color del nodo
            if es_origen:
                color_relleno = COLORES_TEMA["nodo_origen"]
                color_borde = "#065f46"
            elif es_destino:
                color_relleno = COLORES_TEMA["nodo_meta"]
                color_borde = "#991b1b"
            elif es_camino:
                color_relleno = COLORES_TEMA["nodo_camino"]
                color_borde = "#166534"
            elif es_foco:
                color_relleno = COLORES_TEMA["nodo_actual"]
                color_borde = "#155e75"
            elif es_explorado:
                color_relleno = COLORES_TEMA["nodo_explorado"]
                color_borde = "#854d0e"
            else:
                color_relleno = COLORES_CATEGORIAS.get(nodo.categoria, "#64748b")
                color_borde = "#1e293b"

            # Dibujar el círculo del nodo
            tag_nodo = f"nodo_{nodo.informacion}"
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=color_relleno,
                outline=color_borde,
                width=max(1.5, 2.0 * self.zoom),
                tags=("nodo", tag_nodo)
            )

            # Etiqueta textual del identificador del edificio
            tamano_fuente = max(7, int(8.5 * self.zoom))
            color_texto = "#ffffff" if not (es_explorado and not (es_origen or es_destino or es_camino)) else "#1e293b"
            self.canvas.create_text(
                cx, cy,
                text=nodo.informacion,
                font=("Segoe UI", tamano_fuente, "bold"),
                fill=color_texto,
                tags=("nodo_texto", tag_nodo)
            )

            # Mostrar valor heurístico h(n) si está activo
            if self.var_mostrar_heuristicas.get() and self.destino_seleccionado:
                nodo_meta = self.grafo.buscar_nodo(self.destino_seleccionado)
                if nodo_meta:
                    h_val = self.grafo.calcular_distancia_euclidiana(nodo, nodo_meta)
                    self.canvas.create_text(
                        cx, cy + r + 7,
                        text=f"h={h_val:.0f}",
                        font=("Segoe UI", max(6, int(7 * self.zoom)), "italic"),
                        fill="#0369a1",
                        tags="etiqueta_heuristica"
                    )

            # Insignias visuales flotantes sobre Origen y Meta
            if es_origen:
                self._dibujar_insignia_nodo(cx, cy - r - 9, "ORIGEN", "#10b981")
            elif es_destino:
                self._dibujar_insignia_nodo(cx, cy - r - 9, "META", "#ef4444")

    def _dibujar_insignia_nodo(self, x: float, y: float, texto: str, color_bg: str):
        """Dibuja una pequeña etiqueta rectangular redondeada sobre el nodo."""
        ancho_insignia = 24 * self.zoom
        alto_insignia = 9 * self.zoom
        self.canvas.create_rectangle(
            x - ancho_insignia, y - alto_insignia,
            x + ancho_insignia, y + alto_insignia,
            fill=color_bg,
            outline="#ffffff",
            width=1,
            tags="insignia"
        )
        self.canvas.create_text(
            x, y,
            text=texto,
            font=("Segoe UI", max(6, int(7 * self.zoom)), "bold"),
            fill="#ffffff",
            tags="insignia_texto"
        )

    # -------------------------------------------------------------------------
    # INTERACCIÓN DEL USUARIO CON EL CANVAS (MOUSE & CLICS)
    # -------------------------------------------------------------------------
    def _encontrar_nodo_cercano(self, cx: float, cy: float, tolerancia: float = 20.0) -> Optional[NodoEstado]:
        """Detecta si un clic o posición del cursor está cerca de un edificio."""
        todos_nodos = self.grafo.obtener_todos_los_nodos()
        mejor_nodo = None
        menor_dist = float("inf")

        for nodo in todos_nodos:
            ncx, ncy = self.plano_a_canvas(nodo.x, nodo.y)
            d = math.hypot(cx - ncx, cy - ncy)
            if d < tolerancia * self.zoom and d < menor_dist:
                menor_dist = d
                mejor_nodo = nodo

        return mejor_nodo

    def _on_canvas_click_izquierdo(self, event):
        """Maneja el clic izquierdo: selecciona origen o inicia arrastre de paneo."""
        self.arrastre_prev_x = event.x
        self.arrastre_prev_y = event.y

        nodo_click = self._encontrar_nodo_cercano(event.x, event.y)
        if nodo_click is not None:
            # Si el shift está presionado, asigna como destino; de lo contrario, alterna
            if event.state & 0x0001:  # Shift presionado
                self.establecer_destino(nodo_click.informacion)
            else:
                if self.origen_seleccionado == nodo_click.informacion:
                    # Si ya era el origen, lo intercambia a destino
                    self.establecer_destino(nodo_click.informacion)
                else:
                    self.establecer_origen(nodo_click.informacion)
            self._mostrar_ficha_edificio(nodo_click.informacion)

    def _on_canvas_click_derecho(self, event):
        """Maneja el clic derecho: menú contextual o selección directa de Destino."""
        nodo_click = self._encontrar_nodo_cercano(event.x, event.y)
        if nodo_click is not None:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(
                label=f"🟢 Establecer '{nodo_click.informacion}' como ORIGEN",
                command=lambda nid=nodo_click.informacion: self.establecer_origen(nid)
            )
            menu.add_command(
                label=f"🔴 Establecer '{nodo_click.informacion}' como DESTINO (META)",
                command=lambda nid=nodo_click.informacion: self.establecer_destino(nid)
            )
            menu.add_separator()
            menu.add_command(
                label=f"ℹ Ver Ficha Técnica de '{nodo_click.informacion}'",
                command=lambda nid=nodo_click.informacion: self._mostrar_ficha_edificio(nid)
            )
            menu.tk_popup(event.x_root, event.y_root)
        else:
            # Menú en espacio libre
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="⟲ Ajustar Vista Completa", command=self.ajustar_vista_general)
            menu.add_command(label="🔍+ Acercar", command=self.zoom_acercar)
            menu.add_command(label="🔍- Alejar", command=self.zoom_alejar)
            menu.tk_popup(event.x_root, event.y_root)

    def _on_canvas_arrastre(self, event):
        """Arrastra el lienzo para permitir paneo del campus."""
        dx = event.x - self.arrastre_prev_x
        dy = event.y - self.arrastre_prev_y
        self.offset_x += dx
        self.offset_y += dy
        self.arrastre_prev_x = event.x
        self.arrastre_prev_y = event.y
        self.redibujar_lienzo()

    def _on_canvas_mousewheel(self, event):
        """Zoom dinámico centrado en la posición del puntero del mouse."""
        factor = 1.15 if event.delta > 0 else 0.85
        nuevo_zoom = max(0.4, min(3.5, self.zoom * factor))

        # Ajustar offsets para que el zoom haga foco en el mouse
        cx, cy = event.x, event.y
        self.offset_x = cx - (cx - self.offset_x) * (nuevo_zoom / self.zoom)
        self.offset_y = cy - (cy - self.offset_y) * (nuevo_zoom / self.zoom)
        self.zoom = nuevo_zoom

        self.redibujar_lienzo()

    def _on_canvas_hover(self, event):
        """Muestra un tooltip flotante cuando el cursor se posa sobre un edificio."""
        nodo = self._encontrar_nodo_cercano(event.x, event.y, tolerancia=16.0)
        if nodo is not None:
            texto = f"[{nodo.informacion}] {nodo.nombre_completo}\nCategoría: {nodo.categoria}"
            if self.destino_seleccionado:
                nodo_meta = self.grafo.buscar_nodo(self.destino_seleccionado)
                if nodo_meta:
                    h_val = self.grafo.calcular_distancia_euclidiana(nodo, nodo_meta)
                    texto += f"\nh(n) a la meta '{self.destino_seleccionado}': {h_val:.1f} m"

            self.tooltip.configure(text=texto)
            self.tooltip.place(x=event.x + 12, y=event.y + 12)
            self.canvas.configure(cursor="hand2")
        else:
            self.tooltip.place_forget()
            self.canvas.configure(cursor="crosshair")

    # -------------------------------------------------------------------------
    # GESTIÓN DE SELECCIÓN Y COMBOS
    # -------------------------------------------------------------------------
    def _seleccionar_combo_por_id(self, combo: ttk.Combobox, ident: Optional[str]):
        """Sincroniza el ComboBox con el ID del nodo."""
        if not ident:
            return
        for i, opcion in enumerate(self.lista_opciones_nodos):
            if opcion.startswith(f"[{ident}]"):
                combo.current(i)
                break

    def _on_cambio_origen(self, event):
        opcion = self.combo_origen.get()
        ident = self.mapa_opcion_a_id.get(opcion)
        if ident:
            self.establecer_origen(ident, actualizar_combo=False)

    def _on_cambio_destino(self, event):
        opcion = self.combo_destino.get()
        ident = self.mapa_opcion_a_id.get(opcion)
        if ident:
            self.establecer_destino(ident, actualizar_combo=False)

    def establecer_origen(self, ident: str, actualizar_combo: bool = True):
        """Asigna un nuevo nodo origen y actualiza los componentes gráficos."""
        self.origen_seleccionado = ident
        if actualizar_combo:
            self._seleccionar_combo_por_id(self.combo_origen, ident)
        self._mostrar_ficha_edificio(ident)
        self.redibujar_lienzo()

    def establecer_destino(self, ident: str, actualizar_combo: bool = True):
        """Asigna un nuevo nodo meta, actualiza heurísticas del grafo y redibuja."""
        self.destino_seleccionado = ident
        if actualizar_combo:
            self._seleccionar_combo_por_id(self.combo_destino, ident)
        # Actualizar heurísticas euclidianas h(n) en la estructura enlazada
        self.grafo.actualizar_heuristicas(ident)
        self._mostrar_ficha_edificio(ident)
        self._actualizar_visor_listas_enlazadas()
        self.redibujar_lienzo()

    def intercambiar_origen_destino(self):
        """Intercambia el origen y el destino."""
        temp = self.origen_seleccionado
        self.establecer_origen(self.destino_seleccionado)
        self.establecer_destino(temp)

    # -------------------------------------------------------------------------
    # EJECUCIÓN Y PROCESAMIENTO DE ALGORITMOS DE BÚSQUEDA
    # -------------------------------------------------------------------------
    def ejecutar_busqueda(self):
        """Invoca el algoritmo seleccionado sobre el GrafoListas y presenta resultados."""
        self.detener_animacion()

        if not self.origen_seleccionado or not self.destino_seleccionado:
            messagebox.showwarning("Atención", "Por favor selecciona un Origen y un Destino.")
            return

        idx_algo = self.combo_algoritmo.current()

        # Despacho de algoritmos según el menú
        if idx_algo == 0:
            resultado = AlgoritmosBusqueda.bfs(
                self.grafo, self.origen_seleccionado, self.destino_seleccionado
            )
            explicacion = (
                "BÚSQUEDA PRIMERO EN ANCHURA (BFS):\n"
                "• Tipo: No informada con cola FIFO.\n"
                "• Garantiza encontrar el camino con la MENOR CANTIDAD DE SALTOS (aristas).\n"
                "• Al existir aristas de diferente longitud métrica en el campus, no garantiza el menor costo métrico en metros."
            )
        elif idx_algo == 1:
            resultado = AlgoritmosBusqueda.dfs(
                self.grafo, self.origen_seleccionado, self.destino_seleccionado
            )
            explicacion = (
                "BÚSQUEDA PRIMERO EN PROFUNDIDAD (DFS):\n"
                "• Tipo: No informada con pila LIFO.\n"
                "• Avanza por una rama hasta agotarla antes de retroceder (backtracking).\n"
                "• NO garantiza camino óptimo ni en saltos ni en costo métrico, produciendo rutas sinuosas."
            )
        elif idx_algo == 2:
            resultado = AlgoritmosBusqueda.greedy_best_first(
                self.grafo, self.origen_seleccionado, self.destino_seleccionado
            )
            explicacion = (
                "PRIMERO EL MEJOR (GREEDY BEST-FIRST):\n"
                "• Tipo: Informada con función de evaluación f(n) = h(n).\n"
                "• Expande el nodo que visualmente parece más cercano a la meta según la distancia en línea recta.\n"
                "• Muy rápida, pero voraz: ignora el costo acumulado g(n) ya recorrido."
            )
        elif idx_algo == 3:
            resultado = AlgoritmosBusqueda.dijkstra(
                self.grafo, self.origen_seleccionado, self.destino_seleccionado
            )
            explicacion = (
                "ALGORITMO DE DIJKSTRA (COSTO UNIFORME):\n"
                "• Tipo: Informada por costo acumulado f(n) = g(n).\n"
                "• GARANTIZA MATEMÁTICAMENTE EL CAMINO DE MENOR COSTO MÉTRICO GLOBAL.\n"
                "• Explora en ondas concéntricas sin considerar la dirección hacia la meta."
            )
        elif idx_algo == 4:
            resultado = AlgoritmosBusqueda.a_estrella(
                self.grafo, self.origen_seleccionado, self.destino_seleccionado
            )
            explicacion = (
                "BÚSQUEDA HEURÍSTICA A* (A-STAR):\n"
                "• Tipo: Informada con función f(n) = g(n) + h(n).\n"
                "• GARANTIZA LA SOLUCIÓN ÓPTIMA gracias a la heurística euclidiana admisible y consistente.\n"
                "• Enfoca la búsqueda hacia el objetivo, explorando significativamente menos nodos que Dijkstra."
            )
        elif idx_algo == 5:
            resultado = AlgoritmosBusqueda.hill_climbing(
                self.grafo, self.origen_seleccionado, self.destino_seleccionado
            )
            explicacion = (
                "ESCALADA DE COLINAS (HILL CLIMBING / BÚSQUEDA LOCAL):\n"
                "• Tipo: Búsqueda local orientada a meta (Greedy Local).\n"
                "• Desde el nodo actual selecciona el vecino con menor h(n). Si h(vecino) < h(actual) se mueve; "
                "de lo contrario SE DETIENE POR MÍNIMO LOCAL.\n"
                "• Demuestra en clase por qué los métodos locales requieren estrategias para escapar de óptimos locales."
            )
        else:
            resultado = AlgoritmosBusqueda.a_estrella(
                self.grafo, self.origen_seleccionado, self.destino_seleccionado
            )
            explicacion = "Búsqueda A*"

        self.resultado_actual = resultado
        self.paso_animacion_actual = len(resultado.pasos) if resultado.pasos else 0

        # Actualizar componentes de resultados
        self._actualizar_panel_resultados(resultado, explicacion)
        self._poblar_tabla_traza(resultado)
        self.redibujar_lienzo()

    def limpiar_busqueda(self):
        """Reinicia la búsqueda, limpia resaltados y trazas."""
        self.detener_animacion()
        self.resultado_actual = None
        self.paso_animacion_actual = 0

        self.lbl_estado_resultado.configure(
            text="Esperando ejecución...",
            bg="#e2e8f0",
            fg="#334155"
        )
        self.txt_camino.configure(state="normal")
        self.txt_camino.delete("1.0", tk.END)
        self.txt_camino.insert(tk.END, "Búsqueda reiniciada. Selecciona parámetros y ejecuta.")
        self.txt_camino.configure(state="disabled")

        self.lbl_costo_total.configure(text="Costo Total: -- m")
        self.lbl_nodos_explorados.configure(text="Explorados: --")
        self.lbl_tiempo_ejec.configure(text="Tiempo: -- ms")

        self.txt_explicacion.configure(state="normal")
        self.txt_explicacion.delete("1.0", tk.END)
        self.txt_explicacion.insert(tk.END, "Listo para nueva prueba.")
        self.txt_explicacion.configure(state="disabled")

        # Limpiar tabla de traza
        for item in self.tree_traza.get_children():
            self.tree_traza.delete(item)

        self.lbl_paso_contador.configure(text="Paso: 0 / 0")
        self.progreso_animacion["value"] = 0

        self.redibujar_lienzo()

    def _actualizar_panel_resultados(self, res: ResultadoBusqueda, explicacion: str):
        """Escribe las métricas obtenidas en el panel lateral."""
        if res.exito:
            self.lbl_estado_resultado.configure(
                text=f"✔ ÉXITO: {res.algoritmo.split(' - ')[0]}",
                bg="#dcfce7",
                fg="#15803d"
            )
        else:
            self.lbl_estado_resultado.configure(
                text=f"⚠ DETENIDO: {res.algoritmo.split(' - ')[0]}",
                bg="#fef3c7",
                fg="#b45309"
            )

        # Secuencia del camino
        self.txt_camino.configure(state="normal")
        self.txt_camino.delete("1.0", tk.END)
        if res.camino:
            camino_legible = " ➔ ".join(res.camino)
            self.txt_camino.insert(tk.END, camino_legible)
        else:
            self.txt_camino.insert(tk.END, "Sin camino encontrado.")
        self.txt_camino.configure(state="disabled")

        # Métricas
        self.lbl_costo_total.configure(text=f"Costo Total: {res.costo_total:.1f} m")
        total_grafo = self.grafo.total_nodos
        porcentaje_explorado = (len(res.nodos_explorados) / total_grafo) * 100
        self.lbl_nodos_explorados.configure(
            text=f"Explorados: {len(res.nodos_explorados)} de {total_grafo} ({porcentaje_explorado:.0f}%)"
        )
        self.lbl_tiempo_ejec.configure(text=f"Tiempo: {res.tiempo_ms:.2f} ms")

        # Explicación
        self.txt_explicacion.configure(state="normal")
        self.txt_explicacion.delete("1.0", tk.END)
        self.txt_explicacion.insert(tk.END, f"{explicacion}\n\nDetalle: {res.mensaje}")
        self.txt_explicacion.configure(state="disabled")

        # Contador de pasos de animación
        total_pasos = len(res.pasos)
        self.lbl_paso_contador.configure(text=f"Paso: {total_pasos} / {total_pasos}")
        self.progreso_animacion["maximum"] = max(1, total_pasos)
        self.progreso_animacion["value"] = total_pasos

    def _poblar_tabla_traza(self, res: ResultadoBusqueda):
        """Llena el Treeview con cada fila del historial de exploración."""
        for item in self.tree_traza.get_children():
            self.tree_traza.delete(item)

        for paso in res.pasos:
            p_num = paso.get("paso", 0)
            nodo = paso.get("nodo_actual", "")
            accion = paso.get("accion", "")
            g = f"{paso.get('g', 0.0):.1f}"
            h = f"{paso.get('h', 0.0):.1f}"
            f = f"{paso.get('f', 0.0):.1f}"

            self.tree_traza.insert("", tk.END, values=(p_num, nodo, accion, g, h, f))

    def _on_seleccionar_fila_traza(self, event):
        """Al hacer clic en una fila de la traza, sincroniza la visualización con ese paso."""
        if getattr(self, "_bloqueo_evento_traza", False):
            return

        seleccion = self.tree_traza.selection()
        if seleccion:
            item = self.tree_traza.item(seleccion[0])
            valores = item.get("values")
            if valores:
                paso_num = int(valores[0])
                if paso_num != self.paso_animacion_actual:
                    self.ir_al_paso(paso_num)

    # -------------------------------------------------------------------------
    # ANIMACIÓN INTERACTIVA PASO A PASO
    # -------------------------------------------------------------------------
    def toggle_reproduccion_animacion(self):
        """Inicia o pausa la animación automática."""
        if not self.resultado_actual:
            self.ejecutar_busqueda()
            if not self.resultado_actual:
                return

        if self.animacion_activa:
            self.detener_animacion()
        else:
            self.iniciar_animacion()

    def iniciar_animacion(self):
        """Arranca el bucle de animación con temporizador Tkinter de forma asíncrona."""
        if not self.resultado_actual or not self.resultado_actual.pasos:
            return

        self.animacion_activa = True
        self.btn_reproducir.configure(text="⏸ Pausar", bg="#e11d48")

        # Si ya estábamos al final, reiniciar desde el paso 0
        if self.paso_animacion_actual >= len(self.resultado_actual.pasos):
            self.paso_animacion_actual = 0

        # Cancelar cualquier tarea programada anterior
        if self.tarea_after_animacion:
            self.root.after_cancel(self.tarea_after_animacion)
            self.tarea_after_animacion = None

        try:
            delay = max(30, int(self.var_velocidad_animacion.get()))
        except Exception:
            delay = 300

        # Iniciar el primer paso mediante after para no bloquear el bucle de eventos
        self.tarea_after_animacion = self.root.after(delay, self._bucle_animacion)

    def detener_animacion(self):
        """Pausa la animación."""
        self.animacion_activa = False
        self.btn_reproducir.configure(text="▶ Animar", bg="#0284c7")
        if self.tarea_after_animacion:
            self.root.after_cancel(self.tarea_after_animacion)
            self.tarea_after_animacion = None

    def _bucle_animacion(self):
        """Paso recurrente de la animación automática."""
        if not self.animacion_activa or not self.resultado_actual:
            return

        if self.paso_animacion_actual < len(self.resultado_actual.pasos):
            self.paso_animacion_actual += 1
            self.ir_al_paso(self.paso_animacion_actual)
            
            if self.paso_animacion_actual < len(self.resultado_actual.pasos):
                try:
                    delay = max(30, int(self.var_velocidad_animacion.get()))
                except Exception:
                    delay = 300
                self.tarea_after_animacion = self.root.after(delay, self._bucle_animacion)
            else:
                self.detener_animacion()
        else:
            self.detener_animacion()

    def paso_siguiente(self):
        """Avanza manualmente al siguiente paso de exploración."""
        if not self.resultado_actual:
            self.ejecutar_busqueda()
            return
        if self.paso_animacion_actual < len(self.resultado_actual.pasos):
            self.paso_animacion_actual += 1
            self.ir_al_paso(self.paso_animacion_actual)

    def paso_anterior(self):
        """Retrocede manualmente al paso anterior de exploración."""
        if not self.resultado_actual:
            return
        if self.paso_animacion_actual > 1:
            self.paso_animacion_actual -= 1
            self.ir_al_paso(self.paso_animacion_actual)

    def ir_al_paso(self, num_paso: int):
        """Actualiza la visualización gráfica en un paso específico del algoritmo."""
        if not self.resultado_actual or not self.resultado_actual.pasos:
            return

        total_pasos = len(self.resultado_actual.pasos)
        num_paso = max(1, min(total_pasos, num_paso))
        self.paso_animacion_actual = num_paso

        self.lbl_paso_contador.configure(text=f"Paso: {num_paso} / {total_pasos}")
        self.progreso_animacion["value"] = num_paso

        # Sincronizar selección en la tabla Treeview protegiendo contra recursión infinita
        self._bloqueo_evento_traza = True
        try:
            children = self.tree_traza.get_children()
            if 0 <= num_paso - 1 < len(children):
                item_id = children[num_paso - 1]
                self.tree_traza.selection_set(item_id)
                self.tree_traza.see(item_id)
        finally:
            self._bloqueo_evento_traza = False

        self.redibujar_lienzo()

    # -------------------------------------------------------------------------
    # INSPECCIÓN TÉCNICA DE ESTRUCTURAS EN MEMORIA Y FICHAS
    # -------------------------------------------------------------------------
    def _actualizar_visor_listas_enlazadas(self, event=None):
        """
        Recorre explícitamente los punteros de la estructura enlazada en memoria
        y los muestra en formato de texto didáctico para que los estudiantes
        observen la arquitectura interna exigida:
        NodoEstado (informacion, sig_nodo, lista_adyacentes)
        -> NodoAdyacente (peso, valor_heuristico, nodo_referencia, sig_adyacente)
        """
        nodo_id = self.combo_inspeccionar_nodo.get()
        nodo = self.grafo.buscar_nodo(nodo_id)
        if not nodo:
            return

        lineas = []
        lineas.append("=" * 55)
        lineas.append(f"INSPECCIÓN DE LISTA ENLAZADA: ESTADO '{nodo.informacion}'")
        lineas.append("=" * 55)
        lineas.append(f"• informacion      : '{nodo.informacion}'")
        lineas.append(f"• nombre_completo  : '{nodo.nombre_completo}'")
        lineas.append(f"• coordenadas (X,Y): ({nodo.x:.0f}, {nodo.y:.0f})")

        sig_id = nodo.sig_nodo.informacion if nodo.sig_nodo else "None (Fin de Lista Principal)"
        lineas.append(f"• sig_nodo (Puntero): -> NodoEstado('{sig_id}')")
        lineas.append("-" * 55)
        lineas.append("SUB-LISTA ENLAZADA DE ADYACENCIAS (lista_adyacentes):")
        lineas.append("-" * 55)

        curr_ady = nodo.lista_adyacentes
        indice = 1
        if curr_ady is None:
            lineas.append("  (Sin adyacencias enlazadas)")
        else:
            while curr_ady is not None:
                destino_id = curr_ady.nodo_referencia.informacion if curr_ady.nodo_referencia else "None"
                sig_ady_id = (
                    curr_ady.sig_adyacente.nodo_referencia.informacion
                    if curr_ady.sig_adyacente and curr_ady.sig_adyacente.nodo_referencia
                    else "None (Fin de Adyacencias)"
                )
                lineas.append(f"  [{indice}] NodoAdyacente:")
                lineas.append(f"      ├─ nodo_referencia : -> NodoEstado('{destino_id}')")
                lineas.append(f"      ├─ peso            : {curr_ady.peso:.1f} m")
                lineas.append(f"      ├─ valor_heuristico: {curr_ady.valor_heuristico:.1f} (h a meta)")
                lineas.append(f"      └─ sig_adyacente   : -> NodoAdyacente('{sig_ady_id}')")
                curr_ady = curr_ady.sig_adyacente
                indice += 1

        lineas.append("=" * 55)

        self.txt_listas_enlazadas.configure(state="normal")
        self.txt_listas_enlazadas.delete("1.0", tk.END)
        self.txt_listas_enlazadas.insert(tk.END, "\n".join(lineas))
        self.txt_listas_enlazadas.configure(state="disabled")

    def _mostrar_ficha_edificio(self, ident: Optional[str]):
        """Muestra los datos oficiales y catálogo del edificio seleccionado."""
        if not ident:
            return

        nodo = self.grafo.buscar_nodo(ident)
        if not nodo:
            return

        datos_catalog = EDIFICIOS_CAMPUS.get(ident, {})

        # Listar conexiones directas
        conexiones = []
        ady = nodo.lista_adyacentes
        while ady is not None:
            ref = ady.nodo_referencia
            conexiones.append(f"• [{ref.informacion}] {ref.nombre_completo} ({ady.peso:.0f} m)")
            ady = ady.sig_adyacente

        con_str = "\n".join(conexiones) if conexiones else "Ninguna"

        texto = (
            f"EDIFICIO: [{nodo.informacion}] {nodo.nombre_completo}\n"
            f"{'='*40}\n"
            f"Categoría: {nodo.categoria}\n"
            f"Coordenadas en Plano: ({nodo.x:.0f}, {nodo.y:.0f})\n\n"
            f"DESCRIPCIÓN ACADÉMICA / OFICIAL:\n"
            f"{datos_catalog.get('descripcion', nodo.descripcion or 'Instalaciones del ITCG')}\n\n"
            f"ANDADORES Y CONEXIONES PEATONALES DIRECTAS:\n"
            f"{con_str}\n"
        )

        self.txt_ficha_edificio.configure(state="normal")
        self.txt_ficha_edificio.delete("1.0", tk.END)
        self.txt_ficha_edificio.insert(tk.END, texto)
        self.txt_ficha_edificio.configure(state="disabled")

        # Sincronizar el combo del visor de listas
        if hasattr(self, "combo_inspeccionar_nodo"):
            self.combo_inspeccionar_nodo.set(ident)
            self._actualizar_visor_listas_enlazadas()
