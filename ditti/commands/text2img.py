import base64
import os
import re
import urllib
from io import BytesIO

import emoji
import requests
from bs4 import BeautifulSoup, Comment
from PIL import Image, ImageDraw, ImageFont


class Text2Img:
    def __init__(self):
        pass

    RGB_TO_COLOR_NAMES = {
        (0, 0, 0): ["Black"],
        (255, 255, 255): ["White"],
    }

    COLOR_NAME_TO_RGB = dict(
        (name.lower(), rgb)
        for rgb, names in RGB_TO_COLOR_NAMES.items()
        for name in names
    )

    def remove_urls(self, text: str) -> str:
        url_pattern = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|"
            r"[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        return url_pattern.sub("", text)

    def get_bionic_reading_formatted_text(self, text: str):
        text = emoji.replace_emoji(text, replace="")
        text = self.remove_urls(text)
        api_key = os.getenv("BIONIC_KEY")
        url = "https://bionic-reading1.p.rapidapi.com/convert"
        content = urllib.parse.quote(text)
        payload = (
            f"content={content}&response_type=html&request_type=html&"
            f"fixation=1&saccade=10"
        )
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "bionic-reading1.p.rapidapi.com",
        }

        response = requests.post(url, data=payload, headers=headers)  # type: ignore

        if response.status_code == 200:
            return response.text
        else:
            raise ValueError("Failed to fetch Bionic Reading formatted text.")

    def convert(
        self,
        text: str,
        font_size=25,
        color="black",
        image_file=None,
        padding=100,
        desired_width=2000,
    ):
        text_2 = self.get_bionic_reading_formatted_text(text)
        text_3 = self.extract_html(text_2)

        # Load two font files
        font_name_regular = "./ditti/helpers/fonts/SourceSansPro-Light.ttf"
        font_name_bold = "./ditti/helpers/fonts/SourceSansPro-Regular.ttf"
        font_regular = ImageFont.truetype(font_name_regular, font_size)
        font_bold = ImageFont.truetype(font_name_bold, font_size)

        # Wrap the text
        wrapped_text = self.wrap_text(text_3, font_bold, desired_width)

        # Create the image
        w, h = self.get_multiline_text_size(wrapped_text, font_regular, font_bold)
        image = Image.new(
            "RGBA", (w + 2 * padding, int(h + h * 0.1) + 2 * padding), (255, 255, 255)
        )
        draw = ImageDraw.Draw(image)

        # Set the color
        if color not in self.COLOR_NAME_TO_RGB.keys():
            color = "black"

        # Draw the text
        current_x, current_y = padding, padding  # Add padding to starting position
        for line in wrapped_text.split("\n"):
            line_parts = re.split(r"(<b>|</b>)", line)
            use_bold = False  # Initialize use_bold variable
            for part in line_parts:
                if part == "<b>":
                    use_bold = True
                elif part == "</b>":
                    use_bold = False
                else:
                    font = font_bold if use_bold else font_regular
                    draw.text((current_x, current_y), part, fill=color, font=font)
                    current_x += font.getsize(part)[0]

            current_y += font_regular.getsize(" ")[1]  # Move to next line
            current_x = padding  # Reset x position to include padding

        # Save the image
        if image_file is None:
            filename = text.replace(" ", "")
            image_file = "{}.png".format(filename)

        result = self.upload_imgur(image=image)
        print(text_3)
        print(result)
        return result

    def get_multiline_text_size(self, text, font_regular, font_bold):
        max_w = 0
        total_h = 0
        for line in text.split("\n"):
            line_parts = re.split(r"(<b>|</b>)", line)
            line_w = 0
            use_bold = False
            for part in line_parts:
                if part == "<b>":
                    use_bold = True
                elif part == "</b>":
                    use_bold = False
                else:
                    font = font_bold if use_bold else font_regular
                    line_w += font.getsize(part)[0]
            max_w = max(max_w, line_w)
            total_h += font_regular.getsize(" ")[1]

        return max_w, total_h

    def extract_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find("div", {"class": "bionic-reader-container"})
        footer = container.find("div", {"class": "br-foot-node"})
        if footer:
            footer.extract()

        for comment in container.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        container_str = str(container)
        container_str = container_str.replace(
            '<div class="bionic-reader-container">', ""
        )
        container_str = container_str.replace("</div>", "")
        container_str = container_str.replace("<b></b>", "")
        container_str = container_str.replace("&amp;", "&")
        container_str = container_str.replace("<br/>", "\n")

        soup = BeautifulSoup(container_str, "html.parser")
        bold_tags = soup.find_all("b")
        text = ""
        last_index = 0
        for tag in bold_tags:
            start_index = container_str.find(str(tag), last_index)
            text += container_str[last_index:start_index] + "<b>" + tag.string + "</b>"
            last_index = start_index + len(str(tag))
        text += container_str[last_index:]
        return text

    def wrap_text(self, text, font, max_width):
        text_lines = []
        text_line: list[str] = []
        text = text.replace("\n", " [br] ")
        words = text.split()
        new_string: str = """"""

        for word in words:
            if word == "[br]":
                text_lines.append(" ".join(text_line))
                text_line = []
                continue

            # Calculate the width of the line with the new word added
            new_line_width = font.getsize(" ".join(text_line + [word]))[0]

            if new_line_width > max_width:
                text_lines.append(" ".join(text_line))
                text_line = [word]
            else:
                text_line.append(word)

        if len(text_line) > 0:
            text_lines.append(" ".join(text_line))

        for i, line in enumerate(text_lines):
            new_string += f"{line}\n"

        return new_string

    def upload_imgur(self, image) -> str:
        client_id = os.getenv("IMGUR_CLIENT")
        headers = {"Authorization": "Client-ID {}".format(client_id)}
        api_key = os.getenv("IMGUR_SECRET")
        url = "https://api.imgur.com/3/upload.json"

        img_file = BytesIO()
        assert image is not None
        image.save(img_file, "PNG")
        img_file.seek(0)
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        post_result = requests.post(
            url,
            headers=headers,
            data={
                "key": api_key,
                "image": img_base64,
                "type": "base64",
            },
        )
        return post_result.json()["data"]["link"]
