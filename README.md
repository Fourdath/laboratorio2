# Laboratorio 2: Web Scraping y recuperación de información

**Asignatura:** Ingeniería Web Avanzada, OII436-1.

**Integrantes:** COMPLETAR con los nombres antes de entregar.

**Repositorio:** https://github.com/Fourdath/laboratorio2

## Objetivo

Extraer los libros de la primera página de https://books.toscrape.com/, limpiar
los registros y recuperar títulos con TF-IDF y similitud del coseno.
El programa no sigue los enlaces de paginación ni las páginas de cada libro.

## Archivos

| Archivo | Función |
| --- | --- |
| `scraper.py` | Solicitud HTTP, análisis del HTML y extracción de los cuatro atributos. |
| `procesamiento.py` | Limpieza con Pandas, indicadores y exportación del CSV. |
| `buscador.py` | Índice TF-IDF y búsqueda por similitud del coseno. |
| `libros.csv` | Datos generados por `procesamiento.py`; no se copiaron manualmente. |
| `requirements.txt` | Versiones de las dependencias obtenidas mediante `pip freeze`. |
| `.gitignore` | Excluye `.venv/`, cachés de Python y archivos de configuración sensibles. |

## Reproducción desde un entorno virtual nuevo

Se comprobó la ejecución con Python 3.12. Las versiones fijadas de las dependencias
requieren Python 3.12 o posterior compatible.

### Windows: PowerShell

Clonar el repositorio y abrir una terminal dentro de `laboratorio2`:

```powershell
git clone https://github.com/Fourdath/laboratorio2.git
cd laboratorio2
```

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

El intérprete mostrado debe estar dentro de `.venv` y la segunda línea debe
mostrar `True`. El comando de activación en PowerShell es
`.venv\Scripts\Activate.ps1`.

Si PowerShell bloquea la activación, puede abrirse **CMD** en la misma carpeta:

```bat
.venv\Scripts\activate.bat
```

Después se ejecutan en CMD los comandos `python` de instalación y ejecución.

### Linux o macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En la validación de este proyecto se creó y activó `.venv` en Linux con
`source .venv/bin/activate`, se instalaron las cuatro bibliotecas solicitadas y
se generó `requirements.txt` con `python -m pip freeze > requirements.txt`.

### Orden de ejecución

```bash
python scraper.py
python procesamiento.py
python buscador.py
```

El primer comando permite revisar el total y los primeros cinco registros.
El segundo solicita nuevamente la primera página, limpia los datos y genera
`libros.csv`. También puede ejecutarse directamente `procesamiento.py` para
realizar una sola solicitud de extracción. Importar `scraper` no realiza
solicitudes: la ejecución de demostración está protegida con
`if __name__ == "__main__":`.

El buscador lee el CSV y no accede al sitio. Para cada consulta se ejecuta
`python buscador.py` y se escribe una entrada cuando aparece la pregunta.

### Comprobar que Git excluye el entorno

```bash
git init
git check-ignore .venv/pyvenv.cfg
git status --short --untracked-files=all
```

Se verificó que `git check-ignore` devuelve `.venv/pyvenv.cfg` y que los archivos
del entorno no aparecen en `git status`. No subir `.venv/` al repositorio.

## Extracción y limpieza

La solicitud se realiza con `requests.get(URL, timeout=10)` y se valida con
`raise_for_status()`. Se interpreta el contenido como UTF-8 y se procesa con
BeautifulSoup y el analizador `html.parser`.

Los selectores corresponden al HTML de la primera página:

| Elemento | Selector o atributo | Tratamiento |
| --- | --- | --- |
| Tarjeta del libro | `article.product_pod` | Una tarjeta por registro. |
| Título completo | `h3 a`, atributo `title` | Evita usar el texto visual truncado. |
| Precio | `.price_color` | Extrae la parte numérica y convierte a `float`; moneda: GBP. |
| Disponibilidad | `.availability` | Extrae texto y elimina espacios sobrantes. |
| Estrellas | `p.star-rating`, clases `One` a `Five` | Mapea las clases a enteros de 1 a 5. |

Para contrastarlos en un navegador: abrir el catálogo, pulsar F12, seleccionar
una tarjeta y revisar su HTML en la pestaña de elementos.

Si una tarjeta tiene un campo ausente o no válido, se emite una advertencia,
se omite ese registro y se continúa con los demás. Si no se encuentra ninguna
tarjeta, se informa un posible cambio de selectores. Los errores HTTP o de
conexión se informan sin inventar datos.

Pandas elimina espacios repetidos y externos, crea `titulo_normalizado` en
minúsculas y elimina duplicados por ese título normalizado. Convierte precio
y calificación a valores numéricos, descarta registros inválidos y conserva
`precio` como `float64` y `calificacion` como `int64`. El CSV se escribe sin
índice y con codificación UTF-8.

## Evidencias de la ejecución

Validación realizada el 19 de octubre de 2026 sobre la primera página real:

- Libros extraídos: **20**.
- Libros después de la limpieza: **20**.
- Dimensiones del DataFrame: **20 filas y 5 columnas**.
- Precio promedio: **£38.05** (promedio sin redondear: 38.0485 GBP).
- Registros duplicados o inválidos descartados en esta ejecución: **0**.

Primeros cinco registros obtenidos:

| Título | Precio (GBP) | Disponibilidad | Calificación |
| --- | ---: | --- | ---: |
| A Light in the Attic | 51.77 | In stock | 3 |
| Tipping the Velvet | 53.74 | In stock | 1 |
| Soumission | 50.10 | In stock | 1 |
| Sharp Objects | 47.82 | In stock | 4 |
| Sapiens: A Brief History of Humankind | 54.23 | In stock | 5 |

## Dos consultas e interpretación

