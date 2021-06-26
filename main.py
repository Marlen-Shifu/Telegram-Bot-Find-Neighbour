import logging

from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN,  OLD_TOKEN, cities, rent_prices

from orm import DBConnector

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Configure logging
logging.basicConfig(level=logging.INFO)

#Initialize a database orm manager

db_manager = DBConnector()

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())



class WriteFormState(StatesGroup):
	category = State()
	full_name = State()
	phone_number = State()
	title = State()
	address = State()
	city = State()
	people_count = State()
	description = State()
	price = State()
	gender = State()


class FilterState(StatesGroup):
	category = State()
	city = State()
	people_count = State()
	price = State()
	gender = State()


main_menu_btn = types.KeyboardButton('Главное меню')

main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard = True).add(main_menu_btn)

main_menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
btn_1 = types.KeyboardButton('Все объявления')
btn_2 = types.KeyboardButton('Дать объявление')
btn_3 = types.KeyboardButton('Фильтр')
btn_4 = types.KeyboardButton('Мои объявления')
main_menu.add(btn_1).add(btn_2).add(btn_3).add(btn_4)


@dp.message_handler(commands = ['mailing'])
async def mailing(message):
	await message.answer(message.get_args())




async def check_and_add_user(user_id, user_name):
	user_in_database = db_manager.get_user(user_id)

	if user_in_database == None:
		db_manager.add_user(user_id, user_name)


@dp.message_handler(commands = ['registeredusers'])
async def users(message):
	users = db_manager.get_all_users()
	message_to_answer = f"Зарегестрированных пользователей {len(users)}:\n"

	for user in users:
		counter = 1
		message_to_answer += f"{counter} - @{user[1]}\n"

	await message.answer(message_to_answer)

@dp.message_handler(lambda mes: mes.text == 'Главное меню', state='*')
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message, state: FSMContext):
	"""
	This handler will be called when user sends `/start` or `/help` command
	"""
	await state.finish()

	await check_and_add_user(message.from_user.id, message.from_user.username)

	message_to_answer = 'Переход на главную страницу' if message.text == 'Главное меню' else "Здравствуйте!\nЭто бот созданный что бы находить сожителей для совместного проживания и дележки тяжелой ноши аренды :D"

	await message.reply(
						message_to_answer,
						reply_markup = main_menu)



@dp.message_handler(lambda mes: mes.text == 'Дать объявление')
async def write_form(message: types.Message):

	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)

	btn1 = types.KeyboardButton('У меня есть квартира')
	btn2 = types.KeyboardButton('Я ищу квартиру')

	markup.add(btn1, btn2).add(main_menu_btn)

	await WriteFormState.category.set()

	await message.answer(
					'У вас есть квартира или нет?', 
					reply_markup = markup)



@dp.message_handler(state=WriteFormState.category, content_types=types.ContentTypes.TEXT)
async def write_form_get_category(message: types.Message, state: FSMContext):

	if message.text == 'У меня есть квартира' or message.text == 'Я ищу квартиру':

		await state.update_data(category=message.text.title())

		await message.answer(
						'Введите полное имя', 
						reply_markup = main_menu_markup)

		await WriteFormState.full_name.set()

	else:
		await message.answer('Выберите один из вариантов ниже')

@dp.message_handler(state=WriteFormState.full_name, content_types=types.ContentTypes.TEXT)
async def write_form_get_name(message: types.Message, state: FSMContext):

	await state.update_data(user_full_name=message.text.title())
	await message.answer(text='Введите номер телефона', 
					reply_markup = main_menu_markup)
	await WriteFormState.phone_number.set()

@dp.message_handler(state=WriteFormState.phone_number, content_types=types.ContentTypes.TEXT)
async def write_form_get_phone(message: types.Message, state: FSMContext):

	await state.update_data(user_phone=message.text.title())

	await message.answer(
					'Напишите название объявления')

	await WriteFormState.title.set()

@dp.message_handler(state=WriteFormState.title, content_types=types.ContentTypes.TEXT)
async def write_form_get_title(message: types.Message, state: FSMContext):

	await state.update_data(form_title=message.text.title())

	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)

	for city in cities:
		btn = types.KeyboardButton(city)
		markup.add(btn)
	markup.add(main_menu_btn)

	await message.answer(text='Выберите город',
						reply_markup = markup)

	await WriteFormState.city.set()

@dp.message_handler(state=WriteFormState.city, content_types=types.ContentTypes.TEXT)
async def write_form_get_city(message: types.Message, state: FSMContext):

	if message.text.title() in cities:

		await state.update_data(form_city=message.text.title())

		await message.answer(text='Напишите адрес',
							reply_markup = main_menu_markup)
		await WriteFormState.address.set()

	else:
		await message.answer('Напишите один из вариантов ниже')

