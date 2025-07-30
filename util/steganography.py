import numpy as np
from PIL import Image
import io


def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes) or isinstance(data, Image.Image):
        return ''.join([format(i, "08b") for i in data])
    elif isinstance(data, int):
        return format(data, "08b")
    else:
        raise TypeError("Tipo de dato no soportado para conversión a binario.")


def hide_message_image(image_bytes: bytes, message: str) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size

    if img.mode != 'RGB':
        img = img.convert('RGB')

    binary_message = to_bin(message) + '1111111111111110'  # Delimitador para el final del mensaje

    if len(binary_message) > width * height * 3:
        raise ValueError("El mensaje es demasiado largo para esta imagen.")

    data_index = 0
    img_data = img.getdata()

    new_img = Image.new(img.mode, img.size)
    new_img_data = []

    for pixel in img_data:
        if data_index < len(binary_message):
            new_pixel = list(pixel)
            for i in range(3):
                if data_index < len(binary_message):
                    current_bit = int(binary_message[data_index])
                    new_pixel[i] = (new_pixel[i] & ~1) | current_bit
                    data_index += 1
            new_img_data.append(tuple(new_pixel))
        else:
            new_img_data.append(pixel)

    new_img.putdata(new_img_data)

    output_buffer = io.BytesIO()
    new_img.save(output_buffer, format="PNG")
    output_buffer.seek(0)
    return output_buffer.getvalue()


def reveal_message_image(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode != 'RGB':
        img = img.convert('RGB')

    binary_message = ""
    img_data = img.getdata()

    for pixel in img_data:
        for i in range(3):
            binary_message += to_bin(pixel[i])[-1]

            # El delimitador es '1111111111111110' (14 unos y un cero)
            if binary_message[-16:] == '1111111111111110':
                break
        if binary_message[-16:] == '1111111111111110':
            break

    binary_message = binary_message[:-16]

    message = ""
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        message += chr(int(byte, 2))

    return message

def hide_message_in_frames(frames: list, message: str) -> list:
    binary_message = to_bin(message) + '1111111111111110'
    data_index = 0
    new_frames = []

    for frame in frames:
        if data_index >= len(binary_message):
            new_frames.append(frame)
            continue

        frame_copy = np.copy(frame)
        height, width, _ = frame_copy.shape
        for y in range(height):
            for x in range(width):
                if data_index >= len(binary_message):
                    break
                r, g, b = frame_copy[y, x]
                for i in range(3):
                    #TODO ESTA ACA PERO NO SE XDDDD
                    if data_index < len(binary_message):
                        bit = int(binary_message[data_index])
                        if i == 0:
                            frame_copy[y, x, 0] = (r & ~1) | bit
                        elif i == 1:
                            frame_copy[y, x, 1] = (g & ~1) | bit
                        else:
                            frame_copy[y, x, 2] = (b & ~1) | bit
                        data_index += 1
                    print("BP4")
            if data_index >= len(binary_message):
                break
        new_frames.append(frame_copy)
    return new_frames

def reveal_message_from_frames(frames: list) -> str:
    binary_message = ""
    found_delimiter = False
    for frame in frames:
        height, width, _ = frame.shape
        for y in range(height):
            for x in range(width):
                r, g, b = frame[y, x]
                for channel_val in [r, g, b]:
                    binary_message += to_bin(channel_val)[-1]
                    if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
                        found_delimiter = True
                        break
                if found_delimiter:
                    break
            if found_delimiter:
                break
        if found_delimiter:
            break

    if found_delimiter:
        binary_message = binary_message[:-16]
        message = ""
        try:
            for i in range(0, len(binary_message), 8):
                byte = binary_message[i:i+8]
                message += chr(int(byte, 2))
            return message
        except ValueError:
            return ""
    return ""