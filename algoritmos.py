# -*- coding: utf-8 -*-
"""
===============================================================================
INSTITUTO TECNOLÓGICO DE CIUDAD GUZMÁN (ITCG) - TECNOLÓGICO NACIONAL DE MÉXICO
Materia: Inteligencia Artificial (Unidades 1 y 3)
Módulo: Algoritmos de Búsqueda (No Informados, Informados y Locales)
===============================================================================

Este módulo implementa los 6 algoritmos de búsqueda requeridos por la especificación:
1. Búsqueda Primero en Anchura (BFS) - No informada.
2. Búsqueda Primero en Profundidad (DFS) - No informada.
3. Búsqueda Primero el Mejor (Greedy Best-First) - Informada f(n) = h(n).
4. Algoritmo de Dijkstra / Costo Uniforme - Informada por costo acumulado f(n) = g(n).
5. Búsqueda Heurística A* - Informada f(n) = g(n) + h(n).
6. Búsqueda Local (Hill Climbing / Escalada de Colinas) - Búsqueda local orientada a meta.

Todos los algoritmos operan estrictamente sobre la estructura de Listas Enlazadas
(NodoEstado -> sig_nodo, lista_adyacentes -> sig_adyacente) y registran métricas
pedagógicas completas (nodos explorados, costos, tiempo, pasos de exploración).
===============================================================================
"""

import time
import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set, Any
from grafo import GrafoListas
from nodo import NodoEstado, NodoAdyacente


@dataclass
class ResultadoBusqueda:
    """
    Estructura de datos que encapsula el resultado y las métricas de una búsqueda.
    """
    exito: bool
    algoritmo: str
    origen: str
    destino: str
    camino: List[str] = field(default_factory=list)
    costo_total: float = 0.0
    nodos_explorados: List[str] = field(default_factory=list)
    aristas_camino: List[Tuple[str, str]] = field(default_factory=list)
    tiempo_ms: float = 0.0
    max_frontera: int = 0
    mensaje: str = ""
    pasos: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def longitud_camino(self) -> int:
        return len(self.camino)

    @property
    def total_explorados(self) -> int:
        return len(self.nodos_explorados)


