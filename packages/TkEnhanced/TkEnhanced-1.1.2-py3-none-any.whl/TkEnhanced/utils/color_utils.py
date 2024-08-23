# standard libraries:
from typing import Generator, Optional, Union, Tuple
from struct import unpack
from logging import error

# third-party libraries:
from numpy import ndarray, linspace, int64


class ColorUtils:
    @staticmethod
    def clamp(value: Union[int64, int]) -> int:
        value_int: int = int(value)
        clamped_value: int = min(255, value_int)
        return max(0, clamped_value)

    @staticmethod
    def is_character_hex(character: str) -> bool:
        return character.isdigit() or ("a" <= character.lower() <= "f")

    @staticmethod
    def is_hex_code_valid(hex_code: str) -> bool:
        if not hex_code.startswith("#"):
            return False
        hex_characters: str = hex_code[1:]
        return all(ColorUtils.is_character_hex(character) for character in hex_characters)

    @staticmethod
    def convert_hex_to_rgb(hex_code: str) -> Optional[Tuple[int, int, int]]:
        if not ColorUtils.is_hex_code_valid(hex_code):
            error_message: str = "Invalid hex-code: \"{}\".".format(hex_code)
            return error(msg=error_message)
        hex_code_stripped: str = hex_code.lstrip("#")
        byte_data: bytes = bytes.fromhex(hex_code_stripped)
        rgb_values: Tuple[int, int, int] = unpack("BBB", byte_data)
        return rgb_values

    @staticmethod
    def convert_rgb_to_hex(red: int, green: int, blue: int) -> str:
        hex_code: str = "#{:02x}{:02x}{:02x}".format(red, green, blue)
        return hex_code[:7]

    @staticmethod
    def adjust_hex_code(hex_code: str, *, brightness_factor: Optional[float] = 1.) -> str:
        if not ColorUtils.is_hex_code_valid(hex_code):
            error_message: str = "Invalid hex-code: \"{}\".".format(hex_code)
            return error(msg=error_message)
        red, green, blue = ColorUtils.convert_hex_to_rgb(hex_code)
        new_rgb_color: Tuple[int, int, int] = (
            red * brightness_factor,
            green * brightness_factor,
            blue * brightness_factor)
        new_red, new_green, new_blue = map(ColorUtils.clamp, new_rgb_color)
        return ColorUtils.convert_rgb_to_hex(red=new_red, green=new_green, blue=new_blue)

    @staticmethod
    def generate_palette_colors(start_hex_code: str, end_hex_code: str, *, color_amount: Optional[int] = 2) -> Generator[str, None, str]:
        if not ColorUtils.is_hex_code_valid(hex_code=start_hex_code):
            error_message: str = "Invalid start hex-code: \"{}\".".format(start_hex_code)
            return error(msg=error_message)
        if not ColorUtils.is_hex_code_valid(hex_code=end_hex_code):
            error_message: str = "Invalid end hex-code: \"{}\".".format(end_hex_code)
            return error(msg=error_message)
        if color_amount < 2:
            return error(msg="The color amount must be at least 2.")
        start_rgb_values: Tuple[int, int, int] = ColorUtils.convert_hex_to_rgb(start_hex_code)
        end_rgb_values: Tuple[int, int, int] = ColorUtils.convert_hex_to_rgb(end_hex_code)
        interpolated_red: ndarray = linspace(
            start=start_rgb_values[0],
            stop=end_rgb_values[0],
            num=color_amount,
            dtype=int)
        interpolated_green: ndarray = linspace(
            start=start_rgb_values[1],
            stop=end_rgb_values[1],
            num=color_amount,
            dtype=int)
        interpolated_blue: ndarray = linspace(
            start=start_rgb_values[2],
            stop=end_rgb_values[2],
            num=color_amount,
            dtype=int)
        for integer in range(color_amount):
            rgb_values: Tuple[int64, ...] = interpolated_red[integer], interpolated_green[integer], interpolated_blue[integer]
            hex_code: str = ColorUtils.convert_rgb_to_hex(*rgb_values)
            yield hex_code

    @staticmethod
    def is_hex_code_darker(hex_code: str) -> bool:
        if not ColorUtils.is_hex_code_valid(hex_code):
            error_message: str = "Invalid hex-code: \"{}\".".format(hex_code)
            return error(msg=error_message)
        red, green, blue = ColorUtils.convert_hex_to_rgb(hex_code)
        luminance: float = (red * .299 + green * .587 + blue * .114) / 255
        return luminance <= .52