@dp.message_handler(state=WriteFormState.address, content_types=types.ContentTypes.TEXT)
async def write_form_get_address(message: types.Message, state: FSMContext):

	await state.update_data(form_address=message.text.title())
	await WriteFormState.people_count.set()
	await message.answer(text='Напишите количество жильцов',
						reply_markup = main_menu_markup)

@dp.message_handler(state=WriteFormState.people_count, content_types=types.ContentTypes.TEXT)
async def write_form_get_people_count(message: types.Message, state: FSMContext):

	try:
		count = int(message.text.replace(' ', ''))

		await state.update_data(form_people_count=message.text.title())

		await message.answer(text='Напишите описание объявления')
		await WriteFormState.description.set()
		
	except ValueError as e:
		await message.answer('Введите число')


@dp.message_handler(state=WriteFormState.description, content_types=types.ContentTypes.TEXT)
async def write_form_get_description(message: types.Message, state: FSMContext):

	await state.update_data(form_description=message.text.title())

	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)

	for price in rent_prices:
		btn = types.KeyboardButton(price)
		markup.add(btn)

	markup.add(main_menu_btn)

	await message.answer(text='Выберите цену(тг/мес)',
						reply_markup = markup)
	await WriteFormState.price.set()

@dp.message_handler(state=WriteFormState.price, content_types=types.ContentTypes.TEXT)
async def write_form_get_price(message: types.Message, state: FSMContext):

	if message.text in rent_prices:
		await state.update_data(form_price=message.text)

		markup = types.ReplyKeyboardMarkup(resize_keyboard = True)

		btn_1 = types.KeyboardButton('Мужчина')
		btn_2 = types.KeyboardButton('Женщина')
		markup.add(btn_1, btn_2).add(main_menu_btn)

		await message.answer(text='Выберите пол',
							reply_markup = markup)
		await WriteFormState.gender.set()
	else:
		await message.answer('Выберите один из вариантов ниже')


@dp.message_handler(state=WriteFormState.gender, content_types=types.ContentTypes.TEXT)
async def write_form_get_gender(message: types.Message, state: FSMContext):

	if message.text == 'Мужчина' or message.text == 'Женщина':

		await state.update_data(form_gender=message.text.title())

		data = await state.get_data()
		data['user_id'] = message.from_user.id
		data = [data[key] for key in data]
		await state.finish()

		db_manager.add_ad(*data)

		await message.answer(text='Отлично заявка успешно создана!',
							reply_markup = main_menu)

	else:
		await message.answer('Выберите один из вариантов ниже')



