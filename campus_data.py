# -*- coding: utf-8 -*-
"""
===============================================================================
INSTITUTO TECNOLÓGICO DE CIUDAD GUZMÁN (ITCG) - TECNOLÓGICO NACIONAL DE MÉXICO
Materia: Inteligencia Artificial (Unidades 1 y 3)
Módulo: Definición del Plano Oficial del Campus ITCG y Red Peatonal
===============================================================================

Este módulo contiene los datos topológicos y espaciales del mapa de localización
oficial del Instituto Tecnológico de Ciudad Guzmán:
- Coordenadas (X, Y) calibradas respecto a la planimetría del campus.
- Catálogo de edificios, laboratorios, aulas, áreas directivas y accesos peatonales.
- Conexiones peatonales reales entre andadores, plazas y edificios.
- Función constructora 'cargar_grafo_itcg' que instancia y puebla el GrafoListas.
===============================================================================
"""

from typing import Dict, List, Tuple
from grafo import GrafoListas

# Catálogo completo de nodos del ITCG: identificador -> metadatos
EDIFICIOS_CAMPUS: Dict[str, dict] = {
    # Sector Este (Ingreso Principal y Ciencias Básicas / Económico-Administrativas)
    "A": {
        "nombre": "Laboratorio de Ing. Industrial",
        "categoria": "Laboratorios",
        "x": 875, "y": 305,
        "descripcion": "Laboratorios de manufactura, ergonomía y métodos para Ingeniería Industrial."
    },
    "B": {
        "nombre": "Laboratorios de Ing. Eléctrica e Idiomas",
        "categoria": "Laboratorios",
        "x": 800, "y": 268,
        "descripcion": "Laboratorios de máquinas eléctricas y Centro de Autoacceso de Idiomas."
    },
    "C": {
        "nombre": "Laboratorios de Matemáticas y Contaduría",
        "categoria": "Laboratorios",
        "x": 735, "y": 325,
        "descripcion": "Aulas y talleres para cómputo matemático, estadística y finanzas."
    },
    "D": {
        "nombre": "Módulo de Aulas D",
        "categoria": "Aulas",
        "x": 735, "y": 254,
        "descripcion": "Salones para docencia de diversas carreras y materias de tronco común."
    },
    "E": {
        "nombre": "Módulo de Aulas E",
        "categoria": "Aulas",
        "x": 692, "y": 238,
        "descripcion": "Salones para docencia de ciencias económico-administrativas y gestión."
    },
    "F": {
        "nombre": "Cubículos de Contaduría y Cs. Económico-Admon.",
        "categoria": "Cubículos / Administrativo",
        "x": 665, "y": 308,
        "descripcion": "Jefatura del Depto. de Ciencias Económico-Administrativas y cubículos de docentes."
    },
    "G": {
        "nombre": "Cubículos de Ing. en Gestión Empresarial",
        "categoria": "Cubículos / Administrativo",
        "x": 648, "y": 248,
        "descripcion": "Cubículos de profesores y asesores de proyectos de Gestión Empresarial."
    },
    "H": {
        "nombre": "Sala Audiovisual Miguel Velasco Oropeza",
        "categoria": "Eventos / Auditorios",
        "x": 600, "y": 218,
        "descripcion": "Auditorio para conferencias académicas, simposios y presentaciones de tesis."
    },
    "I": {
        "nombre": "Aulas y Unidad Administrativa I",
        "categoria": "Aulas / Administrativo",
        "x": 602, "y": 312,
        "descripcion": "Planta Baja: Depto. Desarrollo Académico y Servicio Médico. Planta Alta: Ciencias de la Tierra."
    },

    # Sector Centro (Plaza Cívica, Cafetería, Ciencias Básicas y Sistemas)
    "J": {
        "nombre": "Módulo de Aulas J",
        "categoria": "Aulas",
        "x": 558, "y": 325,
        "descripcion": "Aulas de clase para las carreras de Ingeniería en Sistemas y Gestión."
    },
    "K": {
        "nombre": "Módulo de Aulas K",
        "categoria": "Aulas",
        "x": 552, "y": 187,
        "descripcion": "Aulas departamentales de ciencias básicas y laboratorios."
    },
    "L1": {
        "nombre": "Cafetería Central (L1)",
        "categoria": "Servicios",
        "x": 528, "y": 252,
        "descripcion": "Cafetería estudiantil, comedor de profesores y terraza de convivencia central."
    },
    "M": {
        "nombre": "Módulo de Aulas M",
        "categoria": "Aulas",
        "x": 510, "y": 190,
        "descripcion": "Aulas de formación multidisciplinaria y ciencias exactas."
    },
    "N": {
        "nombre": "Módulo de Aulas y Lab. de Química",
        "categoria": "Laboratorios",
        "x": 460, "y": 175,
        "descripcion": "Laboratorios de Química General, Ambiental y Bioquímica con módulos de aulas."
    },
    "Ñ": {
        "nombre": "Cubículos de Maestros - Cs. Básicas",
        "categoria": "Cubículos / Administrativo",
        "x": 462, "y": 290,
        "descripcion": "Jefatura del Depto. de Ciencias Básicas y asesoría docente de matemáticas/física."
    },
    "O": {
        "nombre": "Módulo de Aulas O",
        "categoria": "Aulas",
        "x": 448, "y": 235,
        "descripcion": "Aulas centrales para ingeniería e informática."
    },
    "P": {
        "nombre": "Jefatura de Sistemas y Computación",
        "categoria": "Sistemas y Computación",
        "x": 465, "y": 345,
        "descripcion": "Cubículos docentes, Sala de Juntas y Jefatura del Depto. de Sistemas y Computación."
    },

    # Sector Poniente (Electrónica, Mecánica, Cómputo, Auditorio y Dirección)
    "Q": {
        "nombre": "Lab. de Electrónica en Instrumentación",
        "categoria": "Laboratorios",
        "x": 410, "y": 257,
        "descripcion": "Laboratorio para microcontroladores, instrumentación biomédica y automatización."
    },
    "R": {
        "nombre": "Lab. y Jefatura Metal-Mecánica",
        "categoria": "Laboratorios",
        "x": 345, "y": 280,
        "descripcion": "Talleres de máquinas herramientas, tornos CNC, soldadura y Depto. Metal-Mecánica."
    },
    "S": {
        "nombre": "Lab. de Electrónica y Jefatura Eléctrica",
        "categoria": "Laboratorios",
        "x": 315, "y": 345,
        "descripcion": "Laboratorio de telecomunicaciones, robótica y cubículos de Electrónica/Eléctrica."
    },
    "T": {
        "nombre": "Planta Purificadora de Agua",
        "categoria": "Servicios",
        "x": 303, "y": 280,
        "descripcion": "Planta purificadora sustentable que abastece a la comunidad del campus."
    },
    "U": {
        "nombre": "Delegación Sindical D-V-49 / Sección 61",
        "categoria": "Servicios / Administrativo",
        "x": 303, "y": 234,
        "descripcion": "Oficinas sindicales de los trabajadores del ITCG."
    },
    "T1": {
        "nombre": "Unidad Académica Dptal. de Ing. Industrial",
        "categoria": "Aulas / Administrativo",
        "x": 210, "y": 217,
        "descripcion": "Edificio académico departamental con aulas magnas y laboratorios de Industrial."
    },
    "T2": {
        "nombre": "Laboratorio Industrias 4.0",
        "categoria": "Laboratorios",
        "x": 295, "y": 187,
        "descripcion": "Centro de alta tecnología para IoT, gemelos digitales y manufactura 4.0."
    },
    "V": {
        "nombre": "Laboratorio y Centro de Cómputo",
        "categoria": "Sistemas y Computación",
        "x": 245, "y": 328,
        "descripcion": "Salas de servidores, laboratorios de programación y redes de cómputo para el campus."
    },
    "W": {
        "nombre": "Gimnasio Auditorio y Extraescolares",
        "categoria": "Deportivo / Cultural",
        "x": 167, "y": 279,
        "descripcion": "Gimnasio techado, canchas polivalentes y Jefatura de Actividades Extraescolares."
    },
    "X": {
        "nombre": "Centro de Información (Biblioteca)",
        "categoria": "Biblioteca / Posgrado",
        "x": 105, "y": 335,
        "descripcion": "Biblioteca central, sala de titulación, salas de estudio y División de Estudios Profesionales."
    },
    "Y": {
        "nombre": "Talleres de Mantenimiento y Recursos Materiales",
        "categoria": "Servicios",
        "x": 140, "y": 250,
        "descripcion": "Jefatura de Depto. de Mantenimiento, equipo y almacén de recursos materiales."
    },
    "Z": {
        "nombre": "Unidad Académico-Administrativa (Dirección)",
        "categoria": "Dirección / Gobierno",
        "x": 118, "y": 182,
        "descripcion": "Dirección General, Subdirecciones (Planeación, Administrativa, Académica) y Servicios Escolares."
    },

    # Accesos Peatonales y Puntos de Ingreso al Campus
    "ACCESO 1": {
        "nombre": "Acceso 1 - Estudiantes (Principal Este)",
        "categoria": "Accesos",
        "x": 880, "y": 410,
        "descripcion": "Entrada principal peatonal y vehicular sobre Carretera El Grullo para la comunidad estudiantil."
    },
    "ACCESO 2": {
        "nombre": "Acceso 2 - Personal (Centro Este)",
        "categoria": "Accesos",
        "x": 620, "y": 410,
        "descripcion": "Ingreso controlado peatonal para personal docente y administrativo del campus."
    },
    "SOLO SALIDA": {
        "nombre": "Salida Vehicular / Peatonal Sur",
        "categoria": "Accesos",
        "x": 395, "y": 410,
        "descripcion": "Salida obligatoria vehicular hacia la Carretera Estatal El Grullo - Ciudad Guzmán."
    },
    "ACCESO 3": {
        "nombre": "Acceso 3 - Exclusivo Eventos",
        "categoria": "Accesos",
        "x": 205, "y": 410,
        "descripcion": "Ingreso especial hacia Centro de Cómputo (V) y Gimnasio Auditorio (W)."
    },
    "ACCESO 4": {
        "nombre": "Acceso 4 - Poniente (Biblioteca / Dirección)",
        "categoria": "Accesos",
        "x": 50, "y": 410,
        "descripcion": "Ingreso poniente directo a Biblioteca (X), Dirección (Z) y áreas deportivas."
    }
}

