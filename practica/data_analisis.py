from pathlib import Path
import csv
import sys
import statistics
import json

def leer_con_pandas(path: str | Path = "datos.csv"):
    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError("pandas no está instalado. Ejecuta: python -m pip install pandas")

    ruta = Path(path)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    # intenta con utf-8 y fallback a latin-1
    try:
        return pd.read_csv(ruta, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(ruta, encoding="latin-1")


def leer_con_csv(path: str | Path = "datos.csv", delimiter: str = ","):
    """
    Lee el CSV sin dependencias externas. Devuelve una lista de diccionarios.
    Útil si no quieres instalar pandas.
    """
    ruta = Path(path)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    with ruta.open("r", encoding="utf-8", errors="replace") as f:
        lector = csv.DictReader(f, delimiter=delimiter)
        return list(lector)


def estadisticas_con_pandas(path: str | Path = "datos.csv"):
    """
    Devuelve un diccionario {col: {"mean":..., "median":..., "std":...}} para columnas numéricas usando pandas.
    """
    import pandas as pd

    df = leer_con_pandas(path)
    numeric = df.select_dtypes(include="number")
    resultado = {}
    if numeric.empty:
        return resultado

    agg = numeric.agg(["mean", "median", "std"]).transpose()
    for col, row in agg.iterrows():
        mean = row["mean"]
        median = row["median"]
        std = row["std"]
        resultado[str(col)] = {
            "mean": None if pd.isna(mean) else float(mean),
            "median": None if pd.isna(median) else float(median),
            "std": None if pd.isna(std) else float(std),
        }
    return resultado


def estadisticas_sin_pandas(path: str | Path = "datos.csv", delimiter: str = ","):
    """
    Devuelve un diccionario {col: {"mean":..., "median":..., "std":...}} sin pandas.
    Intenta parsear valores a float; ignora celdas vacías o no numéricas.
    """
    filas = leer_con_csv(path, delimiter=delimiter)
    if not filas:
        return {}

    columnas = filas[0].keys()
    datos = {col: [] for col in columnas}

    for fila in filas:
        for col in columnas:
            val = fila.get(col, "")
            if val is None:
                continue
            s = str(val).strip()
            if s == "":
                continue
            try:
                num = float(s)
                datos[col].append(num)
            except ValueError:
                continue

    resultado = {}
    for col, vals in datos.items():
        if not vals:
            continue
        mean = statistics.mean(vals)
        median = statistics.median(vals)
        if len(vals) > 1:
            std = statistics.stdev(vals)  # muestra (sample) std
        else:
            std = 0.0
        resultado[str(col)] = {"mean": mean, "median": median, "std": std}
    return resultado


def plot_scatter(path: str | Path = "datos.csv", x: str = "col1", y: str = "col2", delimiter: str = ",", save_path: str | None = None, show: bool = True):
    """
    Traza un scatter plot de las columnas x vs y.
    Usa pandas si está disponible, si no usa el lector CSV interno.
    Requiere matplotlib: python -m pip install matplotlib
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise RuntimeError("matplotlib no está instalado. Ejecuta: python -m pip install matplotlib")

    # intenta con pandas
    try:
        import pandas as pd  # type: ignore
        df = leer_con_pandas(path)
        if x not in df.columns or y not in df.columns:
            raise ValueError(f"Columnas no encontradas en el archivo: {x}, {y}")

        df[x] = pd.to_numeric(df[x], errors="coerce")
        df[y] = pd.to_numeric(df[y], errors="coerce")
        df = df.dropna(subset=[x, y])

        if df.empty:
            raise ValueError("No hay datos numéricos válidos para las columnas solicitadas.")

        plt.figure(figsize=(8, 6))
        plt.scatter(df[x], df[y], s=30, alpha=0.7)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(f"Scatter: {x} vs {y}")
        plt.grid(True)
        if save_path:
            plt.savefig(save_path, bbox_inches="tight")
        if show:
            plt.show()
        plt.close()
        return
    except RuntimeError:
        # pandas no está instalado, continua con el lector csv estándar
        pass

    # sin pandas: leer con csv.DictReader
    filas = leer_con_csv(path, delimiter=delimiter)
    x_vals = []
    y_vals = []
    for fila in filas:
        try:
            xv = fila.get(x, "")
            yv = fila.get(y, "")
            if xv is None or yv is None:
                continue
            xv_s = str(xv).strip()
            yv_s = str(yv).strip()
            if xv_s == "" or yv_s == "":
                continue
            xv_f = float(xv_s)
            yv_f = float(yv_s)
            x_vals.append(xv_f)
            y_vals.append(yv_f)
        except (ValueError, TypeError):
            continue

    if not x_vals:
        raise ValueError("No hay datos numéricos válidos para las columnas solicitadas (sin pandas).")

    plt.figure(figsize=(8, 6))
    plt.scatter(x_vals, y_vals, s=30, alpha=0.7)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f"Scatter: {x} vs {y}")
    plt.grid(True)
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()


def _guardar_json(data, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _pregunta_si_guardar():
    resp = input("¿Deseas guardar el resultado en un archivo JSON? (ruta o Enter para no): ").strip()
    return resp if resp else None


def main_menu(ruta_default: str = "datos.csv"):
    ruta = ruta_default
    while True:
        print("\nMenú:")
        print("1) Calcular estadísticas (usando pandas si está disponible)")
        print("2) Calcular estadísticas (sin pandas)")
        print("3) Trazar scatter (col1 vs col2 por defecto)")
        print("4) Cambiar ruta de datos (actual: {})".format(ruta))
        print("5) Salir")
        opcion = input("Elige una opción (1-5): ").strip()

        if opcion == "1" or opcion == "2":
            try:
                if opcion == "1":
                    stats = estadisticas_con_pandas(ruta)
                else:
                    stats = estadisticas_sin_pandas(ruta)
            except Exception as e:
                print(f"Error al calcular estadísticas: {e}")
                continue

            if not stats:
                print("No se encontraron columnas numéricas.")
                continue

            accion = input("Mostrar en pantalla (m), guardar JSON (g) o solo calcular sin mostrar (n)? [m/g/n]: ").strip().lower()
            if accion == "m":
                for col, s in stats.items():
                    print(f"{col}: mean={s['mean']}, median={s['median']}, std={s['std']}")
            elif accion == "g":
                path_guardado = _pregunta_si_guardar() or f"estadisticas_{'pandas' if opcion=='1' else 'sin_pandas'}.json"
                try:
                    _guardar_json(stats, path_guardado)
                    print(f"Guardado en: {path_guardado}")
                except Exception as e:
                    print(f"Error al guardar: {e}")
            else:
                print("Cálculo realizado. No se muestran resultados.")

        elif opcion == "3":
            x = input("Columna X (por defecto 'x'): ").strip() or "col1"
            y = input("Columna Y (por defecto 'y'): ").strip() or "col2"
            save_path = input("Ruta para guardar imagen (o Enter para no guardar): ").strip() or None
            mostrar = input("Mostrar gráfica en pantalla? (s/n) [s]: ").strip().lower() or "s"
            try:
                plot_scatter(ruta, x=x, y=y, save_path=save_path, show=(mostrar == "s"))
                print("Scatter generado.")
            except Exception as e:
                print(f"Error al trazar scatter: {e}")

        elif opcion == "4":
            nueva = input("Ingresa la nueva ruta del archivo CSV: ").strip()
            if nueva:
                ruta = nueva
                print(f"Ruta actualizada a: {ruta}")
            else:
                print("Ruta no cambiada.")

        elif opcion == "5":
            print("Saliendo.")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main_menu("datos.csv")