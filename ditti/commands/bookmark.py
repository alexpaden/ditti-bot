import logging
import re

from farcaster import Warpcast
from farcaster.models import Parent


class Bookmark:
    TITLE_PATTERN = r"@ditti\sbookmark(.*?)(?:—|--)\s*tag|(?:@ditti\sbookmark\s)(.*)"
    TAG_PATTERN = r"(?:—|--)\s*tag\s(\w+)"

    def __init__(self, fcc: Warpcast, supabase):
        self.fcc = fcc
        self.supabase = supabase

    def start_bookmark(self, call_cast):
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)

        parsed_command = self.parse_bookmark_command(call_cast.text)
        if parsed_command["title"] is None:
            return (
                "Please provide a title for your bookmark. "
                "`@ditti bookmark <title text> --tag <category>`",
                parent,
            )

        text = self.save_to_supabase(parsed_command, call_cast)

        return text, parent

    def parse_bookmark_command(self, call_text):
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
        tag = tag_match.group(1) if tag_match else None

        return {"title": title, "tag": tag}

    def save_to_supabase(self, parsed_command, call_cast):
        try:
            # Check if the unique pairing of owner_fid and saved_hash exists
            query = (
                self.supabase.table("bookmark")
                .select("id")
                .match(
                    {
                        "saved_hash": call_cast.parent_hash,
                        "owner_fid": call_cast.author.fid,
                    }
                )
            )
            existing_entry = query.execute()

            if len(existing_entry.data) > 0:
                # Update the title and tag if an entry exists
                (
                    self.supabase.table("bookmark")
                    .update(
                        {"title": parsed_command["title"], "tag": parsed_command["tag"]}
                    )
                    .match(
                        {
                            "saved_hash": call_cast.parent_hash,
                            "owner_fid": call_cast.author.fid,
                        }
                    )
                    .execute()
                )
            else:
                # Insert a new entry if it does not already exist
                (
                    self.supabase.table("bookmark")
                    .insert(
                        {
                            "owner_fid": call_cast.author.fid,
                            "saved_hash": call_cast.parent_hash,
                            "title": parsed_command["title"],
                            "tag": parsed_command["tag"],
                        }
                    )
                    .execute()
                )

            cast_response = (
                f"'{parsed_command['title']}' was saved to your bookmarks! 🔖"
            )
            trim_length = len(cast_response) - 300
            if trim_length > 0:
                cast_response = (
                    f"'{parsed_command['title'][:-trim_length-3]}...'"
                    + " was saved to your bookmarks! 🔖"
                )

            return cast_response
        except Exception as e:
            logging.error(e)
