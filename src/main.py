import pandas as pd
import os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
CSV_EMPLEADOS = os.path.join(DATA_DIR, 'empleados.csv')
CSV_SOLICITUDES = os.path.join(DATA_DIR, 'solicitudes.csv')

def cargar_datos():
    """Carga los archivos CSV individuales solucionando problemas de codificación de Excel."""
    try:
        df_empleados = pd.read_csv(CSV_EMPLEADOS, sep=None, engine='python', encoding='utf-8-sig')
        df_solicitudes = pd.read_csv(CSV_SOLICITUDES, sep=None, engine='python', encoding='utf-8-sig')
        
        df_empleados.columns = df_empleados.columns.str.strip()
        df_solicitudes.columns = df_solicitudes.columns.str.strip()

        if 'Legajo' not in df_empleados.columns:
            print(" ALERTA TÉCNICA: Python no encuentra la columna 'Legajo'.")
            print(f"Columnas que leyó el sistema: {df_empleados.columns.tolist()}")
            
        return df_empleados, df_solicitudes
    except Exception as e:
        print(f"Error al cargar los archivos CSV: {e}")
        return None, None

def guardar_datos(df_empleados, df_solicitudes):
    """Guarda los cambios por separado en cada archivo CSV."""
    try:
        df_empleados.to_csv(CSV_EMPLEADOS, index=False)
        df_solicitudes.to_csv(CSV_SOLICITUDES, index=False)
        return True
    except Exception as e:
        print(f"Error al guardar los archivos CSV: {e}")
        return False

def simulador_bot():
    print("BIENVENIDO AL ASISTENTE DE DISTRISUR LOGÍSTICA")
    print("Sistema de Gestión de Vacaciones")
    
    df_empleados, df_solicitudes = cargar_datos()
    if df_empleados is None:
        return

    # ESTADO: VALIDANDO LEGAJO
    empleado_encontrado = None
    while True:
        try:
            legajo_input = input("Por favor, ingrese su número de Legajo (o 'salir'): ").strip()
            if legajo_input.lower() == 'salir':
                print("Muchas gracias por usar el asistente")
                return
            
            legajo = int(legajo_input)
            fila = df_empleados[df_empleados['Legajo'] == legajo]
            
            if fila.empty:
                print("El legajo ingresado no pertenece a la organización. Intente nuevamente.")
            else:
                empleado_encontrado = fila.iloc[0]
                break
        except ValueError:
            print("Entrada inválida. El legajo debe ser un número entero (ej: 1002).")

    print(f"Empleado Identificado: {empleado_encontrado['Nombre']}")
    print(f"Puesto: {empleado_encontrado['Puesto']} | Área: {empleado_encontrado['Área']}")
    print(f"Saldo de días disponibles: {empleado_encontrado['Días_Disponibles']} días.")

    # ESTADO: SOLICITANDO DÍAS
    saldo_actual = int(empleado_encontrado['Días_Disponibles'])
    
    if saldo_actual <= 0:
        print("Usted no posee días disponibles de vacaciones. El proceso ha finalizado.")
        return

    días_solicitados = 0
    while True:
        try:
            días_input = input(f"¿Cuántos días desea solicitar? (Máximo {saldo_actual}): ").strip()
            días_solicitados = int(días_input)
            if días_solicitados <= 0:
                print("La cantidad de días debe ser mayor a 0.")
            elif días_solicitados > saldo_actual:
                print(f"Saldo insuficiente. Está solicitando {días_solicitados} días, pero solo dispone de {saldo_actual}.")
            else:
                break
        except ValueError:
            print("Entrada inválida. Por favor introduzca un número entero")

    # ESTADO: SOLICITANDO FECHA 
    fecha_inicio = ""
    while True:
        fecha_input = input("Ingrese la fecha de inicio (Formato: AAAA-MM-DD, ej: 2026-10-15): ").strip()
        try:
            datetime.strptime(fecha_input, "%Y-%m-%d")
            fecha_inicio = fecha_input
            break
        except ValueError:
            print("Formato de fecha incorrecto. Debe respetar el formato AAAA-MM-DD.")

    # ESTADO: ESPERANDO APROBACIÓN DEL SUPERVISOR
    supervisor = empleado_encontrado['Supervisor']
    print(f"Solicitud registrada con éxito.")
    print(f"Notificando de manera automatizada al supervisor: [{supervisor}]")
    print("PANTALLA DEL SUPERVISOR ")
    print(f"Solicitante: {empleado_encontrado['Nombre']}")
    print(f"Detalle: {días_solicitados} días a partir de la fecha {fecha_inicio}.")
    
    decision = ""
    while decision not in ['S', 'N']:
        decision = input(f"[{supervisor}] ¿Aprueba esta solicitud? (S/N): ").strip().upper()
        if decision not in ['S', 'N']:
            print("Opción inválida. Presione 'S' para Aprobar o 'N' para Rechazar.")


    # PROCESAMIENTO FINAL E INTEGRACIÓN DE DATOS
    if decision == 'S':
        estado_final = "Aprobado"
        print(f"Solicitud APROBADA por {supervisor}!")
        print(f"Se han descontado {días_solicitados} días de su saldo.")
        
        # Modificar el saldo en el DataFrame de Empleados
        df_empleados.loc[df_empleados['Legajo'] == legajo, 'Días_Disponibles'] = saldo_actual - días_solicitados
    else:
        estado_final = "Rechazado"
        print(f"Solicitud RECHAZADA por {supervisor} debido a necesidades operativas.")

    # Registrar la transacción en solicitudes.csv
    nueva_solicitud_id = len(df_solicitudes) + 1
    nueva_fila = {
        'ID_Solicitud': nueva_solicitud_id,
        'Legajo': legajo,
        'Empleado': empleado_encontrado['Nombre'],
        'Fecha_Inicio': fecha_inicio,
        'Días_Solicitados': días_solicitados,
        'Estado': estado_final
    }
    
    df_solicitudes = pd.concat([df_solicitudes, pd.DataFrame([nueva_fila])], ignore_index=False)

    # Persistencia: Guardar de vuelta en los archivos CSV correspondientes
    if guardar_datos(df_empleados, df_solicitudes):
        print("Archivos de DistriSur actualizados correctamente en la carpeta 'data'.")
        
        print(" PANTALLA DEL SOLICITANTE ")
        print(f"NOTIFICACIÓN ENVIADA A: {empleado_encontrado['Nombre']} (Legajo {legajo})")
        if estado_final == "Aprobado":
            print(f" Hola {empleado_encontrado['Nombre']}, tu solicitud de vacaciones por {días_solicitados} días")
            print(f"   a partir del {fecha_inicio} ha sido aprobada por tu supervisor [{supervisor}].")
            print(f"   Tu nuevo saldo disponible es de {saldo_actual - días_solicitados} días.")
        else:
            print(f"Hola {empleado_encontrado['Nombre']}, te informamos que tu solicitud de vacaciones")
            print(f" para el {fecha_inicio} ha sido rechazada por tu supervisor [{supervisor}].")
            print(f"Tu saldo se mantiene en {saldo_actual} días disponibles.")
    else:
        print("Ocurrió un problema al guardar los datos.")

    print("El proceso ha finalizado de punta a punta de acuerdo al flujo estandarizado.")

if __name__ == "__main__":
    simulador_bot()