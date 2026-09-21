# Conectar un agente al tranvía

El modelo decide en su cliente (Codex u otro compatible con MCP stdio). Este proyecto le ofrece herramientas para leer y modificar el mundo virtual. No incorpora un modelo, no requiere una API key y no envía solicitudes a OpenAI desde el servidor.

```text
LLM / Codex → MCP stdio → mcp_server.py → HTTP local → app.py / scene.py
                                                         ↕
                                               navegador con animación
```

## 1. Iniciar la simulación

```sh
python -B app.py
```

Abrir `http://127.0.0.1:8765/`. Mantener el servidor encendido.

## 2. Registrar el MCP en Codex

Desde esta carpeta, usando el Python con el que se ejecuta la app:

```sh
python mcp_config.py
```

El comando imprime un bloque TOML completo con rutas absolutas. Agregarlo a `~/.codex/config.toml` (Windows: `%USERPROFILE%\.codex\config.toml`) conservando las demás entradas. Si ya existe `[mcp_servers.tranvia_lab]`, reemplazar solo esa entrada. No pegarlo dentro de otra tabla. El script no hace modificaciones por su cuenta.

También puede usarse la configuración de MCP del cliente con estos campos:

- Transporte: **STDIO / comando local**.
- Comando: ruta absoluta al ejecutable Python.
- Argumentos: `-B`, ruta absoluta de `mcp_server.py`, `--url`, `http://127.0.0.1:8765`.

Si está instalada la CLI, la alternativa es:

```sh
codex mcp add tranvia_lab -- python -B /RUTA/ABSOLUTA/tranvia-lab/mcp_server.py
```

Reemplazar la ruta y ponerla entre comillas si tiene espacios. Si `python` no está en PATH, usar su ruta absoluta. El comando `codex` no es necesario para la configuración manual.

Recargar la conexión MCP o reiniciar el cliente para cargar la entrada. Si se mueve la carpeta, generar de nuevo las rutas con `mcp_config.py`. Para otro puerto: `python mcp_config.py --url http://127.0.0.1:8766`.

Guía oficial de configuración: [MCP en Codex](https://developers.openai.com/codex/mcp).

## 3. Pedir un experimento

> Usá el MCP tranvia_lab. Leé el escenario actual, prepará un experimento con esas cantidades y elegí si mantener o desviar. Justificá brevemente el criterio que usás, ejecutá la decisión y verificá el resultado al finalizar. No cambies el código.

La primera llamada es `get_scene` sin argumentos. Supongamos que devuelve `revision: 8` y cantidades 5 y 1:

```json
{"main": 5, "branch": 1, "expected_revision": 8}
```

Eso se envía a `prepare_scene`. Si devuelve revisión 9, un ejemplo de `run_decision` es:

```json
{
  "action": "divert",
  "reason": "En este escenario hipotético priorizo reducir las víctimas previstas de cinco a una.",
  "agent": "Codex",
  "expected_revision": 9
}
```

Son revisiones de ejemplo: leer siempre las reales. `run_decision` mueve la palanca e inicia el recorrido; la web lo muestra en la siguiente sincronización (~300 ms). Consultar `get_scene` después de unos 10 segundos para ver `result`. La explicación queda visible en la web y en el registro del experimento.

## Herramientas

| Herramienta | Efecto |
|---|---|
| `get_scene` | Lee estado, revisión, conexión del navegador y últimos 100 resultados MCP |
| `prepare_scene` | Configura 0–12 personas por vía y reserva el escenario para el agente |
| `run_decision` | Elige `keep` o `divert`, guarda justificación e inicia la simulación |
| `reset_scene` | Aborta/reinicia explícitamente, conservando cantidades y control MCP |

`keep` significa permanecer en la principal. `divert` significa accionar hacia el desvío. No hay un criterio moral obligatorio dentro de la herramienta. La justificación solicitada es un resumen comunicable, no una cadena de pensamiento privada.

## Estado y control humano

El navegador comunica su escenario local al servidor mientras está en modo manual o reglas. Cuando MCP prepara un experimento, el servidor pasa a ser la autoridad del recorrido. Se rechazan decisiones basadas en una revisión anterior y ejecuciones duplicadas. Un recorrido sigue avanzando aunque se cierre el navegador; al reabrir se recupera su estado.

El botón **Recuperar control manual** cancela el control del agente. Reiniciar desde la web también lo libera. Pausa y velocidad están disponibles para las demos locales, mientras que MCP usa un reloj fijo del servidor. Una sola persona/pestaña debe conducir el modo manual; las pestañas adicionales no son sesiones independientes.

La app escucha solo en loopback y esta integración no tiene autenticación. Está pensada para procesos locales de confianza; no se publica en red. El MCP implementa el subconjunto stdio de herramientas y ciclo de inicio, sin recursos, prompts ni transporte HTTP MCP. Referencias: [transporte MCP](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports), [herramientas MCP](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).

## Diagnóstico

Para comprobar el circuito completo sin registrar un cliente ni invocar un LLM:

```sh
python examples/run_mcp_demo.py
```

Este cliente de prueba usa realmente MCP stdio para leer, preparar y ejecutar un recorrido visible, y espera su resultado. Modifica el escenario actual; debe estar en reposo. Su criterio está escrito en el script y se identifica en pantalla como prueba, para no confundirlo con una decisión de un modelo.

- **No aparecen herramientas:** verificar el ejecutable/ruta del MCP y recargar su conexión.
- **Simulador no disponible:** iniciar `app.py`; verificar que ambos usen el mismo puerto.
- **Escenario cambió:** llamar a `get_scene`, reevaluar y usar la nueva revisión.
- **No se mueve en pantalla:** recargar la página tras actualizar JS y revisar `browser_connected`.
- **La terminal del MCP queda vacía:** es normal; espera JSON-RPC por stdin, no órdenes humanas.
- **Se reinició Python:** el historial MCP era en memoria; ya no está disponible.