class AlgoritmosBusqueda:
    """
    Colección de algoritmos de Inteligencia Artificial para resolución de problemas
    mediante búsqueda en espacios de estados sobre grafos enlazados.
    """

    # -------------------------------------------------------------------------
    # 1. BÚSQUEDA PRIMERO EN ANCHURA (BFS) - NO INFORMADA
    # -------------------------------------------------------------------------
    @staticmethod
    def bfs(grafo: GrafoListas, origen_id: str, destino_id: str) -> ResultadoBusqueda:
        """
        Búsqueda Primero en Anchura (Breadth-First Search).
        
        - Tipo: Búsqueda No Informada.
        - Estructura de Frontera: Cola FIFO (First-In, First-Out).
        - Estrategia: Expande sistemáticamente todos los nodos de profundidad d
          antes de pasar a los nodos de profundidad d+1.
        - Garantía: Encuentra el camino con el menor número de saltos (aristas).
        """
        tiempo_inicio = time.perf_counter()
        origen_nodo = grafo.buscar_nodo(origen_id)
        destino_nodo = grafo.buscar_nodo(destino_id)

        if origen_nodo is None or destino_nodo is None:
            return ResultadoBusqueda(
                exito=False, algoritmo="BFS", origen=origen_id, destino=destino_id,
                mensaje="Nodo origen o destino inexistente en el grafo."
            )

        if origen_id == destino_id:
            tiempo_fin = time.perf_counter()
            return ResultadoBusqueda(
                exito=True, algoritmo="BFS", origen=origen_id, destino=destino_id,
                camino=[origen_id], costo_total=0.0, nodos_explorados=[origen_id],
                tiempo_ms=(tiempo_fin - tiempo_inicio) * 1000,
                mensaje="El origen y el destino son el mismo edificio."
            )

        # Cola FIFO: almacena (identificador_nodo, camino_actual, costo_acumulado)
        cola: deque = deque([(origen_id, [origen_id], 0.0)])
        visitados: Set[str] = {origen_id}
        explorados_orden: List[str] = []
        pasos: List[Dict[str, Any]] = []
        max_frontera = 1
        paso_num = 0

        while cola:
            max_frontera = max(max_frontera, len(cola))
            actual_id, camino, costo_acum = cola.popleft()
            explorados_orden.append(actual_id)
            paso_num += 1

            pasos.append({
                "paso": paso_num,
                "nodo_actual": actual_id,
                "accion": f"Expande nodo '{actual_id}'",
                "frontera": [item[0] for item in cola],
                "visitados": list(visitados),
                "g": round(costo_acum, 1),
                "h": 0.0,
                "f": round(costo_acum, 1),
                "camino_actual": list(camino)
            })

            # Prueba de meta al expandir
            if actual_id == destino_id:
                tiempo_fin = time.perf_counter()
                aristas = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
                return ResultadoBusqueda(
                    exito=True, algoritmo="BFS (Primero en Anchura)",
                    origen=origen_id, destino=destino_id,
                    camino=camino, costo_total=round(costo_acum, 1),
                    nodos_explorados=explorados_orden,
                    aristas_camino=aristas,
                    tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
                    max_frontera=max_frontera,
                    mensaje=f"Meta alcanzada exitosamente en {len(camino)-1} saltos.",
                    pasos=pasos
                )

            # Obtener el NodoEstado del grafo para recorrer su lista enlazada de adyacentes
            nodo_estado = grafo.buscar_nodo(actual_id)
            if nodo_estado:
                # Recorrer lista enlazada de adyacentes: lista_adyacentes -> sig_adyacente
                curr_ady = nodo_estado.lista_adyacentes
                while curr_ady is not None:
                    vecino_id = curr_ady.nodo_referencia.informacion
                    if vecino_id not in visitados:
                        visitados.add(vecino_id)
                        nuevo_costo = costo_acum + curr_ady.peso
                        cola.append((vecino_id, camino + [vecino_id], nuevo_costo))
                    curr_ady = curr_ady.sig_adyacente

        tiempo_fin = time.perf_counter()
        return ResultadoBusqueda(
            exito=False, algoritmo="BFS (Primero en Anchura)",
            origen=origen_id, destino=destino_id,
            nodos_explorados=explorados_orden,
            tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
            max_frontera=max_frontera,
            mensaje="No existe camino transitable entre el origen y el destino.",
            pasos=pasos
        )

    # -------------------------------------------------------------------------
    # 2. BÚSQUEDA PRIMERO EN PROFUNDIDAD (DFS) - NO INFORMADA
    # -------------------------------------------------------------------------
    @staticmethod
    def dfs(grafo: GrafoListas, origen_id: str, destino_id: str) -> ResultadoBusqueda:
        """
        Búsqueda Primero en Profundidad (Depth-First Search).
        
        - Tipo: Búsqueda No Informada.
        - Estructura de Frontera: Pila LIFO (Last-In, First-Out).
        - Estrategia: Explora siempre el nodo más profundo del árbol de búsqueda.
        - Características: Bajo consumo de memoria O(b*m), pero no garantiza
          ni el camino más corto en saltos ni la solución de menor costo.
        """
        tiempo_inicio = time.perf_counter()
        origen_nodo = grafo.buscar_nodo(origen_id)
        destino_nodo = grafo.buscar_nodo(destino_id)

        if origen_nodo is None or destino_nodo is None:
            return ResultadoBusqueda(
                exito=False, algoritmo="DFS", origen=origen_id, destino=destino_id,
                mensaje="Nodo origen o destino inexistente en el grafo."
            )

        if origen_id == destino_id:
            tiempo_fin = time.perf_counter()
            return ResultadoBusqueda(
                exito=True, algoritmo="DFS", origen=origen_id, destino=destino_id,
                camino=[origen_id], costo_total=0.0, nodos_explorados=[origen_id],
                tiempo_ms=(tiempo_fin - tiempo_inicio) * 1000,
                mensaje="El origen y el destino son el mismo edificio."
            )

        # Pila LIFO: almacena (identificador_nodo, camino_actual, costo_acumulado)
        pila: List[Tuple[str, List[str], float]] = [(origen_id, [origen_id], 0.0)]
        visitados: Set[str] = set()
        explorados_orden: List[str] = []
        pasos: List[Dict[str, Any]] = []
        max_frontera = 1
        paso_num = 0

        while pila:
            max_frontera = max(max_frontera, len(pila))
            actual_id, camino, costo_acum = pila.pop()

            if actual_id in visitados:
                continue

            visitados.add(actual_id)
            explorados_orden.append(actual_id)
            paso_num += 1

            pasos.append({
                "paso": paso_num,
                "nodo_actual": actual_id,
                "accion": f"Expande nodo en profundidad '{actual_id}'",
                "frontera": [item[0] for item in pila],
                "visitados": list(visitados),
                "g": round(costo_acum, 1),
                "h": 0.0,
                "f": round(costo_acum, 1),
                "camino_actual": list(camino)
            })

            # Prueba de meta
            if actual_id == destino_id:
                tiempo_fin = time.perf_counter()
                aristas = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
                return ResultadoBusqueda(
                    exito=True, algoritmo="DFS (Primero en Profundidad)",
                    origen=origen_id, destino=destino_id,
                    camino=camino, costo_total=round(costo_acum, 1),
                    nodos_explorados=explorados_orden,
                    aristas_camino=aristas,
                    tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
                    max_frontera=max_frontera,
                    mensaje=f"Camino en profundidad encontrado ({len(camino)-1} saltos).",
                    pasos=pasos
                )

            # Recorrer lista enlazada de adyacentes
            nodo_estado = grafo.buscar_nodo(actual_id)
            if nodo_estado:
                curr_ady = nodo_estado.lista_adyacentes
                # Guardar adyacentes para apilar
                vecinos = []
                while curr_ady is not None:
                    vecinos.append((curr_ady.nodo_referencia.informacion, curr_ady.peso))
                    curr_ady = curr_ady.sig_adyacente

                # Apilamos en orden inverso para preservar el orden natural de visita
                for vec_id, peso in reversed(vecinos):
                    if vec_id not in visitados:
                        pila.append((vec_id, camino + [vec_id], costo_acum + peso))

        tiempo_fin = time.perf_counter()
        return ResultadoBusqueda(
            exito=False, algoritmo="DFS (Primero en Profundidad)",
            origen=origen_id, destino=destino_id,
            nodos_explorados=explorados_orden,
            tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
            max_frontera=max_frontera,
            mensaje="No existe camino transitable entre el origen y el destino.",
            pasos=pasos
        )

    # -------------------------------------------------------------------------
    # 3. BÚSQUEDA PRIMERO EL MEJOR (GREEDY BEST-FIRST) - INFORMADA
    # -------------------------------------------------------------------------
    @staticmethod
    def greedy_best_first(grafo: GrafoListas, origen_id: str, destino_id: str) -> ResultadoBusqueda:
        """
        Búsqueda Primero el Mejor (Greedy Best-First Search / Búsqueda Voraz).
        
        - Tipo: Búsqueda Informada.
        - Función de Evaluación: f(n) = h(n).
        - Estructura de Frontera: Cola de Prioridad ordenada estrictamente por h(n).
        - Estrategia: Expande siempre el nodo que parece estar más cerca de la meta
          según la distancia euclidiana en línea recta.
        - Nota Pedagógica: Es muy rápida pero NO es óptima en costo acumulado g(n).
        """
        tiempo_inicio = time.perf_counter()
        grafo.actualizar_heuristicas(destino_id)
        origen_nodo = grafo.buscar_nodo(origen_id)
        destino_nodo = grafo.buscar_nodo(destino_id)

        if origen_nodo is None or destino_nodo is None:
            return ResultadoBusqueda(
                exito=False, algoritmo="Greedy Best-First", origen=origen_id, destino=destino_id,
                mensaje="Nodo origen o destino inexistente en el grafo."
            )

        h_inicial = grafo.calcular_distancia_euclidiana(origen_nodo, destino_nodo)

        # Cola de prioridad: tupla (h, contador_desempate, actual_id, camino, costo_g)
        contador = 0
        frontera: List[Tuple[float, int, str, List[str], float]] = []
        heapq.heappush(frontera, (h_inicial, contador, origen_id, [origen_id], 0.0))

        visitados: Set[str] = set()
        explorados_orden: List[str] = []
        pasos: List[Dict[str, Any]] = []
        max_frontera = 1
        paso_num = 0

        while frontera:
            max_frontera = max(max_frontera, len(frontera))
            h_actual, _, actual_id, camino, costo_g = heapq.heappop(frontera)

            if actual_id in visitados:
                continue

            visitados.add(actual_id)
            explorados_orden.append(actual_id)
            paso_num += 1

            pasos.append({
                "paso": paso_num,
                "nodo_actual": actual_id,
                "accion": f"Expande vorazmente '{actual_id}' (h={h_actual:.1f})",
                "frontera": [item[2] for item in frontera],
                "visitados": list(visitados),
                "g": round(costo_g, 1),
                "h": round(h_actual, 1),
                "f": round(h_actual, 1),
                "camino_actual": list(camino)
            })

            if actual_id == destino_id:
                tiempo_fin = time.perf_counter()
                aristas = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
                return ResultadoBusqueda(
                    exito=True, algoritmo="Greedy Best-First (Voraz)",
                    origen=origen_id, destino=destino_id,
                    camino=camino, costo_total=round(costo_g, 1),
                    nodos_explorados=explorados_orden,
                    aristas_camino=aristas,
                    tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
                    max_frontera=max_frontera,
                    mensaje=f"Meta alcanzada mediante heurística voraz f(n)=h(n)={h_actual:.1f}.",
                    pasos=pasos
                )

            nodo_estado = grafo.buscar_nodo(actual_id)
            if nodo_estado:
                curr_ady = nodo_estado.lista_adyacentes
                while curr_ady is not None:
                    vecino = curr_ady.nodo_referencia
                    vecino_id = vecino.informacion
                    if vecino_id not in visitados:
                        contador += 1
                        h_vecino = curr_ady.valor_heuristico
                        nuevo_g = costo_g + curr_ady.peso
                        heapq.heappush(
                            frontera,
                            (h_vecino, contador, vecino_id, camino + [vecino_id], nuevo_g)
                        )
                    curr_ady = curr_ady.sig_adyacente

        tiempo_fin = time.perf_counter()
        return ResultadoBusqueda(
            exito=False, algoritmo="Greedy Best-First (Voraz)",
            origen=origen_id, destino=destino_id,
            nodos_explorados=explorados_orden,
            tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
            max_frontera=max_frontera,
            mensaje="No se encontró solución con la heurística voraz.",
            pasos=pasos
        )

    # -------------------------------------------------------------------------
    # 4. ALGORITMO DE DIJKSTRA (COSTO UNIFORME) - INFORMADA POR COSTO g(n)
    # -------------------------------------------------------------------------
    @staticmethod
    def dijkstra(grafo: GrafoListas, origen_id: str, destino_id: str) -> ResultadoBusqueda:
        """
        Algoritmo de Dijkstra / Búsqueda de Costo Uniforme (UCS).
        
        - Tipo: Búsqueda orientada por costo de trayectoria real.
        - Función de Evaluación: f(n) = g(n).
        - Estructura de Frontera: Cola de Prioridad basada en costo acumulado g(n).
        - Garantía Teórica: Encuentra SIEMPRE el camino de mínimo costo métrico
          global en grafos con pesos no negativos.
        """
        tiempo_inicio = time.perf_counter()
        origen_nodo = grafo.buscar_nodo(origen_id)
        destino_nodo = grafo.buscar_nodo(destino_id)

        if origen_nodo is None or destino_nodo is None:
            return ResultadoBusqueda(
                exito=False, algoritmo="Dijkstra", origen=origen_id, destino=destino_id,
                mensaje="Nodo origen o destino inexistente en el grafo."
            )

        # Cola de prioridad: tupla (g_acumulado, contador, actual_id, camino)
        contador = 0
        frontera: List[Tuple[float, int, str, List[str]]] = []
        heapq.heappush(frontera, (0.0, contador, origen_id, [origen_id]))

        mejores_g: Dict[str, float] = {origen_id: 0.0}
        visitados: Set[str] = set()
        explorados_orden: List[str] = []
        pasos: List[Dict[str, Any]] = []
        max_frontera = 1
        paso_num = 0

        while frontera:
            max_frontera = max(max_frontera, len(frontera))
            g_actual, _, actual_id, camino = heapq.heappop(frontera)

            if actual_id in visitados:
                continue

            visitados.add(actual_id)
            explorados_orden.append(actual_id)
            paso_num += 1

            pasos.append({
                "paso": paso_num,
                "nodo_actual": actual_id,
                "accion": f"Expande con costo mínimo g={g_actual:.1f} m",
                "frontera": [item[2] for item in frontera],
                "visitados": list(visitados),
                "g": round(g_actual, 1),
                "h": 0.0,
                "f": round(g_actual, 1),
                "camino_actual": list(camino)
            })

            # Prueba de meta al extraer de la frontera (garantía de optimalidad de Dijkstra)
            if actual_id == destino_id:
                tiempo_fin = time.perf_counter()
                aristas = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
                return ResultadoBusqueda(
                    exito=True, algoritmo="Dijkstra (Costo Uniforme)",
                    origen=origen_id, destino=destino_id,
                    camino=camino, costo_total=round(g_actual, 1),
                    nodos_explorados=explorados_orden,
                    aristas_camino=aristas,
                    tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
                    max_frontera=max_frontera,
                    mensaje=f"Camino de costo mínimo óptimo demostrado: {g_actual:.1f} m.",
                    pasos=pasos
                )

            nodo_estado = grafo.buscar_nodo(actual_id)
            if nodo_estado:
                curr_ady = nodo_estado.lista_adyacentes
                while curr_ady is not None:
                    vecino_id = curr_ady.nodo_referencia.informacion
                    peso_arista = curr_ady.peso
                    costo_hacia_vecino = g_actual + peso_arista

                    if vecino_id not in mejores_g or costo_hacia_vecino < mejores_g[vecino_id]:
                        mejores_g[vecino_id] = costo_hacia_vecino
                        contador += 1
                        heapq.heappush(
                            frontera,
                            (costo_hacia_vecino, contador, vecino_id, camino + [vecino_id])
                        )
                    curr_ady = curr_ady.sig_adyacente

        tiempo_fin = time.perf_counter()
        return ResultadoBusqueda(
            exito=False, algoritmo="Dijkstra (Costo Uniforme)",
            origen=origen_id, destino=destino_id,
            nodos_explorados=explorados_orden,
            tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
            max_frontera=max_frontera,
            mensaje="No existe camino transitable hacia el destino.",
            pasos=pasos
        )

    # -------------------------------------------------------------------------
    # 5. BÚSQUEDA HEURÍSTICA A* (A-STAR) - INFORMADA
    # -------------------------------------------------------------------------
    @staticmethod
    def a_estrella(grafo: GrafoListas, origen_id: str, destino_id: str) -> ResultadoBusqueda:
        """
        Búsqueda Heurística A* (A-Star Search).
        
        - Tipo: Búsqueda Informada Óptima y Completa.
        - Función de Evaluación: f(n) = g(n) + h(n)
          donde:
            g(n): Costo acumulado real desde el origen hasta el nodo n.
            h(n): Distancia euclidiana en línea recta desde n hasta la meta.
        - Garantía Teórica: Dado que h(n) es la distancia euclidiana 2D, es ADMISIBLE
          (nunca sobreestima) y CONSISTENTE (cumple la desigualdad del triángulo).
          Por lo tanto, A* garantiza encontrar la solución óptima expandiendo
          el menor número posible de nodos.
        """
        tiempo_inicio = time.perf_counter()
        grafo.actualizar_heuristicas(destino_id)
        origen_nodo = grafo.buscar_nodo(origen_id)
        destino_nodo = grafo.buscar_nodo(destino_id)

        if origen_nodo is None or destino_nodo is None:
            return ResultadoBusqueda(
                exito=False, algoritmo="A*", origen=origen_id, destino=destino_id,
                mensaje="Nodo origen o destino inexistente en el grafo."
            )

        h_inicial = grafo.calcular_distancia_euclidiana(origen_nodo, destino_nodo)
        f_inicial = 0.0 + h_inicial

        # Cola de prioridad: tupla (f, contador, actual_id, camino, g, h)
        contador = 0
        frontera: List[Tuple[float, int, str, List[str], float, float]] = []
        heapq.heappush(frontera, (f_inicial, contador, origen_id, [origen_id], 0.0, h_inicial))

        mejores_g: Dict[str, float] = {origen_id: 0.0}
        visitados: Set[str] = set()
        explorados_orden: List[str] = []
        pasos: List[Dict[str, Any]] = []
        max_frontera = 1
        paso_num = 0

        while frontera:
            max_frontera = max(max_frontera, len(frontera))
            f_actual, _, actual_id, camino, g_actual, h_actual = heapq.heappop(frontera)

            if actual_id in visitados:
                continue

            visitados.add(actual_id)
            explorados_orden.append(actual_id)
            paso_num += 1

            pasos.append({
                "paso": paso_num,
                "nodo_actual": actual_id,
                "accion": f"Expande con f={f_actual:.1f} (g={g_actual:.1f}, h={h_actual:.1f})",
                "frontera": [item[2] for item in frontera],
                "visitados": list(visitados),
                "g": round(g_actual, 1),
                "h": round(h_actual, 1),
                "f": round(f_actual, 1),
                "camino_actual": list(camino)
            })

            # Prueba de meta al extraer de la frontera
            if actual_id == destino_id:
                tiempo_fin = time.perf_counter()
                aristas = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
                return ResultadoBusqueda(
                    exito=True, algoritmo="Búsqueda Heurística A*",
                    origen=origen_id, destino=destino_id,
                    camino=camino, costo_total=round(g_actual, 1),
                    nodos_explorados=explorados_orden,
                    aristas_camino=aristas,
                    tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
                    max_frontera=max_frontera,
                    mensaje=(
                        f"Solución óptima A* garantizada: costo={g_actual:.1f} m, "
                        f"explorando {len(explorados_orden)} nodos con heurística euclidiana consistente."
                    ),
                    pasos=pasos
                )

            nodo_estado = grafo.buscar_nodo(actual_id)
            if nodo_estado:
                curr_ady = nodo_estado.lista_adyacentes
                while curr_ady is not None:
                    vecino = curr_ady.nodo_referencia
                    vecino_id = vecino.informacion
                    nuevo_g = g_actual + curr_ady.peso
                    h_vecino = curr_ady.valor_heuristico
                    nuevo_f = nuevo_g + h_vecino

                    if vecino_id not in mejores_g or nuevo_g < mejores_g[vecino_id]:
                        mejores_g[vecino_id] = nuevo_g
                        contador += 1
                        heapq.heappush(
                            frontera,
                            (nuevo_f, contador, vecino_id, camino + [vecino_id], nuevo_g, h_vecino)
                        )
                    curr_ady = curr_ady.sig_adyacente

        tiempo_fin = time.perf_counter()
        return ResultadoBusqueda(
            exito=False, algoritmo="Búsqueda Heurística A*",
            origen=origen_id, destino=destino_id,
            nodos_explorados=explorados_orden,
            tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
            max_frontera=max_frontera,
            mensaje="No existe camino hacia el nodo meta.",
            pasos=pasos
        )

    # -------------------------------------------------------------------------
    # 6. BÚSQUEDA LOCAL: HILL CLIMBING (ESCALADA DE COLINAS)
    # -------------------------------------------------------------------------
    @staticmethod
    def hill_climbing(grafo: GrafoListas, origen_id: str, destino_id: str) -> ResultadoBusqueda:
        """
        Búsqueda Local: Hill Climbing (Escalada de Colinas / Descenso de Gradiente Heurístico).
        
        - Tipo: Búsqueda Local Orientada a Meta (Greedy Local Search).
        - Estrategia: En cada paso, desde el estado actual se examinan todos sus
          vecinos adyacentes en la lista enlazada y se selecciona aquel con el menor
          valor de heurística h(n) (más cercano a la meta).
        - Comportamiento Pedagógico:
          * Si el mejor vecino tiene h(vecino) < h(actual), se avanza a él.
          * Si ningún vecino mejora la heurística (h(vecino) >= h(actual)), el algoritmo
            se detiene inmediatamente por MÍNIMO LOCAL o MESETA.
          * Esto permite a los estudiantes comprender en la práctica las limitaciones
            intrínsecas de los métodos locales sin memoria global ni backtracking.
        """
        tiempo_inicio = time.perf_counter()
        grafo.actualizar_heuristicas(destino_id)
        origen_nodo = grafo.buscar_nodo(origen_id)
        destino_nodo = grafo.buscar_nodo(destino_id)

        if origen_nodo is None or destino_nodo is None:
            return ResultadoBusqueda(
                exito=False, algoritmo="Hill Climbing", origen=origen_id, destino=destino_id,
                mensaje="Nodo origen o destino inexistente en el grafo."
            )

        actual_nodo = origen_nodo
        actual_id = origen_id
        camino = [actual_id]
        costo_total = 0.0
        explorados_orden = [actual_id]
        pasos: List[Dict[str, Any]] = []
        paso_num = 1

        h_actual = grafo.calcular_distancia_euclidiana(actual_nodo, destino_nodo)

        pasos.append({
            "paso": paso_num,
            "nodo_actual": actual_id,
            "accion": f"Inicio de escalada en '{actual_id}' (h={h_actual:.1f})",
            "frontera": [actual_id],
            "visitados": list(camino),
            "g": 0.0,
            "h": round(h_actual, 1),
            "f": round(h_actual, 1),
            "camino_actual": list(camino)
        })

        exito = False
        mensaje_resultado = ""

        # Bucle de escalada local
        while True:
            if actual_id == destino_id:
                exito = True
                mensaje_resultado = f"¡Éxito! Meta alcanzada por descenso de gradiente directo (costo={costo_total:.1f} m)."
                break

            # Examinar todos los vecinos mediante la lista enlazada de adyacentes
            mejor_vecino_nodo: Optional[NodoEstado] = None
            menor_h_vecino: float = float("inf")
            peso_mejor_vecino: float = 0.0

            curr_ady = actual_nodo.lista_adyacentes
            candidatos_log = []

            while curr_ady is not None:
                vecino_nodo = curr_ady.nodo_referencia
                vec_id = vecino_nodo.informacion
                # Evitar ciclos inmediatos en la trayectoria actual
                if vec_id not in camino:
                    h_vecino = curr_ady.valor_heuristico
                    candidatos_log.append(f"{vec_id}(h={h_vecino:.1f})")
                    if h_vecino < menor_h_vecino:
                        menor_h_vecino = h_vecino
                        mejor_vecino_nodo = vecino_nodo
                        peso_mejor_vecino = curr_ady.peso
                curr_ady = curr_ady.sig_adyacente

            paso_num += 1

            # Condición de paro por Mínimo Local o Meseta:
            # Si no hay vecinos no visitados o ninguno ofrece una heurística menor que el estado actual
            if mejor_vecino_nodo is None or menor_h_vecino >= h_actual:
                exito = False
                if mejor_vecino_nodo is None:
                    mensaje_resultado = (
                        f"Estancamiento: El nodo '{actual_id}' no tiene más vecinos no visitados disponibles."
                    )
                else:
                    mensaje_resultado = (
                        f"Atrapado en MÍNIMO LOCAL en '{actual_id}' (h={h_actual:.1f}). "
                        f"El mejor vecino disponible '{mejor_vecino_nodo.informacion}' tiene h={menor_h_vecino:.1f} "
                        f"(no mejora la heurística actual). La escalada simple se detiene."
                    )
                pasos.append({
                    "paso": paso_num,
                    "nodo_actual": actual_id,
                    "accion": f"Detenido en Mínimo Local en '{actual_id}'",
                    "frontera": [],
                    "visitados": list(camino),
                    "g": round(costo_total, 1),
                    "h": round(h_actual, 1),
                    "f": round(h_actual, 1),
                    "camino_actual": list(camino)
                })
                break

            # Avanzar al mejor vecino
            actual_nodo = mejor_vecino_nodo
            actual_id = actual_nodo.informacion
            h_actual = menor_h_vecino
            costo_total += peso_mejor_vecino
            camino.append(actual_id)
            explorados_orden.append(actual_id)

            pasos.append({
                "paso": paso_num,
                "nodo_actual": actual_id,
                "accion": f"Avanza al mejor vecino '{actual_id}' con menor h={h_actual:.1f} (evaluó: {', '.join(candidatos_log)})",
                "frontera": [actual_id],
                "visitados": list(camino),
                "g": round(costo_total, 1),
                "h": round(h_actual, 1),
                "f": round(h_actual, 1),
                "camino_actual": list(camino)
            })

        tiempo_fin = time.perf_counter()
        aristas = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]

        return ResultadoBusqueda(
            exito=exito,
            algoritmo="Hill Climbing (Escalada de Colinas)",
            origen=origen_id,
            destino=destino_id,
            camino=camino,
            costo_total=round(costo_total, 1),
            nodos_explorados=explorados_orden,
            aristas_camino=aristas,
            tiempo_ms=round((tiempo_fin - tiempo_inicio) * 1000, 3),
            max_frontera=1,
            mensaje=mensaje_resultado,
            pasos=pasos
        )
