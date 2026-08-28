import asyncio
from cqg_client import CQGWebsocketClient
from WebAPI.webapi_2_pb2 import ClientMsg, ServerMsg

async def test_token_only():
    host = "wss://api.cqg.com:443"
    print(f"Connecting to {host} using only Token...")
    
    token = "u4MrC4_3tOc7xHwXt7OtIa9B-sS2ZgA5v7nQlVro-bsRZXBY7QKylOOQv_V9AJuLldBiBz1Edmf"
    fp = "3494ffe7-7753-46de-9e01-b20921aa041c"

    # Test 1: partner_token only
    client = CQGWebsocketClient(
        username="",
        password="",
        host=host,
        client_app_id="CQGDesktop"
    )
    
    async def custom_send_partner():
        client_msg = ClientMsg()
        logon = client_msg.logon
        logon.partner_token = token
        logon.fingerprint = fp
        logon.client_app_id = "CQGDesktop"
        logon.client_version = "python-bridge-v1.0"
        logon.protocol_version_major = 2
        logon.protocol_version_minor = 230
        await client._send_message(client_msg)
        print("Logon with ONLY partner_token sent!")

    client._send_logon = custom_send_partner
    try:
        await client.connect()
        print(">>> SUCCESS WITH PARTNER_TOKEN! <<<")
        info = await client.resolve_symbol("SIEU26")
        print(f"Symbol resolved: {info.symbol} -> {info.contract_id}")
        await client.disconnect()
        return
    except Exception as e:
        print(f"Partner token result: {e}")

    # Test 2: access_token only
    client2 = CQGWebsocketClient(
        username="",
        password="",
        host=host,
        client_app_id="CQGDesktop"
    )
    async def custom_send_access():
        client_msg = ClientMsg()
        logon = client_msg.logon
        logon.access_token = token
        logon.fingerprint = fp
        logon.client_app_id = "CQGDesktop"
        logon.client_version = "python-bridge-v1.0"
        logon.protocol_version_major = 2
        logon.protocol_version_minor = 230
        await client2._send_message(client_msg)
        print("Logon with ONLY access_token sent!")

    client2._send_logon = custom_send_access
    try:
        await client2.connect()
        print(">>> SUCCESS WITH ACCESS_TOKEN! <<<")
        info = await client2.resolve_symbol("SIEU26")
        print(f"Symbol resolved: {info.symbol} -> {info.contract_id}")
        await client2.disconnect()
        return
    except Exception as e:
        print(f"Access token result: {e}")

if __name__ == "__main__":
    asyncio.run(test_token_only())
