from ditti.commands.command_manager import Commands


def test_create_givenENS_query(commands: Commands):
    ens_domain = "example.eth"
    query = commands.whois.create_givenENS_query(ens_domain)
    assert "ens:example.eth" in query


def test_create_givenAddress_query(commands: Commands):
    address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    query = commands.whois.create_givenAddress_query(address)
    assert address in query


def test_create_givenUsername_query(commands: Commands):
    username = "example_user"
    query = commands.whois.create_givenUsername_query(username)
    assert "fc_fname:example_user" in query


def test_format_result(commands: Commands):
    result = {
        "Wallet": {
            "identity": "ens:example.eth",
            "addresses": ["0x742d35Cc6634C0532925a3b844Bc454e4438f44e"],
            "socials": [{"userId": "123", "profileName": "example_user"}],
            "domains": [{"name": "example.eth"}],
        }
    }

    formatted_result = commands.whois.format_result(result)
    assert "@example_user is fid 123" in formatted_result
    assert "1. 0x742d35Cc6634C0532925a3b844Bc454e4438f44e" in formatted_result
    assert "1. example.eth" in formatted_result


def test_split_result(commands: Commands):
    formatted_result = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
    split_results = commands.whois.split_result(formatted_result, max_length=15)

    assert len(split_results) == 3
    assert "Line 1\nLine 2" in split_results[0]
    assert "Line 3\nLine 4" in split_results[1]
    assert "Line 5" in split_results[2]
