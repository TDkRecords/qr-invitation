import cv2
import asyncio
import requests


def leer_codigo_qr(camera_url: str):
    """Función bloqueante para leer código QR desde la cámara IP"""
    cap = cv2.VideoCapture(camera_url)
    detector = cv2.QRCodeDetector()

    if not cap.isOpened():
        return None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            cap.release()
            return data


async def escanear_qr(camera_url: str, action_callback, stop_flag):
    """Función asíncrona para escanear QR con feedback"""
    try:
        # Verificar conexión
        response = requests.get(camera_url.replace("/video", ""), timeout=5)
        if response.status_code != 200:
            action_callback(f"❌ No se puede conectar a {camera_url}")
            return
    except Exception as e:
        action_callback(f"❌ Error conectando: {str(e)}")
        return

    action_callback("📡 Conectando a cámara...")

    while stop_flag["active"]:
        try:
            codigo = await asyncio.to_thread(leer_codigo_qr, camera_url)
            if codigo:
                action_callback(f"✅ {codigo}")
                stop_flag["active"] = False
                break
        except Exception as e:
            action_callback(f"❌ Error: {str(e)}")
            break