async def make_ads_markup(ads_data, page_number, mod = 'page', ad_mod = 'ad',filters_data = ''):

	markup = types.InlineKeyboardMarkup()

	ads_data_len = len(ads_data)

	page_rage = page_number * 10 - 10

	page_count = ads_data_len // 10 + 1

	if page_number == page_count:
		ads_count = ads_data_len - page_rage
	else:
		ads_count = 10

	if ads_data_len > 10:

		for i in range(page_rage, page_rage + ads_count):
			ad_btn = types.InlineKeyboardButton(f'{ads_data[i][4]}', callback_data = f'{ad_mod} {ads_data[i][0]}')

			markup.add(ad_btn)

		previous_page = None if page_number == 1 else (page_number - 1)

		next_page = (page_number + 1) if (page_number) != (ads_data_len // 10 + 1) else None

		if previous_page != None:
			previous_page_btn = types.InlineKeyboardButton('<- Назад на страницу ' + str(previous_page), callback_data = mod + ' ' + str(previous_page) + '/' + str(filters_data))
			markup.add(previous_page_btn)

		if next_page != None:
			next_page_btn = types.InlineKeyboardButton('Вперед на страницу ' + str(next_page) + ' ->', callback_data = mod + ' ' + str(next_page) + '/' + str(filters_data))
			markup.add(next_page_btn)

	else:
		for ad_data in ads_data:
			ad_btn = types.InlineKeyboardButton(f'{ad_data[4]}', callback_data = f'{ad_mod} {ad_data[0]}')

			markup.add(ad_btn)

	return markup


@dp.message_handler(lambda mes: mes.text == 'Все объявления')
async def show_all_ads(message: types.Message):

	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
	btn_1 = types.KeyboardButton('Ищу квартиру')
	btn_2 = types.KeyboardButton('Ищу людей')
	markup.add(btn_1, btn_2).add(main_menu_btn)

	await message.answer('Что вы ищете?',
						reply_markup = markup)


async def sort_ads(ads_data, sort_data):

	sort_data_index = {
		'category': 1,
		'city': 5,
		'people_count': 7,
		'price': 9,
		'gender': 10
	}

	category_dict = {
		'Ищу Квартиру': 'У Меня Есть Квартира',
		'Ищу Людей': 'Я Ищу Квартиру'
	}

	ads_data_to_give = ads_data


	if 'category' in sort_data:

		ads_data_to_give = [ad_data for ad_data in ads_data_to_give 
							if ad_data[sort_data_index['category']] == category_dict[sort_data['category']] ] 

	if 'city' in sort_data:
		ads_data_to_give = [ad_data for ad_data in ads_data_to_give 
							if ad_data[sort_data_index['city']] == sort_data['city'] ] 

	if 'people_count' in sort_data:
		ads_data_to_give = [ad_data for ad_data in ads_data_to_give 
							if ad_data[sort_data_index['people_count']] == int(sort_data['people_count']) ] 

	if 'price' in sort_data:
		ads_data_to_give = [ad_data for ad_data in ads_data_to_give	
							if ad_data[sort_data_index['price']] == sort_data['price'] ]

	if 'gender' in sort_data:
		ads_data_to_give = [ad_data for ad_data in ads_data_to_give	
							if ad_data[sort_data_index['gender']] == sort_data['gender'] ] 

	return ads_data_to_give


@dp.message_handler(lambda mes: mes.text == 'Ищу квартиру')
@dp.message_handler(lambda mes: mes.text == 'Ищу людей')
async def show_ads(message: types.Message):

	ads_data = db_manager.get_all_ads()

	ads_data = await sort_ads(ads_data, {'category': message.text.title()})
	markup = await make_ads_markup(ads_data, 1)

	await message.answer('Объявления для ' + message.text,
						reply_markup = markup)



@dp.callback_query_handler(lambda mes: mes.data.startswith('ad'))
async def show_ad(call: types.CallbackQuery):

	await bot.answer_callback_query(call.id)

	call_data = call.data.split()

	ad_data = db_manager.get_ad(call_data[1])

	message_to_answer = await make_ad_message(ad_data)
	
	await bot.send_message(call.from_user.id, message_to_answer)

@dp.callback_query_handler(lambda call: call.data.startswith('page'))
async def show_ads_page(call: types.CallbackQuery):

	await bot.answer_callback_query(call.id)

	call_data = call.data.split()

	ads_data = db_manager.get_all_ads()

	markup = await make_ads_markup(ads_data, int(call_data[1]))

	await bot.send_message(call.from_user.id, 
						'Все объявления\nСтраница ' + call_data[1],
						reply_markup = markup)



@dp.message_handler(lambda mes: mes.text == 'Фильтр')
async def filter_start(message):
	await FilterState.category.set()

	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
	btn_1 = types.KeyboardButton('Ищу квартиру')
	btn_2 = types.KeyboardButton('Ищу людей')
	btn_3 = types.KeyboardButton('Пропустить')
	markup.add(btn_1, btn_2).add(btn_3).add(main_menu_btn)

	await message.answer('Выберите категорию',
						reply_markup = markup)


@dp.message_handler(state=FilterState.category, content_types=types.ContentTypes.TEXT)
async def filter_get_category(message: types.Message, state: FSMContext):

	if message.text == 'Ищу квартиру' or message.text == 'Ищу людей' or message.text == 'Пропустить':

		if message.text == 'Пропустить':
			pass
		else:
			await state.update_data(category=message.text.title())

		markup = types.ReplyKeyboardMarkup(resize_keyboard = True)

		for city in cities:
			btn = types.KeyboardButton(city)
			markup.add(btn)
			
		btn_1 = types.KeyboardButton('Пропустить')

		markup.add(btn_1).add(main_menu_btn)

		await message.answer(
						'Выберите город', 
						reply_markup = markup)

		await FilterState.city.set()

	else:
		await message.answer('Выберите один из вариантов ниже')

@dp.message_handler(state=FilterState.city, content_types=types.ContentTypes.TEXT)
async def write_form_get_city(message: types.Message, state: FSMContext):

	if message.text == 'Пропустить':
		pass
	else:
		if message.text.title() in cities:

			await state.update_data(city=message.text.title())
		else:
			await message.answer('Выберите один из вариантов ниже')

	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
	btn_1 = types.KeyboardButton('Пропустить')
	markup.add(btn_1).add(main_menu_btn)

	await message.answer(text='Напишите количество жильцов',
						reply_markup = markup)
	await FilterState.people_count.set()

@dp.message_handler(state=FilterState.people_count, content_types=types.ContentTypes.TEXT)
async def filter_get_people_count(message: types.Message, state: FSMContext):

	if message.text == 'Пропустить':
		pass
	else:

		try:
			count = int(message.text.replace(' ', ''))

			await state.update_data(people_count=message.text.title())
			
		except ValueError as e:
			await message.answer('Введите число')
			return	
	
	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)

	for price in rent_prices:
		btn = types.KeyboardButton(price)
		markup.add(btn)

	btn_1 = types.KeyboardButton('Пропустить')
	markup.add(btn_1).add(main_menu_btn)

	await message.answer(text='Выберите цену',
								reply_markup = markup)
	await FilterState.price.set()

