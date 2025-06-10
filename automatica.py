import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
import cv2
import psutil

class CasaAutomatica:
    def __init__(self, root):
        self.root = root
        self.root.title("🏡 Casa Inteligente - Monitoramento em Tempo Real")
        self.root.configure(bg="#f0f0f0")
        self.root.geometry("800x600")

        # Estados
        self.cpu_usage = tk.StringVar(value="Carregando...")
        self.motion_status = tk.StringVar(value="Sem movimento")
        self.ac_status = tk.StringVar(value="DESLIGADO")
        self.light_status = tk.StringVar(value="DESLIGADO")

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        if not self.cap.isOpened():
            print("Não foi possível abrir a webcam. Verifique se está em uso ou conectada.")
            self.webcam_width = 480
            self.webcam_height = 360 
        else:
            self.webcam_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.webcam_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Webcam configurada para: {self.webcam_width}x{self.webcam_height}")

        self.setup_ui()

        threading.Thread(target=self.monitor_system, daemon=True).start()
        threading.Thread(target=self.monitor_motion, daemon=True).start()
        self.update_video()

    def setup_ui(self):
        title = ttk.Label(self.root, text="Simulação de Casa Inteligente", font=("Segoe UI", 20, "bold"))
        title.pack(pady=10)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(pady=10)

        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=0, column=0, padx=10, sticky="nw")

        ttk.Label(info_frame, text="Uso da CPU:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, textvariable=self.cpu_usage).grid(row=0, column=1, sticky="w", pady=2)

        ttk.Label(info_frame, text="Sensor de Movimento:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, textvariable=self.motion_status).grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(info_frame, text="Ar-condicionado:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, textvariable=self.ac_status).grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(info_frame, text="Luz da Sala:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, textvariable=self.light_status).grid(row=3, column=1, sticky="w", pady=2)

        self.canvas = tk.Canvas(main_frame, width=self.webcam_width, height=self.webcam_height, bg="black")
        self.canvas.grid(row=0, column=1, padx=10, sticky="nsew")

    def monitor_system(self):
        while True:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage.set(f"{cpu_percent:.1f}%")

            if cpu_percent > 20:
                self.ac_status.set("LIGADO")
            else:
                self.ac_status.set("DESLIGADO")

            time.sleep(2)

    def monitor_motion(self):
        if not self.cap.isOpened():
            print("Monitoramento de movimento desativado: Webcam não disponível.")
            return

        ret, frame1 = self.cap.read()
        ret, frame2 = self.cap.read()

        while ret and self.cap.isOpened():
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                self.motion_status.set("Movimento Detectado")
                self.light_status.set("LIGADO")
            else:
                self.motion_status.set("Sem movimento")
                self.light_status.set("DESLIGADO")

            frame1 = frame2
            ret, frame2 = self.cap.read()
            time.sleep(0.5)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk
        else:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.webcam_width // 2, self.webcam_height // 2,
                text="Webcam não disponível", fill="white", font=("Segoe UI", 16)
            )
        self.root.after(30, self.update_video)

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

root = tk.Tk()
app = CasaAutomatica(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()