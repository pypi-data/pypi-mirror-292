import os
from typing_extensions import deprecated
from PIL import Image
import layeredimage as layered_image  # type: ignore
from .directory import dir_action

IMAGE_TYPES = (".png", ".jpg", ".gif", ".webp", ".tiff", ".bmp", ".jpe",
               ".jfif", ".jif")

LAYERED_IMAGE_TYPES = (".ora", ".pdn", ".xcf", ".psd")


def resize(path: str, image_width: int, image_height: int):
    """
    Resizes an image or all images in a directory

    Args:
        path (string): path of the image to resize or to a directory that contains them
        image_width (int): width of the desired output image in pixels
        image_height (int): height of the desired output image in pixels

    Returns:
        void
    """

    def resize_single(path):
        if path.endswith(IMAGE_TYPES):
            with Image.open(path) as image:
                image = image.resize(
                    (image_width, image_height),
                    resample=Image.Resampling.NEAREST,
                )
                image.save(path)

    if os.path.isfile(path):
        resize_single(path)

    if os.path.isdir(path):
        dir_action(path, True, resize_single)


def scale(path: str, width_multiplier: float, height_multiplier: float):
    """
    Scales an image or all images in a directory with the given multiplier(s)

    Args:
        path (string): path of the image to scale or to a directory that contains them
        width_multiplier (int): integer that will be used to multiply the width of the image
        height_multiplier (int): integer that will be used to multiply the width of the image

    Returns:
        void
    """

    def scale_single(path):
        if path.endswith(IMAGE_TYPES):
            with Image.open(path) as image:
                image_width, image_height = image.size

                image = image.resize(
                    (int(image_width * width_multiplier),
                     int(image_height * height_multiplier)),
                    resample=Image.Resampling.NEAREST,
                )
                image.save(path)

    if os.path.isfile(path):
        scale_single(path)

    if os.path.isdir(path):
        dir_action(path, True, scale_single)


@deprecated("Use `directory.dir_action` instead")
def dir_scale(dir_path: str, width_multiplier: float, height_multiplier: float):
    """
    Scales every image in a directory and its sub directories.

    Args:
        dir_path (str): path of the directory that will be used
        width_multiplier (int): width of all images is multiplied by this
        height_multiplier (int): height of all images is multiplied by this
    """

    for root, _, files in os.walk(dir_path):
        for file in files:
            print(os.path.join(root, file).replace("\\", "/"))
            scale(os.path.join(root, file), width_multiplier, height_multiplier)


@deprecated("Use `directory.dir_action` instead")
def dir_resize(dir_path: str, image_width: int, image_height: int):
    """
    Resizes every image in a directory and its sub directories.

    Args:
        dir_path (str): path of the directory that will be used
        width_multiplier (int): width of the desired output image in pixels
        height_multiplier (int): height of the desired output image in pixels
    """

    for root, _, files in os.walk(dir_path):
        for file in files:
            print(os.path.join(root, file).replace("\\", "/"))
            resize(os.path.join(root, file), image_width, image_height)


def to_png(path: str):
    """Converts normal image or layered image file into PNG.

    Args:
        path (str): path of the layered image to convert or to a directory that contains them
    """

    def to_png_single(path):
        if path.endswith(".png"):
            return
        filename = os.path.splitext(path)[0]
        if path.endswith(LAYERED_IMAGE_TYPES):
            image = layered_image.openLayerImage(path)
            image.getFlattenLayers().save(f"{filename}.png")
        elif path.endswith(IMAGE_TYPES):
            image = Image.open(path)
            image.save(f"{filename}.png")
            os.remove(path)

    if os.path.isfile(path):
        to_png_single(path)

    if os.path.isdir(path):
        dir_action(path, True, to_png_single)


@deprecated("Use `directory.dir_action` instead")
def dir_to_png(dir_path: str):
    """
    Converts every image or layered image file in a directory and its sub directories into PNG.

    Args:
        dir_path (str): path of the directory that will be used
    """

    for root, _, files in os.walk(dir_path):
        for file in files:
            print(os.path.join(root, file).replace("\\", "/"))
            to_png(os.path.join(root, file))


if __name__ == "__main__":
    home_dir = os.path.expanduser('~')

    resize(f"{home_dir}/Downloads/goat.jpg", 1600, 1600)
    resize(f"{home_dir}/Downloads/giraffes", 44, 66)

    scale(f"{home_dir}/Downloads/fox.png", 2.5, 3.3)
    scale(f"{home_dir}/Downloads/cats", 2, 2)

    to_png(f"{home_dir}/Downloads/chicken.jpg")
    to_png(f"{home_dir}/Downloads/koalas")
