import string
# Programa para contar palabras en un archivo de texto
# 1. Pedir al usuario la ruta de un archivo de texto.
# 2. Leer el contenido del archivo.
# 3. Separar en palabras.
# 4. Contar número total de palabras.
 
import re
from collections import Counter
import sys

class ContadorDePalabras:
    def __init__(self, path: str | None = None):
        self.path = path
        self.texto = ""

    def leer_archivo(self, path: str | None = None) -> None:
        ruta = path or self.path
        if not ruta:
            raise ValueError("No se proporcionó ruta de archivo.")
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                self.texto = f.read()
        except FileNotFoundError:
            print("no se encontro el archivo buscado")
            sys.exit(1)

    def contar_palabras(self, top_n: int = 10):
        palabras = re.findall(r"\w+", self.texto.lower())
        total_palabras = len(palabras)
        contador = Counter(palabras)
        mas_comunes = contador.most_common(top_n)
        return total_palabras, mas_comunes

if __name__ == "__main__":
    path = input("ingresar ruta de acceso del archivo: ")
    contador = ContadorDePalabras()
    contador.leer_archivo(path)
    total, mas_comunes = contador.contar_palabras(10)
    print(f"Total palabras: {total}")
    print("Palabras más frecuentes:")
    for palabra, freq in mas_comunes:
        print(f"{palabra}: {freq}")