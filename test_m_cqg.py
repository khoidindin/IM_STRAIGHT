import asyncio
from cqg_client import CQGWebsocketClient

endpoints = [
    ("wss://m.cqg.com:443", "CQGDesktop"),
    ("wss://m.cqg.com/webapi", "CQGDesktop"),
    ("wss://md.cqg.com:443", "CQGDesktop"),
    ("wss://mpt.cqg.com:443", "CQGDesktop"),
    ("wss://api.cqg.com:443", "CQGDesktopWeb"),
    ("wss://api.cqg.com:443", "CQGDesktop_Web"),
    ("wss://api.cqg.com:443", "CQGMobile"),
    ("wss://api.cqg.com:443", "CQGMD"),
    ("wss://api.cqg.com:443", "CQG_M"),
]

async def test_endpoints():
    for host, app_id in endpoints:
        print(f"\n--- Testing host={host}, app_id={app_id} ---")
        client = CQGWebsocketClient(
            username="080C4171295",
            password="BillTun@1111",
            host=host,
            client_app_id=app_id
        )
        try:
            await client.connect()
            print(f"!!! SUCCESS with {host} and {app_id} !!!")
            await client.disconnect()
            return
        except Exception as e:
            print(f"Result: {e}")

if __name__ == "__main__":
    asyncio.run(test_endpoints())
