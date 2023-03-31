import logging
import re

from farcaster import Warpcast
from farcaster.models import Parent
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

logging.getLogger("gql").setLevel(logging.WARNING)


class WhoIs:
    def __init__(self, fcc: Warpcast):
        self.fcc = fcc
        self.client = self.setup_graphql_client()

    def setup_graphql_client(self):
        url = "https://api.airstack.xyz/gql"
        transport = AIOHTTPTransport(url=url)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        return client

    def create_givenENS_query(self, ens_domain):
        return f"""
        query {{
            Wallet(input: {{identity: "ens:{ens_domain}"}}) {{
                identity
                addresses
                socials {{
                    userId
                    profileName
                }}
                domains {{
                    name
                }}
            }}
        }}
        """

    def create_givenAddress_query(self, address):
        return f"""
        query {{
            Wallet(input: {{identity: "{address}"}}) {{
                identity
                addresses
                socials {{
                    userId
                    profileName
                }}
                domains {{
                    name
                }}
            }}
        }}
        """

    def create_givenUsername_query(self, username):
        return f"""
        query {{
            Wallet(input: {{identity: "fc_fname:{username}"}}) {{
                identity
                addresses
                socials {{
                    userId
                    profileName
                }}
                domains {{
                    name
                }}
            }}
        }}
        """

    def execute_query(self, query):
        result = self.client.execute(query)
        return result

    def format_result(self, result):
        wallet = result["Wallet"]
        profile_name = wallet["socials"][0]["profileName"]
        user_id = wallet["socials"][0]["userId"]
        addresses = wallet["addresses"]
        domains = wallet["domains"]

        formatted_result = f"@{profile_name} is fid {user_id}\n\n"
        formatted_result += f"They have {len(addresses)} connected addresses\n"

        for i, address in enumerate(addresses, start=1):
            formatted_result += f"{i}. {address}\n"

        formatted_result += f"\nand {len(domains)} web3 domains\n"

        for i, domain in enumerate(domains, start=1):
            formatted_result += f"{i}. {domain['name']}\n"

        return formatted_result

    def split_result(self, formatted_result, max_length=320):
        lines = formatted_result.split("\n")
        split_results = []
        current_result = ""

        for line in lines:
            if len(current_result) + len(line) + 1 > max_length:
                split_results.append(current_result.strip())
                current_result = ""

            current_result += f"{line}\n"

        if current_result.strip():
            split_results.append(current_result.strip())

        return split_results

    def start_whois(self, call_cast):
        parent = Parent(fid=call_cast.author.fid, hash=call_cast.hash)
        pattern = r"@ditti whois (@[\w.-]+|[0-9a-fA-F]{40}|[\w.-]+\.eth)"
        match = re.search(pattern, call_cast.text, re.IGNORECASE)
        if match:
            word = match.group(1)
            if word.startswith("@"):
                query_givenUsername = gql(self.create_givenUsername_query(word[1:]))
                res = self.execute_query(query_givenUsername)
                formatted_result = self.format_result(res)
            elif word.endswith(".eth"):
                query_givenENS = gql(self.create_givenENS_query(word))
                res = self.execute_query(query_givenENS)
                formatted_result = self.format_result(res)
            elif word.startswith("0x"):
                query_givenAddress = gql(self.create_givenAddress_query(word))
                res = self.execute_query(query_givenAddress)
                formatted_result = self.format_result(res)
            else:
                formatted_result = "The input does not match any of the cases."
        else:
            if call_cast.parent_hash:
                try:
                    parent_cast = self.fcc.get_cast(call_cast.parent_hash).cast
                except Exception as e:
                    logging.error(f"Error while getting parent cast whois: {e}")
                parent_user = self.fcc.get_user(parent_cast.author.fid)
                query_givenUsername = gql(
                    self.create_givenUsername_query(parent_user.username)
                )
                res = self.execute_query(query_givenUsername)
                formatted_result = self.format_result(res)
            else:
                text = (
                    "An error occurred. Are you providing a username,"
                    "ENS, address, or replying to someone?"
                )
                return text, parent

        formatted_result = self.split_result(formatted_result)
        return formatted_result, parent
