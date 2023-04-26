import base64
from PIL import Image, ImageEnhance


class PyCodeAsciiArt:
    """
    Creates ASCII Art from Python code based on an image.
    Can make the resulting ascii art executable Python code.
    """

    DEFAULT_PLACEHOLDER: str = '@'
    CHARS_1B: tuple[str] = (DEFAULT_PLACEHOLDER, ' ')
    CHARS_4B: tuple[str] = (DEFAULT_PLACEHOLDER, '*', '.', ' ')

    def __init__(self, img: Image.Image = None, width: int = 70):
        self.img: Image.Image = img
        self.width: int = width
        self.invert: bool = False
        self.add_exec: bool = True
        self.need_fill: bool = False
        self.color_4bit: bool = False
        self.source_text: str = ''
        self.ascii_image: str = ''

    @property
    def img(self) -> Image:
        return self.__img

    @img.setter
    def img(self, value: Image.Image) -> None:
        if not isinstance(value, Image.Image):
            raise TypeError(f'value should be PIL Image. Got {type(value)}')
        self.__img = value

    @property
    def width(self) -> int:
        return self.__width

    @width.setter
    def width(self, value: int) -> None:
        if not isinstance(value, int):
            raise ValueError(f'value should be int. Got {type(value)}')
        if value > 0:
            self.__width = value

    def create_preview(self) -> str:
        """
        Converts the image specified in the 'img' attribute to ascii art using the default characters,
         stores the resulting string in the 'ascii_image' attribute and returns it.
        :return: str
        """

        if self.img is None:
            return ''
        width, height = self.img.size
        aspect_ratio = height / width
        new_width = self.width
        new_height = int(aspect_ratio * new_width * 0.6) or 1
        img = self.img.resize(size=(new_width, new_height))
        img = img.convert('L')

        if not self.color_4bit:  # Enhance image for 1 bit color
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2)
            img = img.convert('1')

        pixels = img.getdata()

        if self.color_4bit:
            chars = self.CHARS_4B if not self.invert else self.CHARS_4B[::-1]
            divisor = 64
        else:
            chars = self.CHARS_1B if not self.invert else self.CHARS_1B[::-1]
            divisor = 255
        new_pixels = ''.join(chars[pixel // divisor] for pixel in pixels)
        new_pixels_count = len(new_pixels)

        crop_left = crop_right = 0
        for i in range(0, new_pixels_count, new_width):
            if (n := len(new_pixels[i:i + new_width].lstrip())) > crop_left:
                crop_left = n
            if (n := len(new_pixels[i:i + new_width].rstrip())) > crop_right:
                crop_right = n

        crop_left = self.width - crop_left

        self.ascii_image = '\n'.join(new_pixels[index:index + new_width][crop_left:crop_right]
                                     for index in range(0, new_pixels_count, new_width)
                                     if new_pixels[index:index + new_width].strip() != '')
        return self.ascii_image

    def create_art(self) -> str:
        """
        Encodes source text (Python code) in base64 format, then generates the resulting ascii image string based
        on the string from ascii_image, replacing DEFAULT_PLACEHOLDER with characters from the base64 string,
        and returns the result as a string.
        :return: str
        """

        if self.ascii_image == '' or self.source_text == '':
            return ''
        b64_str = base64.b64encode(self.source_text.encode()).decode()
        n = 0
        res = '' if not self.add_exec else '"""\n\n'
        for i in self.ascii_image:
            if i != self.DEFAULT_PLACEHOLDER or (n == len(b64_str) and self.need_fill):
                res += i
            else:
                if n < len(b64_str):
                    res += b64_str[n]
                    n += 1
                else:
                    res += ' '
        res += '\n'
        while n < len(b64_str):
            res += '\n' + b64_str[n:n + self.width]
            n += self.width

        if self.add_exec:
            res += '\n"""\nexec(__import__("base64").b64decode(__doc__))'
        return res
