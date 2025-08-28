import qrcode
import json


def generar_qr(data, nombre_archivo):
    """
    data: dict con la información del usuario
    nombre_archivo: nombre del archivo de salida, ej. 'entrada.png'
    """
    # Convertimos a JSON
    json_data = json.dumps(data, ensure_ascii=False)

    # Creamos QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)

    # Creamos imagen
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(nombre_archivo)
    print(f"QR generado: {nombre_archivo}")


# Ejemplo de uso para host
host_data = {
    "tipo": "host",
    "nombre": "Juan Perez",
    "cedula": "123456789",
    "correo": "juan@email.com",
    "edad": 28,
    "invitados": [{"nombre": "Ana Gomez"}, {"nombre": "Luis Martinez"}],
}
generar_qr(host_data, "entrada_host.png")

# Ejemplo de uso para invitado
invitado_data = {
    "tipo": "invitado",
    "numero": 1,
    "nombre": "Ana Gomez",
    "cedula": "987654321",
    "correo": "ana@email.com",
    "edad": 25,
    "host": {"nombre": "Juan Perez", "cedula": "123456789"},
}
generar_qr(invitado_data, "entrada_invitado.png")
