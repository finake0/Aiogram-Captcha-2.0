import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


logging.basicConfig(level=logging.INFO)

bot_token = ' '# @BotFather

storage = MemoryStorage()

bot = Bot(token=bot_token)

dp = Dispatcher(bot, storage=storage)

class CaptchaStates(StatesGroup):
    captcha = State()

def generate_captcha(text):
    img_width, img_height = 300, 100
    captcha_image = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
    captcha_draw = ImageDraw.Draw(captcha_image)
    captcha_font = ImageFont.truetype('arial.ttf', size=50)
    captcha_draw.text((10, 30), text, font=captcha_font, fill=(0, 0, 0))
    captcha_bytes = BytesIO()
    captcha_image.save(captcha_bytes, format='PNG')
    captcha_bytes.seek(0)
    return captcha_bytes

def generate_captcha_number():
    return str(random.randint(10000, 99999))

@dp.message_handler(commands=['start'])
async def captcha(message: types.Message, state: FSMContext):
    captcha_number = generate_captcha_number()
    await CaptchaStates.captcha.set()
    async with state.proxy() as data:
        data['captcha_number'] = captcha_number
    await message.answer('Введите цифры на картинке:')
    captcha_image = generate_captcha(captcha_number)
    await message.answer_photo(captcha_image)

@dp.message_handler(state=CaptchaStates.captcha)
async def captcha_handler(message: types.Message, state: FSMContext):
    user_answer = message.text
    async with state.proxy() as data:
        captcha_number = data['captcha_number']
    if user_answer == str(captcha_number):
        await message.answer("Поздравляю, вы прошли капчу!")
        await state.finish()
    else:
        await message.answer("Вы ввели неправильное число, попробуйте еще раз.")
        await CaptchaStates.waiting_for_captcha.set() #ожидание правильного ответа от пользователя


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
