import asyncio

from aiosteam_api import Steam

steam = Steam("B59856FFDC7B2215EE7F5F26913A5E56")

async def some_async_foo():
  user = await steam.search_user("jeygavrus") # also you can use steam user id for searching
  await user.get_all_info()
  await user.owned_games[20920].get_all_info()

  print(user) # list[User]



if __name__ == '__main__':
    asyncio.run(some_async_foo())