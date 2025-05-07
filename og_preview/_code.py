from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

WIDTH, HEIGHT = 1200, 630
PADDING = 80
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)
BORDER_COLOR = (255, 255, 255)
BORDER_WIDTH = 8
AVATAR_SIZE = 96
AVATAR_BORDER_THICKNESS = 2

TITLE_FONT_SIZE = 76
DESC_FONT_SIZE = 40
AUTHOR_FONT_SIZE = 36
URL_FONT_SIZE = 30

FONT_DIR = (Path(__file__).parent / '..' / 'fonts').resolve(strict=True)
FONT_TITLE = FONT_DIR / 'Poppins-SemiBold.ttf'
FONT_DESC = FONT_DIR / 'Poppins-Regular.ttf'
FONT_AUTH = FONT_DIR / 'Roboto-Bold.ttf'
FONT_URL = FONT_DIR / 'PTMono-Regular.ttf'

_Path = str | bytes | PathLike[str] | PathLike[bytes]


# --- Create an avatar with a white border and antialiasing ---
def _create_circular_avatar_with_border(*, avatar_path: _Path, avatar_size: int, border_thickness: int) -> (Image,
                                                                                                            Image):
    scale = 4
    full_size = (avatar_size + 2 * border_thickness) * scale
    inner_size = avatar_size * scale

    avatar = Image.open(avatar_path).convert("RGB")
    avatar = ImageOps.fit(avatar, (inner_size, inner_size), method=Image.LANCZOS)

    base = Image.new("RGB", (full_size, full_size), (0, 0, 0))
    draw = ImageDraw.Draw(base)
    draw.ellipse((0, 0, full_size - 1, full_size - 1), fill=(255, 255, 255))

    offset = border_thickness * scale
    mask = Image.new("L", (inner_size, inner_size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, inner_size - 1, inner_size - 1), fill=255)
    base.paste(avatar, (offset, offset), mask)

    total_mask = Image.new("L", (full_size, full_size), 0)
    draw_total_mask = ImageDraw.Draw(total_mask)
    draw_total_mask.ellipse((0, 0, full_size - 1, full_size - 1), fill=255)

    final_size = avatar_size + 2 * border_thickness
    result = base.resize((final_size, final_size), Image.LANCZOS)
    final_mask = total_mask.resize((final_size, final_size), Image.LANCZOS)

    return result, final_mask


@dataclass(slots=True, frozen=True, kw_only=True)
class ArticleInfo:
    title: str
    description: str
    author: str
    url: str
    output_path: _Path


def generate_og_images(*article_infos: ArticleInfo, avatar_path: _Path, logo_path: _Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)

    # Frame
    ImageDraw.Draw(image).rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], outline=BORDER_COLOR, width=BORDER_WIDTH)

    # Add logo
    logo = Image.open(logo_path).convert('RGBA')
    logo_size = (300, 300)
    logo = logo.resize(logo_size, Image.Resampling.LANCZOS)

    # Logo darkening
    enhancer = ImageEnhance.Brightness(logo)
    logo = enhancer.enhance(0.2)

    # Right position
    logo_pos = (WIDTH - logo_size[0] - 60, (HEIGHT - logo_size[1]) // 2)
    image.paste(logo, logo_pos, logo)

    # ======= Circled avatar with antialiasing =======
    avatar_img, avatar_mask = _create_circular_avatar_with_border(
        avatar_path=avatar_path, avatar_size=AVATAR_SIZE, border_thickness=AVATAR_BORDER_THICKNESS
    )
    avatar_pos = (PADDING, HEIGHT - PADDING - avatar_img.height)
    image.paste(avatar_img, avatar_pos, avatar_mask)

    # Fonts
    title_font = ImageFont.truetype(FONT_TITLE, TITLE_FONT_SIZE)
    desc_font = ImageFont.truetype(FONT_DESC, DESC_FONT_SIZE)
    author_font = ImageFont.truetype(FONT_AUTH, AUTHOR_FONT_SIZE)
    url_font = ImageFont.truetype(FONT_URL, URL_FONT_SIZE)

    for article_info in article_infos:
        title = article_info.title
        description = article_info.description
        author = article_info.author
        url = article_info.url
        output_path = article_info.output_path

        copied_image = image.copy()
        draw = ImageDraw.Draw(copied_image)

        # Title
        y = PADDING
        draw.text((PADDING, y), title, font=title_font, fill=TEXT_COLOR)
        y += title_font.getbbox(title)[3] + 40

        # Description
        if description:
            draw.text((PADDING, y), description, font=desc_font, fill=TEXT_COLOR)
            y += desc_font.getbbox(description)[3] + 60

        # Author and link
        text_x = avatar_pos[0] + avatar_img.width + 20
        text_y = avatar_pos[1] + 12
        draw.text((text_x, text_y), author, font=author_font, fill=TEXT_COLOR)
        text_y += author_font.getbbox(author)[3] + 6
        draw.text((text_x, text_y), url, font=url_font, fill=TEXT_COLOR)

        # Saving
        copied_image.save(output_path)
