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


def hide_message(image_bytes: bytes, message: str) -> bytes:
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


def reveal_message(image_bytes: bytes) -> str:
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