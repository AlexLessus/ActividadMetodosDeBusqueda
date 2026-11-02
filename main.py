# -*- coding: utf-8 -*-
"""
===============================================================================
INSTITUTO TECNOLÓGICO DE CIUDAD GUZMÁN (ITCG) - TECNOLÓGICO NACIONAL DE MÉXICO
DEPARTAMENTO DE SISTEMAS Y COMPUTACIÓN
MATERIA: INTELIGENCIA ARTIFICIAL (UNIDADES 1 Y 3)
PROYECTO: SIMULADOR DE MÉTODOS DE BÚSQUEDA SOBRE EL MAPA DEL ITCG
===============================================================================

Autores: Proyecto Didáctico de Inteligencia Artificial
Arquitectura:
  - nodo.py: Clases NodoEstado y NodoAdyacente (Estructuras de Listas Enlazadas)
  - grafo.py: Clase GrafoListas (Manejo de vértices, aristas y heurísticas)
  - campus_data.py: Catálogo oficial de edificios A-Z, L1, Accesos 1-4 del ITCG
  - algoritmos.py: BFS, DFS, Greedy Best-First, Dijkstra, A*, Hill Climbing
  - interfaz.py: Interfaz gráfica interactiva en Tkinter + Pillow con Canvas

Ejecución:
  python main.py
===============================================================================
"""

import sys
import tkinter as tk
from tkinter import messagebox

# Optimización de alta resolución (High-DPI) para pantallas modernas en Windows
if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from interfaz import InterfazGrafica


def main():
    """Punto de entrada principal de la aplicación."""
    try:
        root = tk.Tk()
        
        # Configurar icono o propiedades de la ventana si están disponibles
        root.title("ITCG - Inteligencia Artificial: Métodos de Búsqueda sobre Grafos")
        
        app = InterfazGrafica(root)
        root.mainloop()
    except Exception as e:
        print(f"[FATAL ERROR] Error al iniciar la aplicación gráfica: {e}")
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Error de Inicio", f"Ocurrió un error al iniciar la aplicación:\n\n{e}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
