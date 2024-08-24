import asyncio

from aiosteam import Steam

steam = Steam("B59856FFDC7B2215EE7F5F26913A5E56")

async def run_async():
    user = await steam.search_user("jeygavrus")
    badges = await user.get_account_public_info()
    print()
if __name__ == '__main__':
    asyncio.run(run_async())