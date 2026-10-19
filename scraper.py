"""Extrae únicamente la primera página de Books to Scrape."""

import re
import warnings

import requests
from bs4 import BeautifulSoup


URL = "https://books.toscrape.com/"
ESTRELLAS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def obtener_libros():
    """Retorna una lista de diccionarios; omite tarjetas incompletas."""
    respuesta = requests.get(URL, timeout=10)
    respuesta.raise_for_status()
    # El HTML contiene UTF-8; evita interpretar el símbolo de libra como Â£.
    respuesta.encoding = "utf-8"
    soup = BeautifulSoup(respuesta.text, "html.parser")
    tarjetas = soup.select("article.product_pod")
    if not tarjetas:
        raise ValueError("No se encontraron libros. Revise los selectores HTML.")

    libros = []
    for numero, tarjeta in enumerate(tarjetas, start=1):
        try:
            enlace = tarjeta.select_one("h3 a")
            precio_html = tarjeta.select_one(".price_color")
            disponible_html = tarjeta.select_one(".availability")
            estrellas_html = tarjeta.select_one("p.star-rating")

            if any(elemento is None for elemento in
                   (enlace, precio_html, disponible_html, estrellas_html)):
                raise ValueError("falta alguno de los cuatro campos")

            # El atributo title contiene el título completo, sin truncar.
            titulo = enlace.get("title", "").strip()
            disponibilidad = disponible_html.get_text(" ", strip=True)
            coincidencia = re.search(r"\d+(?:\.\d+)?", precio_html.get_text())
            clases = estrellas_html.get("class", [])
            calificacion = next((ESTRELLAS[c] for c in clases if c in ESTRELLAS), None)

            if not titulo or not disponibilidad or coincidencia is None:
                raise ValueError("título, disponibilidad o precio no válido")
            if calificacion is None:
                raise ValueError("calificación fuera del rango de 1 a 5")

            libros.append({
                "titulo": titulo,
                "precio": float(coincidencia.group()),
                "disponibilidad": disponibilidad,
                "calificacion": calificacion,
            })
        except (ValueError, TypeError, AttributeError) as error:
            warnings.warn(f"Libro {numero} omitido: {error}", stacklevel=2)
            # Un libro incompleto no impide procesar los siguientes.
            continue

    return libros


if __name__ == "__main__":
    try:
        libros = obtener_libros()
    except (requests.RequestException, ValueError) as error:
        raise SystemExit(f"No se pudo extraer el catálogo: {error}")
    print(f"Total extraído: {len(libros)}")
    print("Primeros cinco registros:")
    for libro in libros[:5]:
        print(libro)