### Consulta 1: `the`

Salida real de `python buscador.py`:

```text
Ingrese una palabra o título: the
The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull | Precio: £17.93 | Similitud: 0.4181
The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics | Precio: £22.60 | Similitud: 0.3630
The Black Maria | Precio: £52.15 | Similitud: 0.3282
```

Los tres resultados tienen similitud positiva y aparecen de mayor a menor.
El orden depende de los pesos TF-IDF y de la normalización de los vectores,
además de las coincidencias de palabras. No se ordenan por precio ni por estrellas.
En inglés, `the` es una palabra frecuente y poco descriptiva; se conserva porque
se utiliza la configuración predeterminada de la guía, sin eliminar stopwords.

### Consulta 2: `light`

```text
Ingrese una palabra o título: light
A Light in the Attic | Precio: £51.77 | Similitud: 0.5760
```

Esta consulta recupera un único título. Su puntuación es positiva porque
comparte el término `light`. La coincidencia no alcanza 1 porque el título
contiene otras palabras. En comparación, `the` recupera varios títulos y
`light` permite una búsqueda más específica dentro de esta colección.

### Desafío: `top_k=3`

La función conserva la firma `buscar(consulta, top_k=5)`, y en el bloque de
ejecución se llama a `buscar(consulta, top_k=3)`.
Se comprobó que `buscar("the")` devuelve **5** resultados, mientras que
`buscar("the", top_k=3)` devuelve **3**, todos con similitud positiva.

## Pruebas funcionales

Los cuatro casos se ejecutaron iniciando `buscador.py` con cada entrada:

| Caso | Consulta utilizada | Resultado observado | Estado |
| --- | --- | --- | --- |
| T1 | `the` | Tres resultados positivos: The Coming Woman (0.4181), The Boys in the Boat (0.3630), The Black Maria (0.3282), en orden descendente. | Cumple |
| T2 | `zzxyz123` | Mensaje: «No se encontraron coincidencias». | Cumple |
| T3 | `THE` | Mismos tres títulos, mismo orden y mismas puntuaciones que T1. También se comprobó la igualdad de los resultados sin redondear. | Cumple |
| T4 | Cadena vacía, presionando Enter | Mensajes: «Ingrese una consulta no vacía» y «No se encontraron coincidencias». El programa finaliza sin excepción. | Cumple |

No se detectaron incumplimientos en estos cuatro casos. El segundo mensaje de
T4 corresponde al bloque principal al recibir la lista vacía que retorna `buscar`.

## Respuestas a las preguntas evaluadas

**1. ¿Para qué sirve BeautifulSoup y cómo se diferencia de requests?**

BeautifulSoup analiza el HTML y permite localizar elementos, atributos y textos
mediante selectores. `requests` realiza la solicitud HTTP y obtiene la respuesta
del servidor. En este trabajo, `requests` descarga la página y BeautifulSoup
extrae los atributos de los libros desde su HTML.

**2. ¿Qué riesgo existe al depender de selectores HTML específicos si el sitio cambia?**

Si cambian las etiquetas, clases o estructura, los selectores pueden dejar de
encontrar los elementos o seleccionar datos incorrectos. Esto podría producir
registros incompletos o una extracción vacía. Hay que validar los campos y
actualizar los selectores cuando cambie el sitio.

**3. ¿Por qué normalizar los títulos antes de implementar la búsqueda?**

Permite tratar de forma consistente variantes de mayúsculas y espacios. Así,
`THE` y `the` producen el mismo tratamiento y se facilitan la limpieza y la
detección de duplicados. En este programa también se normaliza la consulta;
el vectorizador predeterminado convierte a minúsculas, por lo que el campo
normalizado hace explícita la preparación y sirve para la limpieza previa.

**4. ¿Qué función cumple fit_transform() sobre los títulos y por qué se usa transform() para la consulta?**

`fit_transform()` aprende el vocabulario y los pesos IDF del conjunto de títulos
y construye su matriz TF-IDF. `transform()` representa la consulta utilizando
ese mismo vocabulario y esos mismos pesos, sin volver a aprenderlos. De este
modo, consulta y documentos quedan en el mismo espacio de características y
pueden compararse. Un término nuevo de la consulta que no está en el vocabulario
no aporta componentes al vector.

**5. Si dos libros obtienen similitudes de 0.75 y 0.20, ¿cuál se muestra primero? ¿Qué indica una puntuación cercana a cero?**

El libro con 0.75 aparece primero porque se ordena de mayor a menor similitud.
Una puntuación cercana a cero indica poca coincidencia entre las representaciones
TF-IDF de consulta y título. Una puntuación exactamente cero significa que no
comparten términos con peso en el vocabulario usado; esos resultados se excluyen.
La puntuación no es una probabilidad de relevancia ni mide comprensión semántica.

**6. ¿Qué limitación tiene buscar solo por palabras presentes en títulos mediante TF-IDF? Proponga una mejora concreta.**

La búsqueda depende de coincidencias léxicas y de la poca información del título.
Puede no encontrar un libro relevante si la consulta usa un sinónimo, otro idioma
o un concepto que no aparece en el título. Una mejora concreta sería indexar
también la descripción y utilizar embeddings de texto para comparar el significado
de las consultas y los documentos. Esto requeriría ampliar la extracción en una
versión posterior; en este laboratorio se mantiene la restricción de una página.

## Entrega en GitHub

Repositorio de entrega: https://github.com/Fourdath/laboratorio2

Los siete archivos requeridos están en la raíz del repositorio. No se versionan
el entorno virtual `.venv/`, la carpeta `.git/` ni las cachés de Python.
Antes de entregar, completar los nombres de integrantes al inicio de este README
y ejecutar los programas en el computador de entrega para verificar los resultados.
