import cv2
import numpy as np
import flet as ft
import asyncio
import requests
import socket
from utils.database import guardar_ip, obtener_ips, eliminar_ip


def leer_codigo_qr(camera_url):
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


def main(page: ft.Page):
    page.title = "Qr Invitation"
    page.window.icon = "src/assets/icon.png"

    page.window.min_height = 426
    page.window.min_width = 240
    page.window.height = 640
    page.window.width = 360
    page.window.max_height = 1080
    page.window.max_width = 720

    page.bgcolor = ft.Colors.BLACK12
    page.padding = 0
    page.vertical_alignment = ft.alignment.top_center
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    # Variables para control
    camera_active = False

    # Texto fijo y dinámico
    titulo_datos = ft.Text("DATOS ESCANEADOS", size=18, color=ft.Colors.WHITE)
    action_text = ft.Text(
        "Configura la IP de la cámara", size=16, color=ft.Colors.WHITE
    )

    # Campo para configurar IP
    ip_field = ft.TextField(
        label="IP de la cámara (ej: 192.168.0.1:8080)",
        value="",
        width=page.window.width,
        color=ft.Colors.WHITE,
    )

    def seleccionar_ip(e):
        if ip_dropdown.value:
            ip_field.value = ip_dropdown.value
            ip_field.update()

    def actualizar_ip():
        ips = obtener_ips()
        ip_dropdown.options = [ft.dropdown.Option(ip) for ip in ips]
        if ip_dropdown in page.controls:
            ip_dropdown.update()

    # Dropdown de ips guardadas
    ip_dropdown = ft.Dropdown(
        label="IPs Guardadas",
        width=page.window.width,
        options=[],
        on_change=seleccionar_ip,
        bgcolor=ft.Colors.GREY_800,
        color=ft.Colors.GREEN,
    )

    def get_device_ip():
        """Obtener la IP del dispositivo actual"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "No disponible"

    async def escanea_qr():
        """Tarea asíncrona para escanear QR"""
        nonlocal camera_active

        camera_ip = ip_field.value.strip()
        if not camera_ip:
            action_text.value = "❌ Ingresa la IP de la cámara"
            page.update()
            return

        if not camera_ip.startswith("http"):
            camera_url = f"http://{camera_ip}/video"
        else:
            camera_url = f"{camera_ip}/video"

        # Verificar conexión
        try:
            response = requests.get(camera_url.replace("/video", ""), timeout=5)
            if response.status_code != 200:
                action_text.value = f"❌ No se puede conectar a {camera_ip}"
                page.update()
                return
        except Exception as e:
            action_text.value = f"❌ Error conectando: {str(e)}"
            page.update()
            return

        action_text.value = "📡 Conectando a cámara..."
        page.update()

        # Escanear QR en bucle
        while camera_active:
            try:
                codigo = await asyncio.to_thread(leer_codigo_qr, camera_url)
                if codigo:
                    action_text.value = f"✅ {codigo}"
                    camera_active = False
                    page.update()
                    break
            except Exception as e:
                action_text.value = f"❌ Error: {str(e)}"
                page.update()
                break

    def start_camera():
        """Iniciar cámara"""
        nonlocal camera_active
        camera_active = True
        page.run_task(escanea_qr)

    def stop_camera():
        """Detener cámara"""
        nonlocal camera_active
        camera_active = False

    def scan_click(e):
        """Click del botón escanear"""
        if not camera_active:
            start_camera()
        else:
            stop_camera()
            action_text.value = "Cámara detenida"
            action_text.update()

    def auto_detect_ip(e):
        """Auto-detectar IP del dispositivo"""
        device_ip = get_device_ip()
        if device_ip != "No disponible":
            ip_parts = device_ip.split(".")
            ip_parts[-1] = "100"
            suggested_ip = ".".join(ip_parts) + ":8080"
            ip_field.value = suggested_ip
            ip_field.update()
            action_text.value = f"IP sugerida: {suggested_ip}"
        else:
            action_text.value = "No se pudo detectar IP automáticamente"
        action_text.update()

    async def save_ip_prompt(e):
        success = guardar_ip(ip_field.value)
        if success:
            save_message.value = f"✅ IP {ip_field.value} guardada correctamente"
            actualizar_ip()
        else:
            save_message.value = f"❌ Error al guardar la IP: {ip_field.value}"
        page.update()

    async def eliminar_ip_seleccionada(e):
        selected_ip = ip_dropdown.value
        if not selected_ip:
            save_message.value = "❌ Selecciona una IP para eliminar"
            page.update()
            return

        # Intentar eliminar la IP directamente
        eliminado = eliminar_ip(selected_ip)
        if eliminado:
            save_message.value = f"✅ IP {selected_ip} eliminada correctamente"
            actualizar_ip()
            # Limpiar el campo si estaba mostrando la IP eliminada
            ip_dropdown.update()
            ip_field.update()
            page.update()

            if ip_field.value == selected_ip:
                ip_field.value = ""
                ip_field.update()
                ip_dropdown.update()
            # Limpiar selección del dropdown
            elif ip_field.value != selected_ip:
                ip_dropdown.value = None
                ip_dropdown.update()
                page.update()

            ip_dropdown.value = None
            ip_dropdown.update()
            page.update()
        else:
            save_message.value = f"❌ Error al eliminar la IP: {selected_ip}"

        page.update()

    # Resto de la interfaz de usuario (igual que antes)
    custom_scan_button = ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    name=ft.Icons.QR_CODE_2_OUTLINED, size=80, color=ft.Colors.WHITE
                ),
                ft.Text(
                    "ESCANEAR" if not camera_active else "DETENER",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    style=ft.TextStyle(font_family="monospace"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=200,
        height=150,
        bgcolor=ft.Colors.GREEN_900 if not camera_active else ft.Colors.RED_900,
        border_radius=10,
        alignment=ft.alignment.center,
        ink=True,
        on_click=scan_click,
    )

    ip_button_autodetect = ft.OutlinedButton(
        "Auto-detectar",
        width=page.window.width,
        on_click=auto_detect_ip,
    )

    ip_button_save = ft.ElevatedButton(
        text="Guardar",
        bgcolor=ft.Colors.GREEN_600,
        color=ft.Colors.WHITE,
        expand=True,
        on_click=save_ip_prompt,
    )

    ip_button_delete = ft.ElevatedButton(
        text="Eliminar",
        bgcolor=ft.Colors.RED_600,
        color=ft.Colors.WHITE,
        expand=True,
        on_click=eliminar_ip_seleccionada,
    )

    save_message = ft.Text(
        "",
        size=12,
        color=ft.Colors.WHITE70,
    )

    # Logica Login
    # if superuser == "admin" and password == "admin":

    form_login = ft.Container(
        content=ft.Column(
            [
                ft.Text("USUARIO", size=24, font_family="monospace"),
                ft.TextField(
                    value="",
                    bgcolor=ft.Colors.BLACK38,
                    hint_text="SANTIAGO@SANTACRUZ...",
                    color=ft.Colors.WHITE70,
                    border_radius=24,
                    border_color=ft.Colors.GREEN_900,
                    focused_border_color=ft.Colors.CYAN_900,
                ),
                ft.Text("PASSWORD", size=24),
                ft.TextField(
                    value="",
                    bgcolor=ft.Colors.BLACK38,
                    hint_text="123456789",
                    color=ft.Colors.WHITE70,
                    border_radius=24,
                    border_color=ft.Colors.GREEN_900,
                    focused_border_color=ft.Colors.CYAN_900,
                ),
                ft.ElevatedButton(
                    "INGRESAR",
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                    icon=ft.Icons.LOGIN_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    width=150,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.GREY_800,
        margin=ft.margin.only(left=20, right=20, top=20),
        padding=ft.padding.only(left=20, right=20, top=30, bottom=30),
        alignment=ft.alignment.center,
        border_radius=16,
    )
    admin_people = ft.Container(
        content=ft.Column(
            [form_login],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
        expand=True,
        bgcolor="#121212",
    )

    config_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("Configuración de Cámara IP", size=16, color=ft.Colors.WHITE),
                ip_field,
                ip_dropdown,
                ft.Row(
                    [ip_button_delete, ip_button_save],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ip_button_autodetect,
                save_message,
                ft.Container(
                    ft.Text(
                        f"IP del dispositivo: {get_device_ip()}",
                        size=12,
                        color=ft.Colors.WHITE70,
                    ),
                    alignment=ft.alignment.bottom_center,
                    expand=True,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.GREY_900,
        padding=ft.padding.only(top=20, bottom=10, left=10, right=10),
        expand=True,
    )

    action_button = ft.Container(
        content=ft.Column(
            [
                titulo_datos,
                action_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        margin=20,
        alignment=ft.alignment.top_center,
        bgcolor=ft.Colors.GREY_800,
        padding=ft.padding.only(top=20, bottom=20),
        expand=True,
    )

    body_scanner = ft.Column(
        [
            ft.Container(
                custom_scan_button,
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=25),
            ),
            action_button,
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        scroll=ft.ScrollMode.AUTO,
    )

    navbar = ft.Container(
        ft.Tabs(
            selected_index=0,
            animation_duration=300,
            indicator_color=ft.Colors.GREEN,
            label_color=ft.Colors.GREEN_600,
            divider_color=ft.Colors.TRANSPARENT,
            unselected_label_color=ft.Colors.WHITE38,
            enable_feedback=True,
            tabs=[
                ft.Tab(
                    text="SCANER",
                    icon=ft.Icons.QR_CODE_SCANNER_ROUNDED,
                    content=ft.Column(
                        [
                            ft.Container(
                                content=body_scanner,
                                bgcolor="#121212",
                                expand=True,
                                alignment=ft.alignment.top_center,
                            ),
                        ]
                    ),
                ),
                ft.Tab(
                    text="PERSONAS",
                    icon=ft.Icons.PERSON_PIN,
                    content=ft.Container(
                        content=admin_people,
                        bgcolor="#121212",
                        expand=True,
                        alignment=ft.alignment.top_center,
                        height=page.window.height,
                    ),
                ),
                ft.Tab(
                    text="OPCIONES",
                    icon=ft.Icons.SETTINGS,
                    content=ft.Container(
                        content=config_container,
                        bgcolor="#121212",
                        expand=True,
                        alignment=ft.alignment.top_center,
                    ),
                ),
            ],
            width=page.width,
        ),
        bgcolor=ft.Colors.BLACK,
        padding=ft.padding.only(top=20),
        expand=True,
    )

    actualizar_ip(),
    page.add(navbar)
    page.update()


ft.app(target=main)
