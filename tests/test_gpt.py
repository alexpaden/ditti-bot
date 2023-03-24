from farcaster.client import Warpcast

from ditti.commands.command_manager import Commands

# @ditti gpt is this hash different
request1_hash = "0xe6b5ef8e693edd8d5f63ebe1624c8a944856e855640b71867edeee2faaf85f00"
# @ditti gpt ^ can the dao be compared to Minecraft factions
request2_hash = "0xc4c419f2afc175762c829d61b2db13df97ea8db5a2fc3990fd514ea516095094"
# @ditti gpt ^why does this guy not add a space
request3_hash = "0x24bbf203c380c8ebd3df78bde59c6ee2fbcfc9f421ead4d7f92f4fb27b29902c"
# @ditti gpt ^^ can the dao be compared to Minecraft factions
request4_hash = "0xc5dc43cec227b3230f301cbe13a6aa7cc0f8e4deffdc5ed7e3c7715f71152978"
# @ditti gpt ^2 how can a dao in web3 be compared to a Minecraft faction
request5_hash = "0x10b5c03104d082e24b8d50dd58e4de77a52e3bcfc529d157f900ab5c120226b7"
# @ditti gpt ^50 why did the woodchuck chuck
request6_hash = "0xf785121b5599c2f350a92ea231856076a0c0b200767f4154f438954aedb112fa"
# @ditti gpt* ^ can the dao be compared to Minecraft factions
request7_hash = "0x7c042f998f3c1d01da1ab2d6948c1d3a57adffbbfb65c9f0bfce11da314b331f"
# @ditti gpt* ^50 why is red always the winning team
request8_hash = "0xb1066c166725de2687ca94c7d9ea2f94b2b3bd5f08fc26ced32c78649f60cffd"
# @ditti gpt* ask me something about myself
request9_hash = "0x61bc8999aec3ae2537e646019e3393e864a927c52eae14548db10a51bb0c9795"


def test_string_bad_int(commands: Commands):
    test_string = (
        "@ditti gpt ^2d how can a dao in web3 be compared to a Minecraft faction"
    )
    res = commands.gpt.find_integer_after_caret(test_string)
    assert res is -1


def test_gpt_basic(fcc: Warpcast, commands: Commands):
    response = fcc.get_cast(request5_hash).cast
    res = commands.gpt.start_gpt(response)
    assert res is not None
