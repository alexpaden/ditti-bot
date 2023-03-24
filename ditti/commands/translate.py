from farcaster import Warpcast
from farcaster.models import Parent
from google.cloud import translate

from ditti.commands.text2img import Text2Img


class TranslatorBotCommand:
    def __init__(self, fcc: Warpcast, gtc: translate.TranslationServiceClient):
        self.fcc = fcc
        self.gtc = gtc
        self.t2i = Text2Img()

    location = "global"
    project_id = "ditti-bot"
    parent = f"projects/{project_id}/locations/{location}"

    # Will break if a parent is deleted, but that's a problem for another day
    def start_translate(self, call_cast):
        if call_cast.parent_hash is None:
            lang = self.get_lang(call_cast.text)
            translated_text = self.translate(
                text=call_cast.text, src_lang=lang, target_lang="en"
            )
            imgur_link = self.t2i.convert(
                translated_text, color="grey", image_file="hello.png"
            )
            final_t_cast = (
                "@{0} requested this cast be translated to English: {1}".format(
                    call_cast.author.username, imgur_link
                )
            )
            parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
            return final_t_cast, parent
        else:
            call_parent = self.fcc.get_cast(call_cast.parent_hash)
            author = call_parent.cast.author.username
            parent_hash = call_parent.cast.hash
            full_text = ""
            if parent_hash is None:
                full_text = f"{call_parent.cast.text}\n\n"
            last_parent_hash = parent_hash
            while parent_hash:
                parent_cast = self.fcc.get_cast(parent_hash)
                if parent_cast.cast.author.username == author:
                    full_text = f"{parent_cast.cast.text}\n\n" + full_text
                    last_parent_hash = parent_hash
                    parent_hash = parent_cast.cast.parent_hash or ""
                else:
                    break
            lang = self.get_lang(full_text)
            translated_text = self.translate(
                text=full_text, src_lang=lang, target_lang="en"
            )
            imgur_link = self.t2i.convert(
                translated_text, color="grey", image_file="hello.png"
            )
            final_t_cast = (
                "@{0} requested this cast be translated to English: {1}".format(
                    call_cast.author.username, imgur_link
                )
            )
            parent_cast = self.fcc.get_cast(hash=last_parent_hash)
            parent = Parent(fid=parent_cast.cast.author.fid, hash=last_parent_hash)
            return final_t_cast, parent

    def get_lang(self, text: str):
        response = self.gtc.detect_language(
            content=text,
            parent=self.parent,
            mime_type="text/plain",
        )
        return response.languages[0].language_code

    def translate(self, text: str, src_lang: str, target_lang: str = "en"):
        translation = self.gtc.translate_text(
            request={
                "contents": [text],
                "mime_type": "text/plain",
                "parent": self.parent,
                "source_language_code": src_lang,
                "target_language_code": target_lang,
            }
        )
        return translation.translations[0].translated_text
