"""Limpia los libros extraídos y genera libros.csv."""

from pathlib import Path

import pandas as pd
import requests

from scraper import obtener_libros


ARCHIVO_CSV = Path(__file__).resolve().parent / "libros.csv"


def procesar_libros(libros):
    columnas = ["titulo", "precio", "disponibilidad", "calificacion"]
    df = pd.DataFrame(libros, columns=columnas)

    # Reduce espacios repetidos y elimina espacios en los extremos.
    for columna in ["titulo", "disponibilidad"]:
        df[columna] = df[columna].astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    df["titulo_normalizado"] = df["titulo"].str.lower()

    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df["calificacion"] = pd.to_numeric(df["calificacion"], errors="coerce")
    df = df.dropna(subset=columnas).copy()
    df = df[(df["titulo_normalizado"] != "") & (df["disponibilidad"] != "")]
    df = df[(df["precio"] >= 0) & df["calificacion"].isin([1, 2, 3, 4, 5])]
    # El título limpio en minúsculas permite detectar también variantes de caja.
    df = df.drop_duplicates(subset=["titulo_normalizado"]).reset_index(drop=True)
    df["precio"] = df["precio"].astype(float)
    df["calificacion"] = df["calificacion"].astype(int)
    return df


def main():
    libros = obtener_libros()
    df = procesar_libros(libros)
    if df.empty:
        raise ValueError("No quedaron libros válidos para exportar.")

    print("Primeras cinco filas:")
    print(df.head().to_string(index=False))
    print("\nInformación del DataFrame:")
    df.info()
    print(f"\nDimensiones: {df.shape}")
    print(f"Columnas: {list(df.columns)}")
    print(f"Cantidad de libros extraídos: {len(libros)}")
    print(f"Cantidad de libros procesados: {len(df)}")
    print(f"Precio promedio: £{df['precio'].mean():.2f}")
    df.to_csv(ARCHIVO_CSV, index=False, encoding="utf-8")
    print(f"Archivo generado: {ARCHIVO_CSV.name}")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, ValueError) as error:
        raise SystemExit(f"No se pudo procesar el catálogo: {error}")
