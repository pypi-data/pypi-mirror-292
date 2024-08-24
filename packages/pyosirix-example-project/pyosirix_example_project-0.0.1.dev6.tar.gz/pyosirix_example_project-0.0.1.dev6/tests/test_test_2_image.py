from PIL import Image, ImageDraw
import numpy as np


def test_append_value_to_tuple(text2image_instance):
    t = (1, 2, 3)
    v = 4
    result = text2image_instance.append_value_to_tuple(v, t)
    assert result == (1, 2, 3, 4)


def test_pad_image(text2image_instance):
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    padded_img = text2image_instance.pad_image(img, pad=(10, 10, 20, 20))

    assert padded_img.size == (120, 140)
    assert isinstance(padded_img, Image.Image)


def test_trim_image_no_trim_needed(text2image_instance):
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    trimmed_img = text2image_instance.trim_image(img, bg_color=(255, 255, 255))

    assert trimmed_img.size == (100, 100)
    assert isinstance(trimmed_img, Image.Image)


def test_trim_image_with_trimming(text2image_instance):
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([25, 25, 75, 75], fill=(0, 0, 0))

    trimmed_img = text2image_instance.trim_image(img, bg_color=(255, 255, 255))

    assert trimmed_img.size == (51, 51)
    assert isinstance(trimmed_img, Image.Image)


def test_paste_image_in_image(text2image_instance):
    base_image = Image.new("RGB", (200, 200), color=(255, 255, 255))
    image_to_paste = Image.new("RGB", (50, 50), color=(0, 0, 0))

    result_image = text2image_instance.paste_image_in_image(image_to_paste,
                                                            base_image)

    assert isinstance(result_image, Image.Image)
    assert result_image.size == (200, 200)

    result_array = np.array(result_image)
    assert np.allclose(np.unique(result_array), [0, 255])


def test_paste_text_in_image(text2image_instance):
    base_image = Image.new("RGB", (200, 200), color=(255, 255, 255))
    result_image = text2image_instance.paste_text_in_image("Hello", base_image, scale=0.2)

    assert isinstance(result_image, Image.Image)
    assert result_image.size == (200, 200)


def test_paste_text_in_array(text2image_instance):
    array = np.ones((200, 200, 3), dtype=np.uint8) * 255
    result_array = text2image_instance.paste_text_in_array("Test", array, scale=0.1)

    assert isinstance(result_array, np.ndarray)
    assert result_array.shape == (200, 200, 3)


def test_text_to_image(text2image_instance):
    img = text2image_instance.text_to_image("Test text", font_size=20, mode="RGB",
                                            color=(0, 0, 0))

    assert isinstance(img, Image.Image)
    assert img.size[0] > 0 and img.size[1] > 0  # Ensure the image is not empty
