#Autor: AvalonTM
#version: 0.0.1
#Tecnológico Nacional de México Campus Ensenada
#Clase de sistemas computacionales 4SS

import time
import sys
import threading

def color(text, color="default"):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "default": "\033[0m"  # Default color
    }
    # Usamos el color especificado o por defecto si no existe el color dado
    color_code = colors.get(color.lower(), "\033[0m")
    return f"{color_code}{text}\033[0m"


# Función para mostrar un indicador de espera
def esperar(mensaje, timer = 0.1):
    print(color(mensaje, "cyan"))
    spinner = ['|', '/', '-', '\\']
    done = False

    def mostrar_spinner():
        while not done:
            for simbolo in spinner:
                sys.stdout.write(f'\r{simbolo}')
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write('\r')  # Limpiar la línea

    spinner_thread = threading.Thread(target=mostrar_spinner)
    spinner_thread.start()

    # Simulando una espera (aquí puedes poner la conexión a la BD)
    time.sleep(timer)
    done = True
    spinner_thread.join()
