# Instituto Tecnológico de Ciudad Guzmán (ITCG)
## Tecnológico Nacional de México
### Asignatura: Inteligencia Artificial (Unidades 1 y 3)
### Proyecto: Simulador Interactivo de Métodos de Búsqueda sobre el Campus ITCG

---

## 🏛 Descripción General
Este software es una herramienta interactiva y pedagógica desarrollada en **Python 3** diseñada para los estudiantes y docentes de la materia de **Inteligencia Artificial** del ITCG. Permite representar, visualizar, explorar e interactuar con el grafo completo del mapa de localización del campus (edificios A-Z, laboratorios, cafetería L1, accesos 1 al 4, andadores y plazas).

El sistema permite seleccionar cualquier nodo origen y destino, ejecutando y comparando paso a paso **6 algoritmos de búsqueda** fundamentales:
1. **BFS (Breadth-First Search / Búsqueda Primero en Anchura)** - No informada.
2. **DFS (Depth-First Search / Búsqueda Primero en Profundidad)** - No informada.
3. **Greedy Best-First Search (Primero el Mejor / Voraz)** - Informada ($f(n) = h(n)$).
4. **Algoritmo de Dijkstra / Búsqueda de Costo Uniforme** - Informada por costo acumulado ($f(n) = g(n)$).
5. **Búsqueda Heurística A\*** - Informada ($f(n) = g(n) + h(n)$).
6. **Hill Climbing (Escalada de Colinas)** - Búsqueda local orientada a meta.

---

## 🧬 Estructura de Datos Obligatoria: Listas Enlazadas
Cumpliendo rigurosamente los lineamientos de la materia, el grafo no utiliza librerías externas (como `networkx`), sino que está implementado explícitamente mediante **Listas Enlazadas**:

### 1. Lista de Información (Estados / Vértices)
Cada elemento es una instancia de `NodoEstado`:
* `informacion`: Identificador del edificio o nodo (`"A"`, `"L1"`, `"Z"`, `"ACCESO 1"`, etc.).
* `sig_nodo`: Puntero/referencia al siguiente `NodoEstado` en la lista principal de estados.
* `lista_adyacentes`: Puntero/referencia al primer `NodoAdyacente` de su lista de adyacencias.
* `x`, `y`: Coordenadas cartesianas en el plano del campus (para renderizado visual y cálculo de heurística euclidiana).
* `nombre_completo`, `categoria`, `descripcion`: Metadatos académicos e institucionales oficiales.

### 2. Lista de Adyacencia (Aristas / Andadores)
Cada elemento es una instancia de `NodoAdyacente`:
* `peso`: Costo métrico real de la arista en metros (distancia física entre edificios).
* `valor_heuristico`: Estimación $h(n)$ calculada dinámicamente como la distancia euclidiana en línea recta hacia el nodo meta actual:
  $$h(n) = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$
  *Al ser distancia euclidiana 2D en plano, $h(n)$ es estrictamente **admisible** ($h(n) \le h^*(n)$) y **consistente/monótona** ($h(n) \le c(n, p) + h(p)$), garantizando que $A^*$ encuentre la solución de costo mínimo óptimo sin reabrir nodos cerrados.*
* `nodo_referencia`: Referencia/apuntador al `NodoEstado` correspondiente en la lista de estados.
* `sig_adyacente`: Puntero/referencia al siguiente `NodoAdyacente` de la lista de adyacencia.

---

## 📁 Arquitectura del Código
El proyecto sigue una estructura limpia, modular y desacoplada:

```text
ActividadMetodosDeBusqueda/
│
├── nodo.py            # Clases NodoEstado y NodoAdyacente (especificación enlazada)
├── grafo.py           # Clase GrafoListas (gestión de estados, aristas y heurísticas)
├── campus_data.py     # Catálogo de edificios A-Z, coordenadas y conexiones del ITCG
├── algoritmos.py      # Implementación de BFS, DFS, Greedy, Dijkstra, A*, Hill Climbing
├── interfaz.py        # Interfaz gráfica interactiva con Tkinter + Canvas + Pillow
├── main.py            # Punto de entrada de la aplicación con soporte High-DPI
├── mapa_itcg.jpg      # Plano oficial de localización del campus ITCG
└── README.md          # Documentación académica del proyecto
```

---

## 🚀 Requisitos e Instalación

