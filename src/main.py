import os

# Función para buscar empleados por legajos
def buscar_empleado(legajo):
    # Apertura del archivo de empleados en modo lectura
    with open("../data/empleados.csv", "r", encoding="utf-8") as archivo:

        # Saltea el encabezado
        next(archivo) 

        # Recorrido de cada registro del archivo
        for linea in archivo:
            # Separación de los campos del registro
            datos = linea.strip().split(";")

            # Comparación del legajo ingresado con el legajo almacenado
            if datos[0] == legajo:
                return datos

    # Retorna None si el legajo no existe
    return None

# Solicitud del número de legajo
legajo = input("Ingrese su legajo: ")

# Búsqueda del empleado en la base de datos
empleado = buscar_empleado(legajo)

# Validación de existencia del empleado
if empleado is None:
    print("ERROR: Legajo inexistente.")
else:
    # Muestra información del empleado
    print(f"Bienvenido {empleado[1]}")
    print(f"Días disponibles: {empleado[5]}")

    # Solicitud de la cantidad de días de vacaciones
    while True:
        try:
            dias_solicitados = int(input("¿Cuántos días desea solicitar?: "))
                # Control de números negativos o cero
            if dias_solicitados <= 0:
                print("ERROR: Debe ingresar una cantidad mayor a cero.")
                continue
            break
        except ValueError:
            print("ERROR: Debe ingresar un número entero.")

    # Validación de saldo disponible
    if dias_solicitados > int(empleado[5]):
        print("ERROR: Saldo insuficiente.")
    else:
        print("Solicitud registrada correctamente.")