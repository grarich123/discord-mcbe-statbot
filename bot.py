import config
import discord
import time
import gc
import concurrent.futures
from discord.ext import commands, tasks

import mcipc.query

startedFlag = False

bot = commands.Bot(command_prefix=config.prefix, intents=discord.Intents.default())

def ssu_coproc():
  status = None
  
  try:
    pt = time.time()
    with mcipc.query.Client(config.host, config.port) as mcbe:
      status = mcbe.stats(full=True)
      ping = (time.time()-pt)*1000
    del mcbe
    gc.collect()
      
  except:
    asyncio.create_task(bot.change_presence(status=discord.Status.dnd, activity=discord.Game('サーバーがオフラインです')))
    return
  
  st = f'{status.num_players} / {status.max_players} | ping: {ping:.1f}ms'
  asyncio.create_task(bot.change_presence(status=discord.Status.online, activity=discord.Game(st)))

@tasks.loop(seconds=30)
async def server_status_updater():
  
  with concurrent.futures.ProcessPoolExecutor() as pool:
    bot.loop.run_until_complete(loop.run_in_executor(pool, ssu_coproc))

@bot.event
async def on_ready():
  global startedFlag
  
  if startedFlag:
   return

  startedFlag = True

  server_status_updater.start()
  
  print('準備ができました')
  
bot.run(config.bot_token)
