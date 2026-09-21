# Tranvía Lab — guía para humanos y agentes

## Objetivo y alcance

Simulador educativo local del dilema del tranvía. Python mantiene reglas explícitas y un escenario compartido; Canvas muestra las acciones. Un LLM externo puede observar, decidir y actuar mediante MCP. La explicación que envía el LLM es una justificación pública, no una traza de sus operaciones internas.

El usuario quiere mover esta carpeta a otro lugar para subirla a GitHub: no inicializar Git, crear remotos ni publicar sin un pedido posterior. Mantener el proyecto portable y sin dependencias externas obligatorias.

## Levantar localmente

1. Abrir una terminal en la carpeta que contiene este archivo.
2. Verificar Python 3.10+: `python --version` (Windows: también `py -3 --version`).
3. Ejecutar `python -B app.py`. En Windows se puede hacer doble clic en `iniciar.bat`.
4. Abrir `http://127.0.0.1:8765/`. El servidor abre el navegador automáticamente, salvo con `--no-browser`.
5. Mantener el proceso vivo durante la demo. Ctrl+C lo detiene.

Sin paquetes que instalar: no usar pip, npm ni claves de API para este proyecto. `iniciar.bat` también detecta el Python local de Codex si existe; fuera de Codex basta con Python normal.

Antes de iniciar otro servidor, comprobar si la URL ya responde. Si se modificó Python, reiniciar el proceso de este proyecto; si cambió HTML/CSS/JS, recargar la página. Evitar detener procesos ajenos. Un puerto alternativo se elige con `python app.py --port 8766`; el MCP deberá usar esa misma URL.

## Conectar un LLM mediante MCP

El transporte es **stdio**: el cliente lanza `python -B mcp_server.py`. `app.py` es otro proceso y debe estar funcionando. La URL HTTP de la web no es una URL MCP.

1. Iniciar `app.py` y abrir la web para observar la demo.
2. Ejecutar `python mcp_config.py` para imprimir un bloque TOML con el ejecutable y la ruta absoluta de ESTA copia.
3. Agregar ese bloque a la configuración MCP del cliente. Para Codex, ver `MCP.md`.
4. Recargar los servidores MCP o reiniciar el cliente si hace falta. Verificar que aparezcan las cuatro herramientas.

Si se mueve la carpeta, volver a generar la configuración. No sobrescribir otras entradas del cliente ni afirmar que está conectado solo porque se creó el servidor.

### Circuito para un agente conectado

1. `get_scene`: leer cantidades, fase, `revision` y `browser_connected`. Un navegador desconectado no impide computar el experimento, pero la animación no estará siendo observada.
2. `prepare_scene(main, branch, expected_revision)`: usar las cantidades solicitadas o conservar las que se leyeron. Toma control y deja el tren listo.
3. Evaluar la situación según el pedido del usuario y enviar `run_decision(action, reason, expected_revision, agent)`. Usar la revisión DEVUELTA POR prepare_scene. `action` solo admite `keep` o `divert`; `reason` es una explicación pública breve. El servidor no obliga a minimizar víctimas.
4. La llamada inicia el tren; aún no es el resultado final. El recorrido dura unos 9.7 segundos. Consultar `get_scene` después y confirmar `phase == finished` y `result`.
5. Para otro recorrido: leer revisión actual y llamar a `prepare_scene` de nuevo. `reset_scene` interrumpe explícitamente uno en curso y conserva el control del agente.

Si una revisión fue rechazada, volver a leer y reconsiderar la acción. No reintentar a ciegas. Si una ejecución devuelve un error de transporte, consultar primero el estado: podría haber empezado. No inventar resultados ni afirmar que se accionó una palanca real.

La persona puede recuperar control desde la web; esa acción invalida la revisión previa del agente. En modo MCP, el reloj y los resultados son del servidor, y los controles de velocidad/pausa locales quedan deshabilitados.

## Archivos principales

- `app.py`: HTTP local; solo escucha en 127.0.0.1.
- `decision.py`: tres reglas deterministas didácticas.
- `scene.py`: escenario MCP, concurrencia, revisiones y reloj.
- `mcp_server.py`: protocolo MCP stdio y puente HTTP local.
- `mcp_config.py`: imprime configuración, sin modificar archivos del cliente.
- `static/app.js`: animación, modo humano/reglas y sincronización MCP.
- `MCP.md`: conexión, herramientas, limitaciones y ejemplo.

La persistencia es temporal: historial de navegador hasta recargar; historial MCP de los últimos 100 recorridos hasta reiniciar Python. El usuario puede exportar el historial visible a JSON.

## Verificación al cambiar código

```sh
python -B -m unittest -v
```

Si hay Node disponible: `node --check static/app.js`. Para cambios visuales, abrir la web y comprobar modo manual, regla en Python y modo MCP. Las pruebas de integración usan un puerto efímero y no deben cambiar el servidor de una demo en curso.

Mantener stdout del MCP exclusivamente para JSON-RPC UTF-8 separado por saltos de línea. Los diagnósticos van a stderr. No agregar logs, banners o prints de depuración a stdout.
