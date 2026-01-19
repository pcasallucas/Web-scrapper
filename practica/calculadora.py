def calcular():
    ops = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b,
    }

    while True:
        operacion = input("ingresar operacion (+, -, *, /) o 'salir' para terminar: ").strip().lower()
        if operacion == "salir":
            break
        if operacion not in ops:
            print("operacion no valida")
            continue

        try:
            num1 = float(input("ingresar primer numero: "))
            num2 = float(input("ingresar segundo numero: "))
        except ValueError:
            print("entrada no valida. intenta de nuevo.")
            continue

        try:
            resultado = ops[operacion](num1, num2)
        except ZeroDivisionError:
            print("error: division por cero")
            continue

        print(f"resultado: {resultado}")

if __name__ == "__main__":
    calcular()