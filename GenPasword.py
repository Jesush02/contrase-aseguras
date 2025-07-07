import random

def generar_contraseña(longitud=12):
    caracteres = "qwertyuiopasdfghjklñzxcvbnmQWERTYUIOPASDFGHJKLÑZXCVBNM1234567890!@#$%&*()_+-=[];,.<>?/"
    contraseña = "".join(random.choice(caracteres) for i in range(longitud))
    return contraseña

# Ejemplo de uso
if __name__ == "__main__":
    longitud = int(input("Introduce la longitud de la contraseña: "))
    etiqueta = input("¿Que nombre le quieres dar a la contraseña?...")
    contraseña = generar_contraseña(longitud)
    print(f"Contraseña para {etiqueta} es: {contraseña}")
    
    # Guardar la contraseña etiquetada en un archivo .txt
    with open("contraseñas.txt", "a") as archivo:  # El 'a' es para agregar al archivo sin sobrescribir
        archivo.write(f"{etiqueta} contraseña: {contraseña}\n")  # Escribe la etiqueta y la contraseña en una nueva línea
    
    print(f"🎉Contraseña generada con éxito.🎉")
    print("\nNo olvides guardarla en un lugar seguro.")
    input("Pulsa enter para cerrar el programa..")
