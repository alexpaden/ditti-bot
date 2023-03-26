from farcaster import Warpcast
from farcaster.models import Parent


class Bookmark:
    def __init__(self, fcc: Warpcast, supabase):
        self.fcc = fcc
        self.supabase = supabase

    def start_bookmark(self, call_cast):
        
        text = "The bookmark command just ran"
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
        return text, parent

