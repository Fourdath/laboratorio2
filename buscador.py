"""Busca títulos mediante TF-IDF y similitud del coseno."""

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ARCHIVO_CSV = Path(__file__).resolve().parent / "libros.csv"
try:
    libros = pd.read_csv(ARCHIVO_CSV)
except FileNotFoundError:
    raise SystemExit("No existe libros.csv. Ejecute primero: python procesamiento.py")

columnas_requeridas = {"titulo", "precio", "titulo_normalizado"}
if not columnas_requeridas.issubset(libros.columns):
    raise SystemExit("El CSV debe contener titulo, precio y titulo_normalizado.")

libros = libros.dropna(subset=["titulo_normalizado"]).copy()
libros["titulo_normalizado"] = libros["titulo_normalizado"].astype(str).str.strip()
libros = libros[libros["titulo_normalizado"] != ""].reset_index(drop=True)
if libros.empty:
    raise SystemExit("No hay títulos válidos. Revise procesamiento.py y libros.csv.")

# El vocabulario y la matriz se construyen una sola vez al cargar el módulo.
vectorizador = TfidfVectorizer()
try:
    matriz_tfidf = vectorizador.fit_transform(libros["titulo_normalizado"])
except ValueError as error:
    raise SystemExit(f"No se pudo construir el índice TF-IDF: {error}")


def buscar(consulta: str, top_k: int = 5):
    consulta = consulta.strip().lower()
    if not consulta:
        print("Ingrese una consulta no vacía.")
        return []
    if top_k <= 0:
        return []

    vector_consulta = vectorizador.transform([consulta])
    puntuaciones = cosine_similarity(vector_consulta, matriz_tfidf).ravel()
    indices = puntuaciones.argsort()[::-1]

    resultados = []
    for i in indices:
        if puntuaciones[i] <= 0:
            break
        resultados.append({
            "titulo": libros.iloc[i]["titulo"],
            "precio": float(libros.iloc[i]["precio"]),
            "similitud": float(puntuaciones[i]),
        })
        if len(resultados) >= top_k:
            break
    return resultados


if __name__ == "__main__":
    consulta = input("Ingrese una palabra o título: ")
    # Desafío de la guía: limitar la salida a tres resultados positivos.
    resultados = buscar(consulta, top_k=3)
    if not resultados:
        print("No se encontraron coincidencias.")
    for resultado in resultados:
        print(f"{resultado['titulo']} | Precio: £{resultado['precio']:.2f} | "
              f"Similitud: {resultado['similitud']:.4f}")
