# -*- coding: utf-8 -*-
"""
===============================================================================
INSTITUTO TECNOLÓGICO DE CIUDAD GUZMÁN (ITCG) - TECNOLÓGICO NACIONAL DE MÉXICO
Materia: Inteligencia Artificial (Unidades 1 y 3)
Módulo: Implementación del Grafo mediante Listas Enlazadas (GrafoListas)
===============================================================================

Esta clase encapsula la estructura de datos del grafo, garantizando:
1. Almacenamiento de vértices mediante la Lista Principal de Estados (cabeza -> sig_nodo).
2. Almacenamiento de aristas mediante Listas Enlazadas de Adyacencia (lista_adyacentes -> sig_adyacente).
3. Cálculo dinámico de distancias euclidianas y pesos métricos.
4. Actualización en tiempo de ejecución de la heurística h(n) hacia el nodo meta
   seleccionado por el usuario, satisfaciendo la condición de admisibilidad
   y consistencia para el algoritmo A*.
===============================================================================
"""

import math
from typing import Optional, List, Tuple, Dict
from nodo import NodoEstado, NodoAdyacente


class GrafoListas:
    """
    Representación explícita del grafo del campus ITCG utilizando Listas Enlazadas.
    
    No utiliza diccionarios ni librerías de terceros (como networkx) para el grafo,
    asegurando el cumplimiento estricto del requerimiento académico de estructuras
    de datos enlazadas.
    """

    def __init__(self):
        # Puntero al primer nodo de la lista enlazada principal de estados
        self.cabeza: Optional[NodoEstado] = None
        self._total_nodos: int = 0
        self._total_aristas: int = 0
        # Referencia al último nodo meta utilizado para actualizar heurísticas
        self.nodo_meta_actual: Optional[NodoEstado] = None

    @property
    def total_nodos(self) -> int:
        return self._total_nodos

    @property
    def total_aristas(self) -> int:
        return self._total_aristas

    def insertar_nodo(
        self,
        informacion: str,
        x: float = 0.0,
        y: float = 0.0,
        nombre_completo: str = "",
        categoria: str = "General",
        descripcion: str = ""
    ) -> NodoEstado:
        """
        Inserta un nuevo NodoEstado al final de la lista enlazada principal.
        Si el identificador ya existe, retorna el nodo existente sin duplicarlo.
        """
        nodo_existente = self.buscar_nodo(informacion)
        if nodo_existente is not None:
            return nodo_existente

        nuevo_nodo = NodoEstado(
            informacion=informacion,
            x=x,
            y=y,
            nombre_completo=nombre_completo,
            categoria=categoria,
            descripcion=descripcion
        )

        if self.cabeza is None:
            self.cabeza = nuevo_nodo
        else:
            # Recorrer la lista enlazada principal hasta el último elemento
            actual = self.cabeza
            while actual.sig_nodo is not None:
                actual = actual.sig_nodo
            actual.sig_nodo = nuevo_nodo

        self._total_nodos += 1
        return nuevo_nodo

    def buscar_nodo(self, informacion: str) -> Optional[NodoEstado]:
        """
        Busca un nodo por su identificador ('A', 'L1', 'Z', etc.) recorriendo
        linealmente la lista enlazada principal a través del puntero sig_nodo.
        """
        actual = self.cabeza
        ident_buscado = str(informacion).strip().upper()
        while actual is not None:
            if actual.informacion.upper() == ident_buscado:
                return actual
            actual = actual.sig_nodo
        return None

    def calcular_distancia_euclidiana(self, nodo_a: NodoEstado, nodo_b: NodoEstado) -> float:
        """
        Calcula la distancia euclidiana en línea recta entre dos nodos:
        d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
        
        En el contexto de IA:
        - Representa una cota inferior admisible para la distancia real en el campus.
        - Garantiza que la heurística h(n) <= h*(n) (Admisible).
        - Cumple la desigualdad triangular h(n) <= c(n, p) + h(p) (Consistente/Monótona).
        """
        dx = nodo_a.x - nodo_b.x
        dy = nodo_a.y - nodo_b.y
        return round(math.hypot(dx, dy), 1)

    def insertar_arista(
        self,
        origen_info: str,
        destino_info: str,
        peso: Optional[float] = None,
        bidireccional: bool = True
    ) -> bool:
        """
        Inserta una arista (conexión peatonal) entre dos nodos del campus.
        
        Si el parámetro 'peso' no se proporciona, se calcula automáticamente
        la distancia euclidiana métrica entre las coordenadas de ambos edificios.
        """
        nodo_origen = self.buscar_nodo(origen_info)
        nodo_destino = self.buscar_nodo(destino_info)

        if nodo_origen is None or nodo_destino is None:
            print(f"[ERROR] No se pudo crear arista: '{origen_info}' o '{destino_info}' no encontrado.")
            return False

        # Si no se especifica el costo, calcular la distancia euclidiana
        if peso is None:
            peso = self.calcular_distancia_euclidiana(nodo_origen, nodo_destino)

        # Insertar en la lista de adyacencia de nodo_origen
        nodo_origen.agregar_adyacente(nodo_destino, peso=peso)
        self._total_aristas += 1

        # Si el camino peatonal es transitable en ambos sentidos (común en andadores)
        if bidireccional and nodo_origen != nodo_destino:
            nodo_destino.agregar_adyacente(nodo_origen, peso=peso)

        return True

    def actualizar_heuristicas(self, nodo_meta_info: str) -> bool:
        """
        Actualiza el valor_heuristico h(n) en cada NodoAdyacente del grafo
        tomando como destino el nodo meta indicado.
        
        Recorre la lista enlazada principal y cada una de las sub-listas
        enlazadas de adyacencia:
        h(n) = distancia_euclidiana(n, meta)
        """
        nodo_meta = self.buscar_nodo(nodo_meta_info)
        if nodo_meta is None:
            print(f"[ERROR] Nodo meta '{nodo_meta_info}' no encontrado en el grafo.")
            return False

        self.nodo_meta_actual = nodo_meta

        # Recorrer la lista enlazada principal de estados
        actual_estado = self.cabeza
        while actual_estado is not None:
            # Recorrer la lista enlazada de adyacentes de este estado
            actual_ady = actual_estado.lista_adyacentes
            while actual_ady is not None:
                # El valor heurístico del nodo de referencia adyacente hacia la meta
                vecino = actual_ady.nodo_referencia
                h_val = self.calcular_distancia_euclidiana(vecino, nodo_meta)
                actual_ady.valor_heuristico = h_val
                actual_ady = actual_ady.sig_adyacente

            actual_estado = actual_estado.sig_nodo

        return True

    def obtener_todos_los_nodos(self) -> List[NodoEstado]:
        """
        Recorre la lista enlazada principal y retorna todos los NodoEstado
        en una lista de Python para facilidad de renderizado en la interfaz.
        """
        nodos = []
        actual = self.cabeza
        while actual is not None:
            nodos.append(actual)
            actual = actual.sig_nodo
        return nodos

    def obtener_todas_las_aristas(self) -> List[Tuple[str, str, float]]:
        """
        Recorre el grafo completo y retorna una lista de tuplas únicas
        representando las aristas: (origen_id, destino_id, peso).
        Evita duplicados en aristas bidireccionales.
        """
        aristas = []
        aristas_vistas = set()

        actual = self.cabeza
        while actual is not None:
            ady = actual.lista_adyacentes
            while ady is not None:
                u = actual.informacion
                v = ady.nodo_referencia.informacion
                clave_arista = tuple(sorted([u, v]))
                if clave_arista not in aristas_vistas:
                    aristas_vistas.add(clave_arista)
                    aristas.append((u, v, ady.peso))
                ady = ady.sig_adyacente
            actual = actual.sig_nodo

        return aristas

    def imprimir_resumen(self):
        """
        Imprime en consola la estructura del grafo para verificación docente.
        """
        print(f"\n{'='*70}")
        print(f"ESTRUCTURA DEL GRAFO - CAMPUS ITCG (Total Estados: {self._total_nodos})")
        print(f"{'='*70}")
        actual = self.cabeza
        while actual is not None:
            adyacencias_str = []
            ady = actual.lista_adyacentes
            while ady is not None:
                adyacencias_str.append(
                    f"{ady.nodo_referencia.informacion} (peso={ady.peso:.0f}, h={ady.valor_heuristico:.0f})"
                )
                ady = ady.sig_adyacente
            con_str = " -> ".join(adyacencias_str) if adyacencias_str else "Sin adyacencias"
            print(f"[{actual.informacion:^4}] {actual.nombre_completo[:35]:<35} | Conecta con: {con_str}")
            actual = actual.sig_nodo
        print(f"{'='*70}\n")
