from farcaster import Warpcast
from farcaster.models import Parent

from ditti.commands.text2img import Text2Img


class Thread:
    def __init__(self, fcc: Warpcast):
        self.fcc = fcc
        self.t2i = Text2Img()

    # Will break if a parent is deleted, but that's a problem for another day
    def start_thread(self, call_cast):
        if call_cast.parent_hash is None:
            thread_text = call_cast.text
            imgur_link = self.t2i.convert(
                thread_text, color="grey", image_file="hello.png"
            )
            final_t_cast = "@{0} requested this cast as an image: {1}".format(
                call_cast.author.username, imgur_link
            )
            parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
            return final_t_cast, parent
        else:
            call_parent = self.fcc.get_cast(call_cast.parent_hash)
            author = call_parent.cast.author.username
            parent_hash = call_parent.cast.hash
            thread_text = ""
            if parent_hash is None:
                thread_text = f"{call_parent.cast.text}\n\n"
            last_parent_hash = parent_hash
            while parent_hash:
                parent_cast = self.fcc.get_cast(parent_hash)
                if parent_cast.cast.author.username == author:
                    thread_text = f"{parent_cast.cast.text}\n\n" + thread_text
                    last_parent_hash = parent_hash
                    parent_hash = parent_cast.cast.parent_hash or ""
                else:
                    break
            imgur_link = self.t2i.convert(
                thread_text, color="grey", image_file="hello.png"
            )
            final_t_cast = "@{0} requested this thread as an image: {1}".format(
                call_cast.author.username, imgur_link
            )
            parent_cast = self.fcc.get_cast(hash=last_parent_hash)
            parent = Parent(fid=parent_cast.cast.author.fid, hash=last_parent_hash)
            return final_t_cast, parent
