import os

import cv2

# Dimensiones de la imagen a animar
image_size = 64

# Crear la imagen (64x64) que se animará
# image = np.full((image_size, image_size, 3), (0, 255, 0),
#                 dtype=np.uint8)  # Imagen verde de 64x64
ruta_imagen = os.path.join("toasty.jpg")
image = cv2.imread(ruta_imagen)


def update_animation_state(animation_phase, frame_count, animation_speed, pause_frames):
    if animation_phase == 1:  # Intro
        frame_count += animation_speed
        if frame_count >= image_size:
            animation_phase = 2
            frame_count = 0
    elif animation_phase == 2:  # Pausa
        frame_count += 1
        if frame_count >= pause_frames:
            animation_phase = 3
            frame_count = 0
    elif animation_phase == 3:  # Outro
        frame_count += animation_speed
        if frame_count >= image_size:
            animation_phase = 0
            frame_count = 0
    return animation_phase, frame_count


def apply_animation(frame, start_animation, animation_phase, frame_count, image_size):
    if start_animation:
        start_x = frame.shape[1] - image_size
        start_y = frame.shape[0] - image_size

        if animation_phase == 1:  # Intro
            x = frame.shape[1] + image_size - (frame_count + image_size)
            y = start_y
            region_width = min(image_size, frame.shape[1] - x)
            region_height = image_size
            if region_width > 0 and region_height > 0:
                frame[y:y+region_height, x:x +
                      region_width] = image[:region_height, :region_width]

        elif animation_phase == 2:  # Pausa
            x = start_x
            y = start_y
            region_width = image_size
            region_height = image_size
            if x + region_width <= frame.shape[1] and y + region_height <= frame.shape[0]:
                frame[y:y+region_height, x:x+region_width] = image

        elif animation_phase == 3:  # Outro
            x = frame.shape[1] - 128 + (frame_count + image_size)
            y = start_y
            region_width = min(image_size, frame.shape[1] - x)
            region_height = image_size
            if region_width > 0 and region_height > 0:
                frame[y:y+region_height, x:x +
                      region_width] = image[:region_height, :region_width]

    return frame
