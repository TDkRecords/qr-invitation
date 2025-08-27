import cv2
import numpy as np
import flet as ft


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

    # Texto fijo y dinámico
    titulo_datos = ft.Text("DATOS ESCANEADOS", size=18, color=ft.Colors.WHITE)
    action_text = ft.Text("", size=18, color=ft.Colors.WHITE)

    # --- Función para abrir cámara y escanear QR ---
    def scan_click(e):
        action_text.value = "Abriendo cámara..."
        action_text.update()

        cap = cv2.VideoCapture(0)  # 0 = cámara principal
        detector = cv2.QRCodeDetector()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detectar y decodificar QR
            data, bbox, _ = detector.detectAndDecode(frame)
            if data:
                print("QR Detectado:", data)
                action_text.value = f"{data}"
                action_text.update()
                break  # cerrar después de detectar un código válido

            # Mostrar ventana para debug (puedes quitarla si no quieres abrir la cámara)
            cv2.imshow("Escaner QR", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    # Botón personalizado
    custom_scan_button = ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    name=ft.Icons.QR_CODE_2_OUTLINED, size=100, color=ft.Colors.WHITE
                ),
                ft.Text(
                    "ESCANEAR",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    style=ft.TextStyle(font_family="monospace"),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        width=225,
        height=225,
        bgcolor=ft.Colors.GREEN_900,
        border_radius=10,
        alignment=ft.alignment.center,
        ink=True,  # efecto ripple
        on_click=scan_click,
    )

    # Contenedor para datos
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
        margin=30,
        alignment=ft.alignment.top_center,
        bgcolor=ft.Colors.GREY_800,
        padding=ft.padding.only(top=20, bottom=20),
        expand=True,
    )

    # Layout principal
    body_scanner = ft.Column(
        [
            ft.Container(
                custom_scan_button,
                margin=ft.margin.only(top=20),
                alignment=ft.alignment.top_center,
            ),
            action_button,
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        scroll=ft.ScrollMode.HIDDEN,
    )

    # Tabs (navegación)
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
                        ],
                    ),
                ),
                ft.Tab(
                    text="PERSONAS",
                    icon=ft.Icons.PERSON_PIN,
                    content=ft.Container(ft.Text("WAWAWA")),
                ),
            ],
            width=page.width,
        ),
        bgcolor=ft.Colors.BLACK,
        padding=ft.padding.only(top=20),
        expand=True,
    )

    page.add(navbar)
    page.update()


ft.app(target=main)
