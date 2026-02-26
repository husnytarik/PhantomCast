import cv2
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import threading
import time
from PIL import Image, ImageTk
from pynput.keyboard import Controller, Key
import math
import mediapipe as mp

# --- DYNAMIC PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "camwork_settings_v8_5.json")


class GestureApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.keyboard = Controller()

        self.current_frame = None
        self.is_running = False
        self.stop_threads = False

        # Lock mechanisms
        self.locks = {
            "mouth": False,
            "left_hand_macro": False,
            "left_rock": False,
            "right_rock": False,
            "eye_blink": False,
        }
        self.active_keys = set()

        # HUD Status Information
        self.hud_status = {
            "Left Hand": "Passive",
            "Right Hand": "Passive",
            "Mouth": "Closed",
            "Eye": "Open",
            "Left Rock": "No",
            "Right Rock": "No",
        }

        # --- PARAMETERS ---
        self.vars = {
            "threshold_mouth": tk.DoubleVar(value=0.20),
            "threshold_eye": tk.DoubleVar(value=0.02),
            "threshold_left_tilt_left": tk.DoubleVar(value=20.0),
            "threshold_left_tilt_right": tk.DoubleVar(value=20.0),
            "threshold_right_tilt_left": tk.DoubleVar(value=20.0),
            "threshold_right_tilt_right": tk.DoubleVar(value=20.0),
            "threshold_left_spread": tk.DoubleVar(value=0.085),
            "threshold_right_gas_brake": tk.DoubleVar(value=0.045),
            "threshold_rock_sens": tk.DoubleVar(value=0.05),
            # Key Assignments
            "key_mouth": tk.StringVar(value="g, end"),
            "key_eye": tk.StringVar(value="g"),
            "key_left_rock": tk.StringVar(value="alt+caps_lock"),
            "key_right_rock": tk.StringVar(value="r"),
            "key_left_spread": tk.StringVar(value="'"),
            "key_left_closed": tk.StringVar(value="tab"),
            "key_left_tilt_l": tk.StringVar(value="ctrl+tab"),
            "key_left_tilt_r": tk.StringVar(value="e"),
            "key_right_forward": tk.StringVar(value="w"),
            "key_right_backward": tk.StringVar(value="s"),
            "key_right_left": tk.StringVar(value="a"),
            "key_right_right": tk.StringVar(value="d"),
        }

        self.load_settings()
        self.vid = cv2.VideoCapture(0)

        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.mp_hands = mp.solutions.hands.Hands(
            max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7
        )
        self.mp_face = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

        self.setup_ui()

        self.cam_thread = threading.Thread(target=self.video_capture_loop, daemon=True)
        self.logic_thread = threading.Thread(
            target=self.logic_processing_loop, daemon=True
        )
        self.cam_thread.start()
        self.logic_thread.start()

        self.update_canvas()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if k in self.vars:
                            self.vars[k].set(v)
            except:
                pass

    def save_settings(self):
        data = {k: v.get() for k, v in self.vars.items()}
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
        messagebox.showinfo("PhantomCast", "Settings Saved Successfully!")

    def setup_ui(self):
        # --- CAMERA UI ---
        self.canvas = tk.Canvas(self.window, width=640, height=360, bg="#111")
        self.canvas.pack(side=tk.TOP, pady=10)

        # --- SETTINGS PANEL ---
        container = ttk.Frame(self.window)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas_scroll = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=self.canvas_scroll.yview
        )

        self.panel = ttk.Frame(self.canvas_scroll, padding=10)

        self.window_item = self.canvas_scroll.create_window(
            (320, 0), window=self.panel, anchor="n"
        )

        def on_configure(event):
            self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))

            canvas_width = event.width
            self.canvas_scroll.itemconfig(self.window_item, width=canvas_width - 20)
            self.canvas_scroll.coords(self.window_item, canvas_width / 2, 0)

        self.canvas_scroll.bind("<Configure>", on_configure)
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Button(
            self.panel,
            text="💾 SAVE ALL SETTINGS",
            command=self.save_settings,
            bg="#34495e",
            fg="white",
            font=("Arial", 9, "bold"),
        ).pack(fill=tk.X, pady=5)

        ttk.Label(
            self.panel, text="--- FACE SENSITIVITY ---", font=("Arial", 8, "bold")
        ).pack(pady=5)
        self.create_slider("😮 Mouth Opening", self.vars["threshold_mouth"], 0.05, 0.40)
        self.create_slider(
            "😉 Eye Blink Sens.", self.vars["threshold_eye"], 0.005, 0.05
        )

        ttk.Label(
            self.panel,
            text="--- TILT (DEGREE) THRESHOLDS ---",
            font=("Arial", 8, "bold"),
        ).pack(pady=5)
        self.create_slider(
            "⬅️ Left Hand / Tilt Left", self.vars["threshold_left_tilt_left"], 5, 60
        )
        self.create_slider(
            "➡️ Left Hand / Tilt Right", self.vars["threshold_left_tilt_right"], 5, 60
        )
        self.create_slider(
            "⬅️ Right Hand / Tilt Left", self.vars["threshold_right_tilt_left"], 5, 60
        )
        self.create_slider(
            "➡️ Right Hand / Tilt Right", self.vars["threshold_right_tilt_right"], 5, 60
        )

        ttk.Label(
            self.panel, text="--- HAND & ROCK GESTURE ---", font=("Arial", 8, "bold")
        ).pack(pady=5)
        self.create_slider(
            "🖐️ Left Finger Spread Gap", self.vars["threshold_left_spread"], 0.04, 0.15
        )
        self.create_slider(
            "⛽ Right Gas/Brake Sens.",
            self.vars["threshold_right_gas_brake"],
            0.02,
            0.10,
        )
        self.create_slider(
            "🤘 Rock Gesture Sens.", self.vars["threshold_rock_sens"], 0.01, 0.15
        )

        ttk.Separator(self.panel, orient="horizontal").pack(fill=tk.X, pady=10)
        ttk.Label(
            self.panel, text="--- KEY ASSIGNMENTS ---", font=("Arial", 8, "bold")
        ).pack(pady=5)

        self.create_input("😮 Mouth Macro", self.vars["key_mouth"])
        self.create_input("😉 Eye Blink Key", self.vars["key_eye"])
        self.create_input("🤘 Left Hand ROCK", self.vars["key_left_rock"])
        self.create_input("🤘 Right Hand ROCK", self.vars["key_right_rock"])
        self.create_input("⬅️ Left Tilt Left Key", self.vars["key_left_tilt_l"])
        self.create_input("➡️ Left Tilt Right Key", self.vars["key_left_tilt_r"])
        self.create_input("🖐️ Left Spread Key", self.vars["key_left_spread"])
        self.create_input("✊ Left Closed Key", self.vars["key_left_closed"])

        # Movement Keys Grid
        w_f = ttk.Frame(self.panel)
        w_f.pack(fill=tk.X, pady=5)
        self.create_input(
            "FORWARD (W)", self.vars["key_right_forward"], parent=w_f, side=tk.LEFT
        )
        self.create_input(
            "BACK (S)", self.vars["key_right_backward"], parent=w_f, side=tk.LEFT
        )
        self.create_input(
            "LEFT (A)", self.vars["key_right_left"], parent=w_f, side=tk.LEFT
        )
        self.create_input(
            "RIGHT (D)", self.vars["key_right_right"], parent=w_f, side=tk.LEFT
        )

        self.btn_toggle = tk.Button(
            self.panel,
            text="START SYSTEM",
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.toggle_system,
            height=2,
        )
        self.btn_toggle.pack(fill=tk.X, pady=15)

    def update_canvas(self):
        if self.current_frame is not None:
            display_frame = cv2.resize(self.current_frame, (640, 360))

            overlay = display_frame.copy()
            cv2.rectangle(overlay, (5, 5), (280, 180), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.4, display_frame, 0.6, 0, display_frame)

            y = 25
            for label, status in self.hud_status.items():
                cv2.putText(
                    display_frame,
                    f"{label}: {status}",
                    (15, y),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.4,
                    (255, 255, 255),
                    1,
                )
                y += 22

            status_text = "ACTIVE KEYS: " + " + ".join(list(self.active_keys))
            cv2.putText(
                display_frame,
                status_text,
                (15, 345),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                2,
            )

            img = Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(320, 180, image=self.photo)
        self.window.after(15, self.update_canvas)

    def create_slider(self, text, var, start, end):
        f = ttk.Frame(self.panel)
        f.pack(fill=tk.X)
        ttk.Label(f, text=text, font=("Arial", 7)).pack(anchor=tk.W)
        ttk.Scale(f, from_=start, to=end, variable=var, orient=tk.HORIZONTAL).pack(
            fill=tk.X
        )

    def create_input(self, text, var, parent=None, side=tk.TOP):
        target = parent if parent else self.panel
        f = ttk.Frame(target)
        f.pack(side=side, fill=tk.X, expand=True)
        ttk.Label(f, text=text, font=("Arial", 7)).pack(anchor=tk.W)
        ttk.Entry(f, textvariable=var, font=("Arial", 8)).pack(fill=tk.X)

    def video_capture_loop(self):
        while not self.stop_threads:
            ret, frame = self.vid.read()
            if ret:
                self.current_frame = cv2.flip(frame, 1)
            time.sleep(0.01)

    def is_rock_gesture(self, lm):
        # Index (8) and Pinky (20) must be UP
        # Middle (12) and Ring (16) must be DOWN
        index_up = lm[8].y < lm[6].y
        pinky_up = lm[20].y < lm[18].y
        middle_down = lm[12].y > lm[10].y
        ring_down = lm[16].y > lm[14].y
        return index_up and pinky_up and middle_down and ring_down

    def logic_processing_loop(self):
        while not self.stop_threads:
            if self.is_running and self.current_frame is not None:
                rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                hand_res = self.mp_hands.process(rgb)
                face_res = self.mp_face.process(rgb)

                # --- FACE LOGIC ---
                if face_res.multi_face_landmarks:
                    m = face_res.multi_face_landmarks[0].landmark
                    mouth_ratio = abs(m[13].y - m[14].y) / abs(m[10].y - m[152].y)
                    if mouth_ratio > self.vars["threshold_mouth"].get():
                        self.hud_status["Mouth"] = "OPEN"
                        if not self.locks["mouth"]:
                            for s in self.vars["key_mouth"].get().split(","):
                                self.handle_keys(s.strip(), True)
                                self.handle_keys(s.strip(), False)
                            self.locks["mouth"] = True
                    else:
                        self.hud_status["Mouth"] = "Closed"
                        self.locks["mouth"] = False

                    avg_eye_gap = (
                        abs(m[159].y - m[145].y) + abs(m[386].y - m[374].y)
                    ) / 2
                    if avg_eye_gap < self.vars["threshold_eye"].get():
                        self.hud_status["Eye"] = "BLINK"
                        if not self.locks["eye_blink"]:
                            for s in self.vars["key_eye"].get().split(","):
                                self.handle_keys(s.strip(), True)
                                self.handle_keys(s.strip(), False)
                            self.locks["eye_blink"] = True
                    else:
                        self.hud_status["Eye"] = "Open"
                        self.locks["eye_blink"] = False

                # --- HAND LOGIC ---
                active_this_frame = {"Left": False, "Right": False}
                if hand_res.multi_hand_landmarks:
                    for idx, hand_lms in enumerate(hand_res.multi_hand_landmarks):
                        side = hand_res.multi_handedness[idx].classification[0].label
                        lm = hand_lms.landmark
                        angle = math.degrees(
                            math.atan2(lm[9].x - lm[0].x, -(lm[9].y - lm[0].y))
                        )
                        active_this_frame[side] = True

                        if side == "Left":
                            # Left Hand Tilt
                            l_tilt_l = self.vars["threshold_left_tilt_left"].get()
                            l_tilt_r = self.vars["threshold_left_tilt_right"].get()
                            if angle < -l_tilt_l:
                                self.handle_keys(
                                    self.vars["key_left_tilt_l"].get(), True
                                )
                                self.handle_keys(
                                    self.vars["key_left_tilt_r"].get(), False
                                )
                                self.hud_status["Left Hand"] = f"LEFT ({int(angle)}°)"
                            elif angle > l_tilt_r:
                                self.handle_keys(
                                    self.vars["key_left_tilt_r"].get(), True
                                )
                                self.handle_keys(
                                    self.vars["key_left_tilt_l"].get(), False
                                )
                                self.hud_status["Left Hand"] = f"RIGHT ({int(angle)}°)"
                            else:
                                self.handle_keys(
                                    self.vars["key_left_tilt_l"].get(), False
                                )
                                self.handle_keys(
                                    self.vars["key_left_tilt_r"].get(), False
                                )
                                self.hud_status["Left Hand"] = "CENTER"

                            # ROCK GESTURE (Left)
                            if self.is_rock_gesture(lm):
                                self.hud_status["Left Rock"] = "YES 🤘"
                                if not self.locks["left_rock"]:
                                    for s in (
                                        self.vars["key_left_rock"].get().split(",")
                                    ):
                                        self.handle_keys(s.strip(), True)
                                        self.handle_keys(s.strip(), False)
                                    self.locks["left_rock"] = True
                            else:
                                self.hud_status["Left Rock"] = "No"
                                self.locks["left_rock"] = False

                            # Finger Macro (Spread/Closed)
                            f_up = sum([lm[i].y < lm[i - 2].y for i in [8, 12, 16, 20]])
                            if f_up >= 3:
                                gap = math.sqrt(
                                    (lm[8].x - lm[12].x) ** 2
                                    + (lm[8].y - lm[12].y) ** 2
                                )
                                if not self.locks["left_hand_macro"]:
                                    m_str = (
                                        self.vars["key_left_spread"].get()
                                        if gap
                                        > self.vars["threshold_left_spread"].get()
                                        else self.vars["key_left_closed"].get()
                                    )
                                    for s in m_str.split(","):
                                        self.handle_keys(s.strip(), True)
                                        self.handle_keys(s.strip(), False)
                                    self.locks["left_hand_macro"] = True
                            else:
                                self.locks["left_hand_macro"] = False

                        elif side == "Right":
                            # Right Hand Tilt
                            r_tilt_l = self.vars["threshold_right_tilt_left"].get()
                            r_tilt_r = self.vars["threshold_right_tilt_right"].get()
                            if angle < -r_tilt_l:
                                self.handle_keys(
                                    self.vars["key_right_left"].get(), True
                                )
                                self.handle_keys(
                                    self.vars["key_right_right"].get(), False
                                )
                                self.hud_status["Right Hand"] = f"LEFT ({int(angle)}°)"
                            elif angle > r_tilt_r:
                                self.handle_keys(
                                    self.vars["key_right_right"].get(), True
                                )
                                self.handle_keys(
                                    self.vars["key_right_left"].get(), False
                                )
                                self.hud_status["Right Hand"] = f"RIGHT ({int(angle)}°)"
                            else:
                                self.handle_keys(
                                    self.vars["key_right_left"].get(), False
                                )
                                self.handle_keys(
                                    self.vars["key_right_right"].get(), False
                                )
                                self.hud_status["Right Hand"] = "CENTER"

                            # ROCK GESTURE (Right)
                            if self.is_rock_gesture(lm):
                                self.hud_status["Right Rock"] = "YES 🤘"
                                if not self.locks["right_rock"]:
                                    for s in (
                                        self.vars["key_right_rock"].get().split(",")
                                    ):
                                        self.handle_keys(s.strip(), True)
                                        self.handle_keys(s.strip(), False)
                                    self.locks["right_rock"] = True
                            else:
                                self.hud_status["Right Rock"] = "No"
                                self.locks["right_rock"] = False

                            # Gas/Brake (Gap based)
                            gap_ws = math.sqrt(
                                (lm[8].x - lm[12].x) ** 2 + (lm[8].y - lm[12].y) ** 2
                            )
                            if (
                                sum([lm[i].y < lm[i - 2].y for i in [8, 12, 16, 20]])
                                >= 3
                            ):
                                if (
                                    gap_ws
                                    > self.vars["threshold_right_gas_brake"].get()
                                ):
                                    self.handle_keys(
                                        self.vars["key_right_forward"].get(), True
                                    )
                                    self.handle_keys(
                                        self.vars["key_right_backward"].get(), False
                                    )
                                else:
                                    self.handle_keys(
                                        self.vars["key_right_backward"].get(), True
                                    )
                                    self.handle_keys(
                                        self.vars["key_right_forward"].get(), False
                                    )
                            else:
                                self.handle_keys(
                                    self.vars["key_right_forward"].get(), False
                                )
                                self.handle_keys(
                                    self.vars["key_right_backward"].get(), False
                                )

                if not active_this_frame["Left"]:
                    self.hud_status["Left Hand"] = "Passive"
                    self.hud_status["Left Rock"] = "Passive"
                if not active_this_frame["Right"]:
                    self.hud_status["Right Hand"] = "Passive"
                    self.hud_status["Right Rock"] = "Passive"

            time.sleep(0.01)

    def handle_keys(self, key_str, press=True):
        if not key_str:
            return
        for combo in key_str.split(","):
            parts = combo.strip().replace(" ", "").split("+")
            keys = []
            for p in parts:
                p = p.lower()
                # Expanded special keys mapping
                spec = {
                    "ctrl": Key.ctrl,
                    "shift": Key.shift,
                    "alt": Key.alt,
                    "tab": Key.tab,
                    "space": Key.space,
                    "end": Key.end,
                    "caps_lock": Key.caps_lock,
                    "capslock": Key.caps_lock,
                    "esc": Key.esc,
                    "enter": Key.enter,
                }
                keys.append(spec.get(p, p))

            target = keys if press else reversed(keys)
            for k in target:
                try:
                    if press:
                        self.keyboard.press(k)
                        self.active_keys.add(str(k).replace("Key.", "").upper())
                    else:
                        self.keyboard.release(k)
                        kn = str(k).replace("Key.", "").upper()
                        if kn in self.active_keys:
                            self.active_keys.remove(kn)
                except:
                    pass

    def toggle_system(self):
        self.is_running = not self.is_running
        self.btn_toggle.config(
            text="STOP SYSTEM" if self.is_running else "START SYSTEM",
            bg="#c0392b" if self.is_running else "#27ae60",
        )
        if not self.is_running:
            self.release_all()
            self.active_keys.clear()

    def release_all(self):
        # Emergency release for all possible mapped keys
        keys = [
            Key.ctrl,
            Key.shift,
            Key.alt,
            Key.tab,
            Key.space,
            Key.end,
            Key.caps_lock,
            "w",
            "a",
            "s",
            "d",
            "e",
            "g",
            "f",
            "r",
            "'",
        ]
        for k in keys:
            try:
                self.keyboard.release(k)
            except:
                pass

    def on_closing(self):
        self.stop_threads = True
        self.vid.release()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("640x640")
    app = GestureApp(root, "PhantomCast v1.0")
    root.mainloop()
