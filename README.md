# Tranvía Lab

Documentación de referencias y demostración práctica sobre **razonamiento, lógica, computación y agencia**, a partir del dilema del tranvía.

Este README consolida y ordena las fuentes relacionadas con los conceptos que explora el proyecto, como material complementario de la serie de Nicolás Ezequiel Melluso sobre inteligencia e inteligencia artificial.

Sigue la organización de [Intelligence-from-scratch](https://github.com/Nicolas-Melluso/Intelligence-from-scratch): referencias agrupadas por tema, con autor, título, año y acceso a la fuente. También incluye un laboratorio que podés ejecutar, modificar y conectar con un agente.

Como punto de partida de la serie: **[IA] Inteligencia Natural**.  
https://youtu.be/KQGPMeEr8XY

## Referencias científicas y filosóficas

Las fuentes dan contexto al experimento. El simulador no implementa todos los modelos que aparecen en ellas. Se incluyen artículos, un libro y un informe de investigación; el tipo de publicación se indica cuando corresponde.

### El dilema del tranvía: acciones, intenciones y consecuencias

1. Philippa Foot — *The Problem of Abortion and the Doctrine of the Double Effect* (1967).  
   Artículo que introduce un antecedente central del dilema y examina las diferencias entre intención, consecuencias previstas y deberes.  
   [Texto completo, copia académica en Pittsburgh](https://sites.pitt.edu/~mthompso/readings/foot.pdf).  
   [Reedición en *Virtues and Vices* (Oxford, 2002)](https://doi.org/10.1093/0199252866.003.0002).
2. Judith Jarvis Thomson — *The Trolley Problem* (1985).  
   Análisis de las variantes del problema y de lo que cambia cuando intervenimos para redistribuir el daño.  
   [Artículo en *The Yale Law Journal*](https://doi.org/10.2307/796133).  
   [PDF en el repositorio de Yale](https://openyls.law.yale.edu/bitstream/handle/20.500.13051/16338/56_94YaleLJ1395_1984_1985_.pdf).

### Cómo razonamos las personas

1. Jonathan St. B. T. Evans y Keith E. Stanovich — *Dual-Process Theories of Higher Cognition: Advancing the Debate* (2013).  
   Marco para discutir procesos más automáticos y procesos más deliberados, y su relación con razonamiento y memoria de trabajo.  
   https://doi.org/10.1177/1745691612460685  
   [Registro académico de la Universidad de Plymouth](https://researchportal.plymouth.ac.uk/en/publications/dual-process-theories-of-higher-cognition-advancing-the-debate/).

### De las palabras a las reglas: lógica y procedimientos

1. George Boole — *The Mathematical Analysis of Logic* (1847).  
   Libro fundacional sobre el tratamiento algebraico de la lógica y el razonamiento deductivo. Contexto histórico para pasar de enunciados a operaciones explícitas.  
   https://www.gutenberg.org/ebooks/36884
2. Alonzo Church — *A Note on the Entscheidungsproblem* (1936).  
   Resultado sobre los límites de un procedimiento general de decisión en lógica. Resolver las pocas alternativas de esta demo no equivale a resolver ese problema general.  
   [Artículo original, copia académica en MIT](https://people.csail.mit.edu/brooks/idocs/church_ent.pdf).

### Turing: computar, aprender y discutir si una máquina piensa

1. Alan M. Turing — *On Computable Numbers, with an Application to the Entscheidungsproblem* (1936–1937).  
   Fundamentos de computabilidad y de la máquina universal. El manuscrito fue recibido en 1936; la ficha editorial del volumen indica 1937.  
   https://doi.org/10.1112/plms/s2-42.1.230  
   [PDF en Stanford](https://theory.stanford.edu/~trevisan/cs172-07/turing36.pdf).
2. Alan M. Turing — *Intelligent Machinery* (1948).  
   Informe para el National Physical Laboratory sobre máquinas inteligentes, redes desorganizadas y organización mediante entrenamiento. Es contexto histórico: el motor de reglas de este proyecto no aprende.  
   [Texto del informe](https://intelligentmachinerycourse.com/wp-content/uploads/2018/08/turing-intelligent-machinery-1948.pdf).
3. Alan M. Turing — *Computing Machinery and Intelligence* (1950).  
   Artículo que examina la pregunta por el pensamiento de las máquinas y propone el juego de imitación. Permite volver a la distinción entre observar una respuesta y explicar el mecanismo que la produjo.  
   https://academic.oup.com/mind/article/LIX/236/433/986238

## Del concepto al experimento

Un tren sin frenos avanza hacia una bifurcación. En cada vía hay una cantidad de personas y una palanca permite elegir el recorrido. ¿Qué hace una persona? ¿Qué hace un programa con reglas explícitas? ¿Qué decide un agente conectado a un modelo de lenguaje?

El proyecto permite comparar esas tres situaciones sobre el mismo mundo:

- **Yo decido:** la persona controla la palanca.
- **Regla en Python:** el programa aplica uno de los criterios escritos en `decision.py`.
- **Agente MCP:** un LLM externo recibe el escenario, elige una acción y envía una justificación pública; el simulador ejecuta esa acción.

El tren y las vías se dibujan en Canvas. Las decisiones por reglas se calculan en Python y las acciones del agente se reciben mediante un servidor MCP local. No hay un criterio ético obligatorio para el agente.

## Ejecutar

Requiere **Python 3.10 o posterior** y un navegador moderno. La demo local y el servidor MCP no requieren paquetes externos ni claves. Usar un LLM externo requiere el cliente y la conexión que ese proveedor necesite.

**Windows: doble clic en `iniciar.bat`.** Busca Python instalado y, si no lo encuentra, el runtime local de Codex cuando está disponible. En otra computadora basta con instalar Python. La carpeta no depende de Codex.

Desde esta carpeta:

```sh
python app.py
```

En Windows también podés usar `py app.py`. Se abre el navegador en **http://127.0.0.1:8765**. Mantené la terminal abierta; Ctrl+C detiene el servidor.

Si el puerto está ocupado:

```sh
python app.py --port 8766
```

Para iniciar sin abrir automáticamente el navegador: `python app.py --no-browser`.

## Qué se puede hacer

- Cambiar entre 0 y 12 personas por vía y usar escenarios predefinidos.
- Decidir manualmente, con el botón, la palanca dibujada o la tecla **L**.
- Delegar la decisión a una de tres reglas explícitas calculadas por Python.
- Conectar un agente mediante MCP y ver su decisión y justificación en la escena.
- Pausar y continuar con **Espacio**, reiniciar con **R** y ajustar la velocidad.
- Usar el modo presentación para grabar la escena y sus controles.
- Comparar recorridos en el cuaderno y descargar un JSON con resultados.

En modo manual, la palanca queda bloqueada al llegar a la bifurcación. Pausar no permite modificar una decisión ya ejecutada. Durante un recorrido se congelan cantidades y criterios. En modo MCP, el agente elige antes de iniciar y el servidor usa un reloj fijo; pausa y velocidad locales quedan deshabilitadas. La simulación no representa frenado ni cambios de personas durante el recorrido.

El cuaderno vive en la pestaña actual: recargar la página lo borra. Descargá el JSON para conservar los experimentos. La app no llama a servicios externos por su cuenta; al conectar un LLM, el cliente recibe el escenario y gestiona esa información según su propia configuración.

## Un experimento de dos minutos

1. Elegí **Clásico 5:1**, modo **Yo decido**. Iniciá y mové la palanca. La animación ejecuta tu elección.
2. Reiniciá. Elegí **Regla en Python → Minimizar víctimas**. Observá los datos y la condición antes de iniciar.
3. Elegí **Inverso 1:5**. La misma regla ahora mantiene la vía.
4. Conservá 1:5 y elegí **Proteger la vía principal**. La regla desvía y afecta a cinco personas. Los hechos no cambiaron; el criterio sí.
5. Probá **Empate 3:3** con minimizar víctimas. Mostrá que el desempate también es una decisión de diseño: mantener.

## Qué enseña

| Concepto | Dónde aparece |
|---|---|
| Representación | Personas por vía y acciones como datos |
| Algoritmo | Procedimiento explícito en `decide()` |
| Condicionales | Comparaciones y reglas `if` |
| Decisión | Selección según un criterio escrito por una persona |
| Acción en un entorno | La interfaz aplica la decisión y mueve el tren |
| Feedback | Resultado observado y registro del recorrido |

El motor no aprende del feedback: ejecuta las mismas reglas. El ciclo percepción–acción aquí es mínimo, con un estado completamente conocido y consecuencias ciertas. Sirve para ilustrar acción sobre un entorno, sin pretender ser un agente autónomo general.

La demo **no reproduce los mecanismos internos de GPT**. No incluye un LLM embebido, inferencia probabilística ni entrenamiento; puede recibir decisiones de un LLM externo mediante MCP. Los tres criterios son reglas didácticas y no equivalen a teorías éticas completas. El resultado numérico no prueba qué decisión es moralmente correcta. No se asigna un valor distinto a la vida de ninguna persona.

## Estructura

```text
tranvia-lab/
  app.py              servidor HTTP local con biblioteca estándar
  decision.py         motor de decisión independiente de la interfaz
  scene.py            estado compartido y reloj del modo agente
  mcp_server.py       herramientas MCP mediante stdio
  mcp_config.py       generador de configuración para Codex
  iniciar.bat         lanzador para Windows
  AGENTS.md           guía operativa para agentes y humanos
  MCP.md              conexión, herramientas y diagnóstico
  README.md           referencias y documentación del proyecto
  test_decision.py    pruebas de reglas, empates y límites
  test_mcp.py         pruebas de estado, concurrencia y transporte MCP
  examples/
    run_mcp_demo.py   cliente de prueba MCP, sin invocar un LLM
  static/
    index.html        interfaz
    style.css         diseño adaptable y modo presentación
    app.js            dibujo, animación, controles e historial
    favicon.svg       icono local
```

Toda la carpeta es portable. Las rutas se resuelven respecto de `app.py`. Si la movés, regenerá la configuración MCP para actualizar su ruta absoluta. GitHub Pages por sí solo no ejecuta el servidor Python; este proyecto se descarga y se ejecuta localmente.

## Usar el motor desde Python

```python
from decision import decide

result = decide(main=5, branch=1, criterion="minimize")
print(result["action"])  # divert
print(result["reason"])
```

## API local

`POST /api/decide` recibe JSON:

```json
{"main": 5, "branch": 1, "criterion": "minimize"}
```

Criterios: `minimize`, `nonintervention`, `protect_main`. Devuelve acción, regla, explicación y consecuencias. Esta llamada evalúa; la interfaz aplica la acción al iniciar el recorrido.

## Verificar

```sh
python -m unittest -v
```

Las pruebas incluyen todas las combinaciones de 0 a 12 personas para minimizar víctimas, empates, criterios opuestos, entradas inválidas, revisiones desactualizadas y una comunicación real MCP stdio → HTTP local.

## Conectar un LLM con MCP

Ya incluye un servidor MCP stdio para que Codex u otro cliente pueda leer el mundo, preparar un escenario y ejecutar `keep` o `divert` con una justificación visible. Ver [MCP.md](MCP.md) para conectarlo y [AGENTS.md](AGENTS.md) para instrucciones operativas.

```sh
python mcp_config.py
```

Imprime la configuración de conexión para la ubicación actual de esta carpeta. No modifica la configuración de Codex. El servidor web debe estar iniciado por separado.

El estado del modo MCP reside en `scene.py` y el puente en `mcp_server.py`. En ese modo, el reloj del servidor permite completar un recorrido aunque se cierre la pestaña. Al volver a abrirla, la escena se sincroniza. Los últimos 100 resultados MCP se conservan hasta reiniciar Python.

## Extensiones posibles

Se puede comparar sistemáticamente las decisiones de distintos modelos o incorporar incertidumbre. Esta versión mantiene un mundo pequeño con consecuencias ciertas.

## Documentación técnica de referencia

Estas fuentes describen las herramientas utilizadas; no son papers científicos.

1. Python — servidor HTTP de la biblioteca estándar.  
   https://docs.python.org/3/library/http.server.html
2. Model Context Protocol — transporte stdio.  
   https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
3. Model Context Protocol — herramientas y llamadas.  
   https://modelcontextprotocol.io/specification/2025-11-25/server/tools
4. Codex — conexión de servidores MCP.  
   https://developers.openai.com/codex/mcp
