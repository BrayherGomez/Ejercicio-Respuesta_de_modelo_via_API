import ast
import json
from pathlib import Path

cells = []

def md(text):
    cells.append({'cell_type': 'markdown', 'metadata': {}, 'source': text.splitlines(True)})

def code(text):
    cells.append({'cell_type': 'code', 'metadata': {}, 'source': text.splitlines(True), 'execution_count': None, 'outputs': []})

md('''# Tu primera llamada a un LLM vía API

**Objetivo:** enviar el mismo mensaje sin instrucciones de rol y con un system prompt, e interpretar las diferencias.

## Cómo usar este notebook
1. Abre [Google Colab](https://colab.research.google.com/), elige **Archivo → Subir notebook** y selecciona este `.ipynb`.
2. Elige el proveedor de tu cuenta en la celda de configuración.
3. En el icono de llave de Colab, crea el secreto `OPENAI_API_KEY` o `ANTHROPIC_API_KEY` y habilita su acceso para este notebook. También puedes introducir la clave en un campo oculto cuando se solicite.
4. Ejecuta las celdas en orden y completa tus observaciones.

Las celdas de los niveles 1 y 2 hacen una llamada real cada una. Repetirlas genera nuevas llamadas y consumo. La clave no se imprime ni se guarda en el código. Este notebook se entrega sin respuestas ejecutadas: la verificación real requiere tu clave y acceso al modelo.
''')
code('%pip install -q -U openai anthropic')
md('## Configuración\nUsa solo el proveedor que configuraste anteriormente. Puedes cambiar el ID del modelo por uno disponible en tu cuenta.')
code('''# @title 1. Selecciona tu proveedor y escribe el mensaje
PROVEEDOR = "openai"  # @param ["openai", "anthropic"]
MODELOS = {"openai": "gpt-4.1-mini", "anthropic": "claude-haiku-5-5"}
if PROVEEDOR not in MODELOS:
    raise ValueError('Elige "openai" o "anthropic".')
MODELO = MODELOS[PROVEEDOR]
MENSAJE = "¿Cómo puedo estimar el tiempo necesario para desarrollar una aplicación web?"  # @param {type:"string"}
SYSTEM_PROMPT = (
    "Eres un experto en estimación de software. Responde en español, con tono profesional "
    "y didáctico. Organiza tu respuesta en: supuestos, pasos para estimar, un ejemplo "
    "con un rango de tiempo y riesgos. Explica la incertidumbre y evita dar una fecha "
    "exacta sin conocer el alcance. Limita la respuesta a unas 250 palabras."
)
''')
code('''from getpass import getpass

nombre_secreto = "OPENAI_API_KEY" if PROVEEDOR == "openai" else "ANTHROPIC_API_KEY"
try:
    from google.colab import userdata
    api_key = userdata.get(nombre_secreto)
except Exception:
    api_key = getpass(f"Introduce {nombre_secreto} (entrada oculta): ")
if not api_key or not api_key.strip():
    raise ValueError("Falta la clave API. Configura el secreto o introduce una clave.")

if PROVEEDOR == "openai":
    from openai import OpenAI
    cliente = OpenAI(api_key=api_key.strip(), timeout=60.0, max_retries=0)
else:
    from anthropic import Anthropic
    cliente = Anthropic(api_key=api_key.strip(), timeout=60.0, max_retries=0)
del api_key
print(f"Cliente preparado: {PROVEEDOR} / {MODELO}. Aún no se ha hecho ninguna llamada.")
''')
md('''## Nivel 1 — Llamada básica
Se envía un único mensaje de usuario. Observa la llamada específica de cada proveedor.
''')
code('''if PROVEEDOR == "openai":
    respuesta_1 = cliente.responses.create(
        model=MODELO, input=MENSAJE, max_output_tokens=1200,
    )
    texto_1 = respuesta_1.output_text
else:
    respuesta_1 = cliente.messages.create(
        model=MODELO, max_tokens=1200,
        messages=[{"role": "user", "content": MENSAJE}],
    )
    texto_1 = "\\n".join(b.text for b in respuesta_1.content if b.type == "text")

if not texto_1.strip():
    raise RuntimeError("La API respondió sin texto visible. Revisa la respuesta y el límite de tokens.")
print(texto_1)
configuracion_1 = (PROVEEDOR, MODELO, MENSAJE)
''')
md('''## Nivel 2 — Añadir un system prompt
Se conserva **exactamente el mismo mensaje, modelo y límite de salida**. Solo añadimos las instrucciones de rol. OpenAI Responses las recibe en `instructions`; Anthropic Messages las recibe en `system`. Cada llamada es independiente, sin historial de la anterior.
''')
code('''if "configuracion_1" not in globals():
    raise RuntimeError("Ejecuta el nivel 1 antes del nivel 2.")
if configuracion_1 != (PROVEEDOR, MODELO, MENSAJE):
    raise RuntimeError("La configuración cambió. Ejecuta de nuevo el nivel 1 para comparar el mismo mensaje y modelo.")
if PROVEEDOR == "openai":
    respuesta_2 = cliente.responses.create(
        model=MODELO, instructions=SYSTEM_PROMPT,
        input=MENSAJE, max_output_tokens=1200,
    )
    texto_2 = respuesta_2.output_text
else:
    respuesta_2 = cliente.messages.create(
        model=MODELO, system=SYSTEM_PROMPT, max_tokens=1200,
        messages=[{"role": "user", "content": MENSAJE}],
    )
    texto_2 = "\\n".join(b.text for b in respuesta_2.content if b.type == "text")

if not texto_2.strip():
    raise RuntimeError("La API respondió sin texto visible. Revisa la respuesta y el límite de tokens.")
print(texto_2)
configuracion_2 = (PROVEEDOR, MODELO, MENSAJE)
''')
md('## Comparar las respuestas\nLa siguiente celda reutiliza las respuestas guardadas; no hace llamadas adicionales.')
code('''print("NIVEL 1 — SIN ROL\\n")
print(texto_1)
print("\\n" + "=" * 70 + "\\nNIVEL 2 — CON ROL\\n")
print(texto_2)
print(f"\\nPalabras aproximadas: nivel 1 = {len(texto_1.split())}; nivel 2 = {len(texto_2.split())}")
''')
code('''from html import escape
from IPython.display import HTML, display

display(HTML(
    '<div style="display:flex;gap:20px;flex-wrap:wrap">' +
    ''.join(
        '<section style="flex:1;min-width:260px;border:1px solid #bbb;border-radius:10px;padding:16px">'
        f'<h3>{escape(titulo)}</h3><div style="white-space:pre-wrap">{escape(texto)}</div></section>'
        for titulo, texto in [("Nivel 1: sin rol", texto_1), ("Nivel 2: experto en estimación", texto_2)]
    ) + '</div>'
))
''')
md('''### Tus observaciones
Edita esta celda después de ejecutar los dos niveles:

| Aspecto | Nivel 1: sin rol | Nivel 2: con rol |
|---|---|---|
| Tono | Completar | Completar |
| Nivel de detalle | Completar | Completar |
| Estructura | Completar | Completar |
| Supuestos e incertidumbre | Completar | Completar |

**Conclusión personal:** ¿qué instrucciones se reflejaron en la segunda respuesta? Incluye un ejemplo concreto.

Las respuestas pueden variar entre ejecuciones. Una comparación aislada ilustra el efecto del prompt, pero no demuestra que toda diferencia se deba exclusivamente a él.
''')
md('## Nivel 3 — Metadatos (opcional)\nEstos datos proceden de las dos respuestas reales, sin hacer nuevas llamadas.')
code('''def metadatos(respuesta):
    uso = respuesta.usage
    if uso is None:
        raise RuntimeError("La respuesta no contiene metadatos de uso.")
    if PROVEEDOR == "openai":
        detalles = uso.input_tokens_details
        cache = getattr(detalles, "cached_tokens", 0) or 0
        escritura = 0
    else:
        cache = getattr(uso, "cache_read_input_tokens", 0) or 0
        escritura = getattr(uso, "cache_creation_input_tokens", 0) or 0
    return {
        "modelo": respuesta.model,
        "tokens_entrada": uso.input_tokens,
        "tokens_salida": uso.output_tokens,
        "tokens_lectura_cache": cache,
        "tokens_escritura_cache": escritura,
    }

datos = {"Nivel 1": metadatos(respuesta_1), "Nivel 2": metadatos(respuesta_2)}
for nivel, valores in datos.items():
    print(nivel, valores)
''')
md('''### Coste estimado en USD (opcional)
Consulta las tarifas **del modelo devuelto por la API**: [OpenAI](https://platform.openai.com/pricing) o [Anthropic](https://www.anthropic.com/pricing). Introduce precios por **un millón de tokens**, para llamadas estándar de texto, sin Batch ni herramientas.

Fórmula: `(entrada × tarifa_entrada + salida × tarifa_salida) / 1_000_000`. La caché puede tener tarifas diferentes. En OpenAI, los tokens de caché están incluidos en `input_tokens`; en Anthropic se reportan por separado. El cálculo siguiente contempla esa diferencia y detiene la estimación si aparece caché sin tarifa configurada. Es una estimación, no una factura.
''')
code('''# Tarifas de GPT-4.1 mini verificadas el 13 de octubre de 2026.
# Para otro modelo o proveedor, completa las tarifas de su página oficial.
es_gpt41_mini = PROVEEDOR == "openai" and all(
    d["modelo"] == "gpt-4.1-mini" or d["modelo"].startswith("gpt-4.1-mini-")
    for d in datos.values()
)
PRECIO_ENTRADA_USD_POR_MILLON = 0.40 if es_gpt41_mini else None
PRECIO_SALIDA_USD_POR_MILLON = 1.60 if es_gpt41_mini else None
PRECIO_LECTURA_CACHE_USD_POR_MILLON = 0.10 if es_gpt41_mini else None
PRECIO_ESCRITURA_CACHE_USD_POR_MILLON = None

def coste_estimado(d):
    entrada = d["tokens_entrada"]
    lectura = d["tokens_lectura_cache"]
    escritura = d["tokens_escritura_cache"]
    if PROVEEDOR == "openai":
        entrada -= lectura
    total = entrada * PRECIO_ENTRADA_USD_POR_MILLON + d["tokens_salida"] * PRECIO_SALIDA_USD_POR_MILLON
    for cantidad, tarifa in [(lectura, PRECIO_LECTURA_CACHE_USD_POR_MILLON),
                             (escritura, PRECIO_ESCRITURA_CACHE_USD_POR_MILLON)]:
        if cantidad and tarifa is None:
            raise ValueError("Hay tokens de caché: configura su tarifa oficial.")
        if cantidad:
            total += cantidad * tarifa
    return total / 1_000_000

if PRECIO_ENTRADA_USD_POR_MILLON is None or PRECIO_SALIDA_USD_POR_MILLON is None:
    print("Completa las tarifas oficiales y vuelve a ejecutar esta celda.")
else:
    tarifas = [PRECIO_ENTRADA_USD_POR_MILLON, PRECIO_SALIDA_USD_POR_MILLON,
               PRECIO_LECTURA_CACHE_USD_POR_MILLON, PRECIO_ESCRITURA_CACHE_USD_POR_MILLON]
    if any(t is not None and (not isinstance(t, (int, float)) or t < 0) for t in tarifas):
        raise ValueError("Las tarifas deben ser números no negativos.")
    costes = {nivel: coste_estimado(d) for nivel, d in datos.items()}
    for nivel, coste in costes.items():
        print(f"{nivel}: USD {coste:.8f}")
    print(f"Total de ambas llamadas: USD {sum(costes.values()):.8f}")
''')
md('''## Comprobación de la entrega
La celda siguiente comprueba que ambas respuestas contienen texto, proceden de la misma configuración y han terminado sin alcanzar el límite de generación. No hace llamadas a la API. La valoración de tono, detalle y estructura debes completarla tú.
''')
code('''assert configuracion_1 == configuracion_2 == (PROVEEDOR, MODELO, MENSAJE), "Repite ambos niveles con la misma configuración."
assert texto_1.strip() and texto_2.strip(), "Falta una respuesta visible."
for nivel, respuesta in [("Nivel 1", respuesta_1), ("Nivel 2", respuesta_2)]:
    estado = respuesta.status if PROVEEDOR == "openai" else respuesta.stop_reason
    esperado = "completed" if PROVEEDOR == "openai" else "end_turn"
    assert estado == esperado, f"{nivel}: respuesta incompleta o parada inesperada ({estado}). Revisa el límite de salida."
    print(f"✓ {nivel}: respuesta real recibida y completada ({respuesta.model}).")
print("✓ Niveles obligatorios completados. Completa tus observaciones y guarda el notebook.")
''')
md('''## Guardar una evidencia de las respuestas (opcional)
Esta celda guarda el mensaje, el system prompt, ambas respuestas y sus metadatos en `resultados_llm.json`. No incluye la clave ni los encabezados de autenticación. Puedes descargar el archivo desde el panel **Archivos** de Colab. Antes de compartirlo, revisa su contenido.
''')
code('''import json
from pathlib import Path
from datetime import datetime, timezone

evidencia = {
    "fecha_utc": datetime.now(timezone.utc).isoformat(),
    "proveedor": PROVEEDOR,
    "mensaje": MENSAJE,
    "system_prompt_nivel_2": SYSTEM_PROMPT,
    "nivel_1": {"texto": texto_1, "metadatos": datos["Nivel 1"]},
    "nivel_2": {"texto": texto_2, "metadatos": datos["Nivel 2"]},
}
Path("resultados_llm.json").write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")
print("Evidencia guardada: resultados_llm.json")
''')
md('''## Si aparece un error
- **401 / AuthenticationError:** comprueba la clave y el proveedor seleccionado.
- **429 / RateLimitError:** revisa saldo, cuota y límites de tu cuenta antes de repetir.
- **404 / NotFoundError:** revisa el ID del modelo y su disponibilidad en tu cuenta.
- **Error de conexión o timeout:** revisa la conexión y vuelve a ejecutar la celda afectada.
- **Respuesta cortada:** revisa `respuesta_1.status` / `respuesta_2.status` en OpenAI o `stop_reason` en Anthropic; aumenta el límite de salida si corresponde.
- **NameError:** ejecuta primero las celdas de configuración y los niveles en orden.

## Antes de la sesión en vivo
- [ ] Nivel 1 ejecutado con respuesta visible y sin errores.
- [ ] Nivel 2 ejecutado con respuesta visible y sin errores.
- [ ] Tabla de observaciones y conclusión completadas.
- [ ] Notebook guardado con las respuestas; clave guardada únicamente como secreto.

## Documentación oficial
- [OpenAI: generación de texto y Responses](https://developers.openai.com/api/docs/guides/text)
- [OpenAI: GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini)
- [Anthropic: Messages API en Python](https://platform.claude.com/docs/en/api/python/messages/create)
- [Anthropic: modelos e IDs](https://platform.claude.com/docs/en/models/overview)
''')

notebook = {'nbformat': 4, 'nbformat_minor': 5, 'metadata': {
    'colab': {'provenance': []},
    'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
    'language_info': {'name': 'python'},
}, 'cells': cells}
for index, cell in enumerate(cells):
    cell['id'] = f'celda-{index:02d}'
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if not source.startswith('%'):
            ast.parse(source)
path = Path('Primera_llamada_LLM_API.ipynb')
path.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Notebook generado: {path.resolve()} ({len(cells)} celdas). Sintaxis Python verificada.')
