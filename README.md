# Tu primera llamada a un LLM vía API

Ejercicio en Python para Google Colab: enviar un mensaje a un LLM y comparar su respuesta al añadir instrucciones de rol.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/BrayherGomez/Ejercicio-Respuesta_de_modelo_via_API/blob/main/Primera_llamada_LLM_API.ipynb)

## Cómo ejecutarlo

1. Pulsa **Abrir en Colab** y guarda una copia en tu Google Drive si quieres conservar tus cambios.
2. Selecciona **OpenAI** o **Anthropic** en la celda de configuración, según la cuenta que tengas preparada.
3. En el panel **Secretos** (icono de llave), añade `OPENAI_API_KEY` o `ANTHROPIC_API_KEY` y habilita el acceso del notebook. También puedes introducir la clave en el campo oculto cuando se solicite.
4. Ejecuta las celdas en orden. Necesitas una clave válida, acceso al modelo y saldo o cuota de API disponibles.
5. Completa la tabla de observaciones y guarda tu copia con los resultados para la sesión en vivo.

## Contenido

- **Nivel 1:** llamada básica y respuesta impresa.
- **Nivel 2:** mismo mensaje y modelo, con un system prompt de experto en estimación de software.
- **Comparación:** respuestas en paralelo y tabla para analizar tono, detalle y estructura.
- **Nivel 3, opcional:** modelo utilizado, tokens y coste estimado. Incluye tarifas de referencia de GPT-4.1 mini verificadas el 13 de octubre de 2026; comprueba las tarifas actuales antes de utilizarlas. Para otros modelos, completa los precios oficiales.
- **Comprobación final y exportación:** valida que ambas respuestas terminaron y permite guardar una evidencia en JSON.

El notebook publicado no contiene claves ni respuestas ejecutadas. Su estructura y ambos flujos se comprobaron localmente con respuestas simuladas; las llamadas reales se realizan al ejecutarlo con tu cuenta. Cada repetición de los niveles 1 y 2 consume API.

## Archivos

- [`Primera_llamada_LLM_API.ipynb`](Primera_llamada_LLM_API.ipynb): notebook completo para Colab.
- [`crear_notebook.py`](crear_notebook.py): generador del notebook. Para regenerarlo, ejecuta `python crear_notebook.py` con Python 3.

## Documentación oficial

- [OpenAI: generación de texto](https://developers.openai.com/api/docs/guides/text)
- [Anthropic: Messages API](https://platform.claude.com/docs/en/api/python/messages/create)
- [Precios de OpenAI](https://platform.openai.com/pricing)
- [Precios de Anthropic](https://www.anthropic.com/pricing)

Mantén las claves en Secretos de Colab. Revisa las respuestas antes de publicar una copia ejecutada o compartir el archivo de evidencia.
