import logging
import re
from farcaster import Warpcast
from farcaster.models import Parent


class Cut:
    TITLE_PATTERN = r"@ditti\scut(.*?)(?:—|--)\s*tag|(?:@ditti\scut\s)(.*)"
    TAG_PATTERN = r"(?:—|--)\s*tag\s(\w+)"
    IMG_URL_PATTERN = r"https://i.imgur.com/(\w+\.\w+)"



    def __init__(self, fcc: Warpcast, supabase, DEV_MODE):
        self.fcc = fcc
        self.supabase = supabase
        self.DEV_MODE = DEV_MODE

    def start_cut(self, call_cast):
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
        parent_cast = self.fcc.get_cast(call_cast.parent_hash).cast
        
        parsed = self.parse_cut_command(call_cast.text)
        logging.info(parsed)
        
        img_urls = self.extract_img_urls(parent_cast.text)
        if not img_urls:
            return "No images found in parent cast", parent
        
        img_url = img_urls[0]
        print(img_url)
        
        if self.DEV_MODE is False:
            self.save_to_supabase(parsed, call_cast, img_url)
            
        text= ""
        return text, parent

    def parse_cut_command(self, call_text):
        title_match = re.search(self.TITLE_PATTERN, call_text)
        tag_match = re.search(self.TAG_PATTERN, call_text)

        title = (
            title_match.group(1).strip()
            if title_match and title_match.group(1)
            else (
                title_match.group(2).strip()
                if title_match and title_match.group(2)
                else None
            )
        )

        if title == "":
            title = None

        tag = tag_match.group(1) if tag_match else None

        return {"title": title, "tag": tag}

    def extract_img_urls(self, parent_text):
        img_urls = re.findall(self.IMG_URL_PATTERN, parent_text)
        img_urls = [f"https://i.imgur.com/{link}" for link in img_urls]
        return img_urls
    
    def save_to_supabase(self, parsed_command, call_cast, img_url):
        try:
            table = self.supabase.table("cut")
            result = table.select("*").eq("parent_hash", call_cast.parent_hash).eq("owner_fid", call_cast.author.fid).execute()
            
            if not result.data:
                table.insert({"parent_hash": call_cast.parent_hash, "owner_fid": call_cast.author.fid, "title": parsed_command["title"], "tag": parsed_command["tag"], "img_url": img_url}).execute()
            else:
                table.update({"title": parsed_command["title"], "tag": parsed_command["tag"], "img_url": img_url}).eq("parent_hash", call_cast.parent_hash).eq("owner_fid", call_cast.author.fid).execute()

        except Exception as e:
            logging.error(e)