### Requisitos:
* Python 3.8 o superior.
* Librería `Pillow` (para manejo y renderizado fluido del mapa sobre el Canvas):
  ```bash
  pip install pillow
  ```
  *(Nota: Tkinter ya viene incluido de forma estándar en las distribuciones de Python para Windows).*

### Ejecución:
Para iniciar el simulador, ejecuta en tu terminal o consola:
```bash
python main.py
```

---

## 🎮 Controles y Guía de Uso de la Interfaz

1. **Lienzo del Campus (Canvas Central):**
   * **Clic Izquierdo sobre un edificio:** Selecciona el nodo como **Origen** (o alterna a Destino).
   * **Clic Derecho sobre un edificio:** Despliega un menú contextual para definir rápidamente **Origen**, **Destino** o consultar su **Ficha Técnica**.
   * **Arrastrar con el ratón:** Desplaza (paneo) el campus libremente.
   * **Rueda del ratón:** Acerca o aleja (Zoom dinámico centrado en el cursor).
   * **Casilla "🗺 Mapa Oficial":** Alterna entre la imagen real del mapa del ITCG y una vista esquemática vectorial limpia.
   * **Casilla "📏 Pesos (m)":** Muestra u oculta las distancias métricas de cada andador.
   * **Casilla "🎯 Heurística h(n)":** Muestra sobre cada edificio la distancia estimada en línea recta a la meta.

2. **Panel de Búsqueda:**
   * Elige el **Origen** y **Destino** desde las listas desplegables (o haciendo clic directo en el mapa).
   * Selecciona el **Algoritmo de Búsqueda** deseado (1 al 6).
   * Presiona **"▶ Ejecutar Búsqueda"**.

3. **Panel de Animación Didáctica:**
   * **"▶ Animar / ⏸ Pausar":** Reproduce automáticamente el orden de exploración nodo a nodo.
   * **"⏮ Anterior" / "⏭ Siguiente":** Permite al docente o estudiante avanzar paso por paso para explicar cómo evoluciona la frontera y los nodos visitados.
   * **Control de Velocidad:** Ajusta el tiempo de retraso entre pasos.

4. **Pestañas de Inspección Técnica:**
   * **Traza de Pasos:** Tabla con el registro numérico de cada paso: nodo expandido, acción, $g(n)$, $h(n)$ y $f(n)$.
   * **Listas Enlazadas:** Inspección viva en memoria de los punteros `sig_nodo`, `lista_adyacentes` y `sig_adyacente` de cada edificio.
   * **Ficha Edificio:** Información detallada de las carreras, laboratorios y andadores que componen el edificio seleccionado.

---

## 📊 Comparativa Pedagógica de Algoritmos (Ejemplo: Origen A -> Destino Z)

| Algoritmo | Tipo | Función $f(n)$ | Garantía de Costo Óptimo | Nodos Explorados | Saltos | Costo Total |
|---|---|---|:---:|:---:|:---:|:---:|
| **BFS** | No informada | $f(n) = \text{profundidad}$ | ❌ (Solo óptimo en saltos) | 31 / 34 | 9 | 854.3 m |
| **DFS** | No informada | Pila LIFO | ❌ (Rutas largas) | 31 / 34 | 29 | 2301.8 m |
| **Greedy Best-First** | Informada | $f(n) = h(n)$ | ❌ (Voraz) | 10 / 34 | 9 | 854.3 m |
| **Dijkstra (UCS)** | Informada por costo | $f(n) = g(n)$ | ✔ Sí | 32 / 34 | 11 | **803.0 m** |
| **A\*** | Informada | $f(n) = g(n) + h(n)$ | ✔ Sí | **19 / 34** | 11 | **803.0 m** |
| **Hill Climbing** | Búsqueda Local | Descenso $h(n)$ | ❌ (Sensible a mínimos locales) | 10 / 34 | 9 | 854.3 m |

> **Observación Docente Clave:**  
> Ambos algoritmos **Dijkstra** y **A\*** hallan el camino globalmente óptimo ($803.0\text{ m}$), pero **A\*** expande únicamente 19 nodos frente a los 32 de Dijkstra (un **40% menos de exploraciones**), demostrando la eficiencia de las heurísticas admisibles. Por su parte, **Hill Climbing** ilustra cómo la búsqueda local puede atascarse en mínimos locales (por ejemplo, al intentar ir de `ACCESO 1` a `ACCESO 4`).