# Red de andadores peatonales y conexiones transitables entre edificios del campus
CONEXIONES_CAMPUS: List[Tuple[str, str]] = [
    # Accesos con edificios adyacentes
    ("ACCESO 1", "A"),
    ("ACCESO 1", "C"),
    ("ACCESO 2", "I"),
    ("ACCESO 2", "J"),
    ("SOLO SALIDA", "P"),
    ("SOLO SALIDA", "S"),
    ("ACCESO 3", "V"),
    ("ACCESO 3", "W"),
    ("ACCESO 4", "X"),

    # Conexiones Sector Este (A, B, C, D, E, F, G, H, I)
    ("A", "B"),
    ("A", "C"),
    ("B", "D"),
    ("B", "C"),
    ("C", "D"),
    ("C", "F"),
    ("D", "E"),
    ("E", "G"),
    ("E", "F"),
    ("F", "I"),
    ("F", "G"),
    ("G", "H"),
    ("H", "I"),
    ("H", "K"),
    ("H", "L1"),
    ("I", "J"),

    # Conexiones Sector Centro (J, K, L1, M, N, Ñ, O, P)
    ("J", "L1"),
    ("J", "P"),
    ("K", "M"),
    ("K", "L1"),
    ("L1", "M"),
    ("L1", "O"),
    ("L1", "Ñ"),
    ("M", "N"),
    ("M", "O"),
    ("N", "O"),
    ("N", "T2"),
    ("O", "Ñ"),
    ("O", "Q"),
    ("Ñ", "P"),
    ("Ñ", "Q"),
    ("P", "S"),

    # Conexiones Sector Poniente (Q, R, S, T, U, T1, T2, V, W, X, Y, Z)
    ("Q", "R"),
    ("Q", "U"),
    ("R", "S"),
    ("R", "T"),
    ("R", "U"),
    ("S", "V"),
    ("S", "T"),
    ("T", "U"),
    ("T", "V"),
    ("U", "T1"),
    ("U", "T2"),
    ("T2", "T1"),
    ("T1", "V"),
    ("T1", "W"),
    ("T1", "Z"),
    ("V", "W"),
    ("W", "X"),
    ("W", "Y"),
    ("X", "Y"),
    ("X", "Z"),
    ("Y", "Z"),
]


def cargar_grafo_itcg() -> GrafoListas:
    """
    Función de fábrica que inicializa el GrafoListas y puebla todos los
    nodos y aristas basándose en la cartografía oficial del ITCG.
    
    Retorna:
        GrafoListas: Instancia lista con todos los estados y adyacencias enlazadas.
    """
    grafo = GrafoListas()

    # 1. Insertar todos los edificios en la Lista Principal de Estados
    for ident, datos in EDIFICIOS_CAMPUS.items():
        grafo.insertar_nodo(
            informacion=ident,
            x=datos["x"],
            y=datos["y"],
            nombre_completo=datos["nombre"],
            categoria=datos["categoria"],
            descripcion=datos["descripcion"]
        )

    # 2. Insertar todas las conexiones peatonales en las Listas de Adyacencia
    for origen, destino in CONEXIONES_CAMPUS:
        # El peso se calcula automáticamente como distancia euclidiana métrica
        grafo.insertar_arista(origen, destino, peso=None, bidireccional=True)

    return grafo