@dp.message_handler(state=FilterState.price, content_types=types.ContentTypes.TEXT)
async def filter_get_price(message: types.Message, state: FSMContext):
	
	if message.text == 'Пропустить':
		pass
	else:
		await state.update_data(price=message.text)

	markup = types.ReplyKeyboardMarkup(resize_keyboard = True)

	btn_1 = types.KeyboardButton('Мужчина')
	btn_2 = types.KeyboardButton('Женщина')
	btn_3 = types.KeyboardButton('Пропустить')

	markup.add(btn_1).add(btn_2).add(btn_3).add(main_menu_btn)

	await message.answer(text='Выберите пол',
						reply_markup = markup)
	await FilterState.gender.set()


@dp.message_handler(state=FilterState.gender, content_types=types.ContentTypes.TEXT)
async def filter_get_gender(message: types.Message, state: FSMContext):

	if message.text == 'Мужчина' or message.text == 'Женщина' or message.text == 'Пропустить':

		if message.text == 'Пропустить':
			pass
		else:
			await state.update_data(gender=message.text.title())
		

		sort_data = await state.get_data()

		await state.finish()

		ads_data = db_manager.get_all_ads()

		sorted_ads = await sort_ads(ads_data, sort_data)

		ads_markup = await make_ads_markup(sorted_ads, 1, mod = 'filter', filters_data = sort_data)

		await message.answer(text='Фильтр применен',
							reply_markup = main_menu)

		await message.answer('Объявления', 
							reply_markup = ads_markup)

	else:
		await message.answer('Выберите один из вариантов ниже')

@dp.callback_query_handler(lambda call: call.data.startswith('filter'))
async def filter(call):

	call_data = call.data.split('/')

	ads_data = db_manager.get_all_ads()

	sort_data = eval(call_data[1])

	sorted_ads = await sort_ads(ads_data, sort_data)

	ads_markup = await make_ads_markup(sorted_ads, int(call_data[0][-1]), mod = 'filter', filters_data = sort_data)


	await bot.send_message(call.from_user.id,
						'Объявления\nСтраница ' + call_data[0][-1], 
						reply_markup = ads_markup)



@dp.message_handler(lambda mes: mes.text == 'Мои объявления')
async def my_ads(message):
	user_id = message.from_user.id

	ads = db_manager.get_ads_of_user(user_id)

	ads_markup = await make_ads_markup(ads, 1, ad_mod = 'myad')

	await message.answer('Мои объявления\nСтраница 1',
						reply_markup = ads_markup)

@dp.callback_query_handler(lambda call: call.data.startswith('myad'))
async def show_my_ad(call):
	await bot.answer_callback_query(call.id)

	call_data = call.data.split()

	ad_data = db_manager.get_ad(call_data[1])

	message_to_answer = await make_ad_message(ad_data)

	markup = types.InlineKeyboardMarkup()

	btn_1 = types.InlineKeyboardButton('Удалить', callback_data = 'deletemyad ' + call_data[1])
	markup.add(btn_1)

	await bot.send_message(call.from_user.id,
							message_to_answer,
							reply_markup = markup)

@dp.callback_query_handler(lambda call: call.data.startswith('deletemyad'))
async def delete_my_ad(call):
	await bot.answer_callback_query(call.id)

	call_data = call.data.split()

	db_manager.delete_ad(int(call_data[1]))

	await bot.send_message(call.from_user.id,
							'Объявление успешно удалено')


async def make_ad_message(ad_data):
	message_to_answer = f'''
		Категория: {ad_data[1]}
		Владелец: {ad_data[2]}
		Телефон: {ad_data[3]}
		Название: {ad_data[4]}
		Описание: {ad_data[8]}
		Адрес: {ad_data[6]}
		Город: {ad_data[5]}
		Количество сожильцов: {ad_data[7]}
		Цена(тг/мес): {ad_data[9]}
		Пол: {ad_data[10]}
	'''
	return message_to_answer



if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
