# -*- coding: utf-8 -*-
"""
===============================================================================
INSTITUTO TECNOLÓGICO DE CIUDAD GUZMÁN (ITCG) - TECNOLÓGICO NACIONAL DE MÉXICO
Materia: Inteligencia Artificial (Unidades 1 y 3)
Módulo: Definición de Estructura de Datos en Listas Enlazadas
===============================================================================

Este módulo define las dos clases fundamentales requeridas para la representación
del grafo del campus ITCG mediante Listas Enlazadas explícitas, prescindiendo
de librerías externas para garantizar el rigor pedagógico en estructuras de datos:

1. NodoEstado:
   Representa un vértice (edificio o acceso) en la Lista Principal de Estados.
   Contiene la información del estado, el puntero al siguiente estado (sig_nodo),
   y el puntero al inicio de su lista enlazada de adyacencias (lista_adyacentes).

2. NodoAdyacente:
   Representa una arista o conexión peatonal en la Lista de Adyacencia.
   Contiene el peso (distancia métrica en metros), el valor heurístico h(n)
   hacia la meta actual, la referencia al NodoEstado de destino (nodo_referencia),
   y el puntero al siguiente vecino adyacente (sig_adyacente).
===============================================================================
"""

from typing import Optional, List, Tuple


class NodoAdyacente:
    """
    Nodo de la Lista de Adyacencia (Arista del Grafo).
    
    Representa una conexión directa y transitable desde un edificio hacia otro
    dentro del campus del ITCG.
    
    Atributos exigidos por la especificación:
        peso (float):
            Costo de la arista (por defecto = 1.0). Representa la distancia
            física/métrica real en metros entre ambos edificios.
        valor_heuristico (float):
            Distancia o costo estimado h(n) hacia el nodo meta (por defecto = 0.0).
            Se recalcula dinámicamente cuando el usuario selecciona un nodo destino.
        nodo_referencia (NodoEstado):
            Puntero / referencia al objeto NodoEstado correspondiente en la lista
            principal de estados.
        sig_adyacente (Optional[NodoAdyacente]):
            Puntero / referencia al siguiente nodo adyacente en la lista enlazada
            de adyacencias del estado origen.
    """

    def __init__(
        self,
        nodo_referencia: "NodoEstado",
        peso: float = 1.0,
        valor_heuristico: float = 0.0
    ):
        self.peso: float = float(peso)
        self.valor_heuristico: float = float(valor_heuristico)
        self.nodo_referencia: "NodoEstado" = nodo_referencia
        self.sig_adyacente: Optional["NodoAdyacente"] = None

    def __repr__(self) -> str:
        ref_id = self.nodo_referencia.informacion if self.nodo_referencia else "None"
        return (
            f"NodoAdyacente(destino='{ref_id}', peso={self.peso:.1f}, "
            f"h={self.valor_heuristico:.1f})"
        )


class NodoEstado:
    """
    Nodo de la Lista de Información (Estados / Vértices del Grafo).
    
    Representa un edificio, laboratorio, cafetería o acceso en la Lista Principal
    de Estados del campus del Instituto Tecnológico de Ciudad Guzmán.
    
    Atributos exigidos por la especificación:
        informacion (str):
            Identificador único del edificio o nodo (ej. "A", "L1", "Z", "ACCESO 1").
        sig_nodo (Optional[NodoEstado]):
            Puntero / referencia al siguiente nodo en la lista principal de estados.
        lista_adyacentes (Optional[NodoAdyacente]):
            Puntero / referencia al primer nodo de su lista enlazada de adyacencias.
            
    Atributos complementarios para renderizado gráfico y cálculo heurístico:
        x (float): Coordenada espacial X en el plano del campus.
        y (float): Coordenada espacial Y en el plano del campus.
        nombre_completo (str): Nombre oficial y legible del edificio/área.
        categoria (str): Categoría temática (Aulas, Laboratorios, Administrativo, etc.).
        descripcion (str): Reseña descriptiva de las instalaciones y departamentos.
    """

    def __init__(
        self,
        informacion: str,
        x: float = 0.0,
        y: float = 0.0,
        nombre_completo: str = "",
        categoria: str = "General",
        descripcion: str = ""
    ):
        self.informacion: str = str(informacion)
        self.sig_nodo: Optional["NodoEstado"] = None
        self.lista_adyacentes: Optional[NodoAdyacente] = None

        # Atributos espaciales y descriptivos
        self.x: float = float(x)
        self.y: float = float(y)
        self.nombre_completo: str = nombre_completo or f"Edificio {informacion}"
        self.categoria: str = categoria
        self.descripcion: str = descripcion

    def agregar_adyacente(
        self,
        nodo_destino: "NodoEstado",
        peso: float = 1.0,
        valor_heuristico: float = 0.0
    ) -> NodoAdyacente:
        """
        Inserta un nuevo NodoAdyacente al final de la lista enlazada de adyacencias.
        Evita aristas duplicadas si ya existe conexión hacia el mismo destino.
        """
        nuevo_adyacente = NodoAdyacente(
            nodo_referencia=nodo_destino,
            peso=peso,
            valor_heuristico=valor_heuristico
        )

        if self.lista_adyacentes is None:
            self.lista_adyacentes = nuevo_adyacente
        else:
            actual = self.lista_adyacentes
            while actual.sig_adyacente is not None:
                if actual.nodo_referencia == nodo_destino:
                    # Si ya existe, actualizamos su peso
                    actual.peso = peso
                    return actual
                actual = actual.sig_adyacente

            if actual.nodo_referencia == nodo_destino:
                actual.peso = peso
                return actual

            actual.sig_adyacente = nuevo_adyacente

        return nuevo_adyacente

    def obtener_lista_adyacentes(self) -> List[Tuple["NodoEstado", float, float]]:
        """
        Recorre la lista enlazada de adyacencias usando el puntero sig_adyacente
        y devuelve una lista de tuplas: (nodo_referencia, peso, valor_heuristico).
        """
        resultado = []
        actual = self.lista_adyacentes
        while actual is not None:
            resultado.append((
                actual.nodo_referencia,
                actual.peso,
                actual.valor_heuristico
            ))
            actual = actual.sig_adyacente
        return resultado

    def __repr__(self) -> str:
        return f"NodoEstado(id='{self.informacion}', nombre='{self.nombre_completo}')"
