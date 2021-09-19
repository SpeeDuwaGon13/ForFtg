from .. import loader, utils
from telethon import events

def register(cb):
  cb(SendEchoLOL())
  
class SendEchoLOL(loader.Module):
  """This is my f1rst project :D"""
  strings = {'name': 'VovaProject'}
  
  async def V_texcmd(self, message):
    """Пиши .V_tex <Аргумент ("abme", "ths")>"""
    text = utils.get_args_raw(message)
    
    if not text:
      await message.edit("<b>Нету аргумента - я не понимаю что ты от меня хочешь</b>")
      return
    
    await message.edit("<b>Минуточку...</b>")
    if text == "abme":
      await message.edit("<b>Я - Вова, и я учусь писать модули, и мне тяжело всё это даётся</b>")
      return
    
    elif text == "ths":
      await message.edit("<b>Это мой самый первый проект, который был создан благодаря ответам Fl1yd :D</b>")
      return
