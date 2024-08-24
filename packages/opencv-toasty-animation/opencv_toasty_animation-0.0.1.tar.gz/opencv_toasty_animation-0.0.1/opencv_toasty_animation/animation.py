import threading
import time

import cv2
from playsound import playsound
from importlib import resources


class Animation:
    def __init__(self, image_path=None, sound_path=None, animation_speed=15, pause_frames=5, repetition_delay=300):
        # Cargar png con canal alfa
        with resources.path(__package__, 'toasty.png') as img_path:
            self.image = cv2.imread(image_path if image_path else str(img_path), cv2.IMREAD_UNCHANGED)
        with resources.path(__package__, 'toasty.mp3') as snd_path:
            self.sound_path = sound_path if sound_path else str(snd_path)
        self.animation_speed = animation_speed
        self.pause_frames = pause_frames
        self.start_animation = False
        self.animation_phase = 0
        self.frame_count = 0
        self.repetition_delay = repetition_delay
        self.last_execution_time = 0

    def play_sound(self):
        if self.sound_path:
            playsound(self.sound_path)

    def update_animation_state(self):
        if self.animation_phase == 1:  # Intro
            self.frame_count += self.animation_speed
            if self.frame_count >= 64:
                self.animation_phase = 2
                self.frame_count = 0
        elif self.animation_phase == 2:  # Pausa
            self.frame_count += 1
            if self.frame_count >= self.pause_frames:
                self.animation_phase = 3
                self.frame_count = 0
        elif self.animation_phase == 3:  # Outro
            self.frame_count += self.animation_speed
            if self.frame_count >= 64:
                self.animation_phase = 0
                self.frame_count = 0
                self.start_animation = False
        return self.animation_phase, self.frame_count

    def apply_animation(self, frame):
        if self.start_animation:
            start_x = frame.shape[1] - 64
            start_y = frame.shape[0] - 64
            if self.animation_phase == 1:  # Intro
                x = frame.shape[1] + 64 - (self.frame_count + 64)
                y = start_y
                region_width = min(64, frame.shape[1] - x)
                region_height = 64
            elif self.animation_phase == 2:  # Pausa
                x = start_x
                y = start_y
                region_width = 64
                region_height = 64
            elif self.animation_phase == 3:  # Outro
                x = frame.shape[1] - 128 + (self.frame_count + 64)
                y = start_y
                region_width = min(64, frame.shape[1] - x)
                region_height = 64

            # Combinación de la imagen PNG con transparencia sobre el frame
            if region_width > 0 and region_height > 0:
                overlay = self.image[:region_height, :region_width]
                overlay_rgb = overlay[:, :, :3]  # Canal de color
                overlay_alpha = overlay[:, :, 3] / 255.0  # Canal alfa

                # Extraer la región de interés del frame
                frame_region = frame[y:y + region_height, x:x + region_width]

                # Mezclar la imagen PNG con la región del frame
                for c in range(0, 3):
                    frame_region[:, :, c] = (overlay_rgb[:, :, c] * overlay_alpha +
                                             frame_region[:, :, c] * (1 - overlay_alpha))

                # Reemplazar la región en el frame original
                frame[y:y + region_height, x:x + region_width] = frame_region

        return frame

    def start(self, prevent_repetition=False):
        current_time = time.time()
        if prevent_repetition:
            if current_time - self.last_execution_time < self.repetition_delay:
                return
        self.last_execution_time = current_time
        self.start_animation = True
        self.animation_phase = 1
        threading.Thread(target=self.play_sound).start()

    def reset(self):
        self.start_animation = False
        self.animation_phase = 0
        self.frame_count = 0
