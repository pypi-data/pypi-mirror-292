# llm_content_filter

`llm_content_filter` es un paquete de Python flexible y fácil de usar que permite filtrar texto inapropiado para grandes modelos de lenguaje (LLMs). Con soporte para personalizar palabras prohibidas, manejar sinónimos y realizar filtrado contextual, es una herramienta poderosa para moderar contenido generado por LLMs.

## Instalación

Puedes instalar el paquete usando `pip`:

```bash
pip install llm_content_filter

Uso
Aquí tienes un ejemplo de cómo utilizar llm_content_filter en un proyecto:

1. Filtrado básico con palabras predeterminadas

```python

from llm_content_filter.filter import LLMContentFilter

# Crear una instancia del filtro con las palabras predeterminadas
filter = LLMContentFilter()

# Verificar si un texto es apropiado
text = "This text promotes violence"
if not filter.is_appropriate(text):
    print("Texto inapropiado detectado!")

# Filtrar el texto inapropiado
clean_text = filter.filter_text(text)
print(clean_text)

2. Usar palabras prohibidas personalizadas

```python
from llm_content_filter.filter import LLMContentFilter

# Crear una instancia del filtro con palabras prohibidas personalizadas
custom_banned_words = ["spam", "scam"]
filter = LLMContentFilter(banned_words=custom_banned_words)

# Filtrar un texto con las palabras personalizadas
text = "This text is a scam"
clean_text = filter.filter_text(text, replacement="[BLOCKED]")
print(clean_text)

3. Cargar y guardar listas de palabras prohibidas desde un archivo JSON


```python
from llm_content_filter.filter import LLMContentFilter

# Crear una instancia del filtro cargando las palabras prohibidas desde un archivo JSON
filter = LLMContentFilter(banned_words_file="custom_banned_words.json")

# Verificar si un texto es apropiado
text = "This text is offensive"
if not filter.is_appropriate(text):
    print("Texto inapropiado detectado!")

# Guardar las palabras prohibidas actuales en un archivo JSON
filter.save_banned_words_to_file("updated_banned_words.json")

4. Filtrado avanzado con sinónimos y normalización de texto

```python
from llm_content_filter.filter import LLMContentFilter

# Supongamos que tienes un archivo JSON que incluye sinónimos y otras configuraciones avanzadas
filter = LLMContentFilter(banned_words_file="custom_banned_words_with_synonyms.json")

# Filtrar un texto con acentos y sinónimos
text = "This text contains brutalité, which is a form of violence"
clean_text = filter.filter_text(text)
print(clean_text)  # Salida: "this text contains [REDACTED], which is a form of [REDACTED]"


###Características
**Personalización Total: Define tus propias listas de palabras prohibidas o carga listas desde archivos JSON.
**Manejo de Sinónimos: Detecta y filtra variaciones de palabras prohibidas usando sinónimos.
**Filtrado Contextual: Soporte para filtrado avanzado basado en el contexto (próximamente).
**Normalización de Texto: Elimina acentos y caracteres especiales para un filtrado más robusto.

```json
{
    "banned_words": [
        "violence",
        "hate",
        "discrimination",
        "abuse",
        "offensive"
    ],
    "synonyms": {
        "violence": ["aggression", "brutality", "cruelty"],
        "hate": ["detest", "loathe", "abhor"],
        "discrimination": ["prejudice", "bias", "inequality"],
        "abuse": ["mistreatment", "misuse", "exploitation"],
        "offensive": ["insulting", "derogatory", "rude"]
    },
    "severity_levels": {
        "violence": 5,
        "hate": 4,
        "discrimination": 4,
        "abuse": 5,
        "offensive": 3
    },
    "replacement_words": {
        "default": "[REDACTED]",
        "violence": "[VIOLENCE]",
        "hate": "[HATE]",
        "discrimination": "[DISCRIMINATION]",
        "abuse": "[ABUSE]",
        "offensive": "[OFFENSIVE]"
    },
    "contextual_filtering": {
        "enabled": true,
        "context_threshold": 0.8
    }
}

