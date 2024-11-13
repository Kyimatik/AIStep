import json
import asyncio
import logging
import sys
from openai import OpenAI
import requests
import os
import time 

from aiogram.types import ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
import subprocess
import speech_recognition as sr
from pydub import AudioSegment
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import buttons
from states import Cordinates


gpt_api_key = "?" # ключ от GPTшки
googlemaps_api_key = "?" 


client = OpenAI(api_key=gpt_api_key)


TOKEN = "?"
bot = Bot(TOKEN)
dp = Dispatcher()   
router = Router()

r = sr.Recognizer()

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer(f"""Приветствую вас <b>{message.from_user.first_name}</b>!
Создадим маршрут для вас с AIStep""", parse_mode="HTML", reply_markup=buttons.vseverno)

@dp.callback_query(lambda callback_query: callback_query.data == "yes")
async def letsgo(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Отправьте ваши координаты: ", reply_markup=buttons.otmena)
    await state.set_state(Cordinates.place)

@dp.message(Cordinates.place)
async def getlocation(message: Message, state: FSMContext):
    if message.text == "Отмена ❌":
        await message.answer("Вы отменили действие", reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(place=message.text)
    await message.answer("Длина маршрута: ", reply_markup=buttons.mainkb)
    await state.set_state(Cordinates.radius)

@dp.message(Cordinates.radius)
async def getradius(message: Message, state: FSMContext):
    await state.update_data(radius=message.text)
    await message.answer("""Ваши <i>предпочтения</i>?
Что вы хотите увидеть по пути ? 
Вы можете как текстом написать 📄, так и отправить голосовой 🗣.""", parse_mode="HTML")
    await state.set_state(Cordinates.prefer)

@dp.message(Cordinates.prefer)
async def getpreferences(message: Message, state: FSMContext):
    if message.content_type == 'text':
        # Сохраняем текстовые предпочтения
        await state.update_data(prefer=message.text)
    elif message.content_type == 'voice':
        # Если это голосовое сообщение, сохраняем его как файл
        voice = message.voice
        file_info = await bot.get_file(voice.file_id)
        
        # Создаем имя файла для сохранения
        file_name = f"{voice.file_id}.ogg"
        file_name_wav = f"{voice.file_id}.wav"
        
        # Скачиваем голосовое сообщение
        await bot.download_file(file_info.file_path, file_name)
        
        # Конвертируем из ogg в wav с помощью ffmpeg
        subprocess.call(['ffmpeg', '-i', file_name, file_name_wav])

        # Распознаем голосовое сообщение
        prefer_text = recognize_audio(file_name_wav)

        # Обновляем данные предпочтений с распознанным текстом
        await state.update_data(prefer=prefer_text)
        
        # Удаляем временные файлы
        os.remove(file_name)
        os.remove(file_name_wav)
    else:
        await message.answer("Пожалуйста, отправьте текст или голосовое сообщение.")
    data = await state.get_data()
    place = data["place"]  # Координаты
    radius = data["radius"]  # Радиус
    prefer = data["prefer"]  # Предпочтения

    await message.answer(f"""<b>Ваши координаты</b> - {place}
<b>Длина Маршрута</b> - {radius}
<b>Ваши предпочтения</b> - {prefer}
""", parse_mode="HTML")

    # Шаг 1: Генерируем запрос для Google Places API с помощью ChatGPT
    places_api_query = generate_places_api_query(client, place, radius, prefer)

    # Шаг 2: Выполняем запрос и получаем список мест
    places_results = get_places(places_api_query)
    location_part = places_api_query.split("location=")[1].split("&")[0]

    # Разделяем на широту и долготу
    latitude, longitude = location_part.split(',')

    cor = []
    sor = []
    for i in places_results:
        cor.append(f"{i['coordinates']}")
    for coord in cor:
        # Убираем скобки и разделяем строку по запятой
        lat, lng = coord.strip('()').split(', ')
        sor.append((float(lat), float(lng)))
    # Количество маркеров в одном запросе
    chunk_size = 9  # Можно варьировать в зависимости от длины URL

    # Инициализируем базовый URL для карты
    base_static_map_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"size=600x400&"
        f"markers=color:red%7Clabel:U%7C{latitude},{longitude}&"  # Маркер на пользователя
    )

    # Разбиваем запросы на части по chunk_size маркеров
    for start in range(0, len(sor), chunk_size):
        # Создаем частичный URL для текущего набора маркеров
        partial_url = base_static_map_url
        chunk = sor[start:start + chunk_size]

        # Добавляем маркеры для текущей части
        for i, (lat, lng) in enumerate(chunk):
            partial_url += f"markers=color:blue%7Clabel:{i+1}%7C{lat},{lng}&"

            # Добавляем маршруты для текущей части
            directions_url = (
                f"https://maps.googleapis.com/maps/api/directions/json?"
                f"origin={latitude},{longitude}&"
                f"destination={lat},{lng}&"
                f"key={googlemaps_api_key}"
            )
            directions_response = requests.get(directions_url)

            if directions_response.status_code == 200:
                directions_data = directions_response.json()
                if directions_data['routes']:
                    route_points = directions_data['routes'][0]['overview_polyline']['points']
                    partial_url += f"path=enc:{route_points}&"
            else:
                print(f"Ошибка при запросе маршрута: {directions_response.status_code}")

        # Добавляем API ключ в конце
        partial_url += f"key={googlemaps_api_key}"

        # Проверяем длину URL
        if len(partial_url) > 2048:
            print("URL слишком длинный, пропускаем.")
            continue

        # Выполняем запрос к Static Map API
        static_map_response = requests.get(partial_url)

        if static_map_response.status_code == 200:
            # Сохраняем изображение карты
            with open(f'map_with_routes_{start//chunk_size + 1}.png', 'wb') as file:
                file.write(static_map_response.content)
            print(f"Карта {start//chunk_size + 1} сохранена.")
        else:
            print(f"Ошибка при запросе карты: {static_map_response.status_code}")

    
    
    # Отправляем карты пользователю и затем информацию по маркерам
    for i in range(1, (len(sor) // chunk_size) + 2):
        file_path = rf'C:\Users\STE\Desktop\HACKATHON\map_with_routes_{i}.png'
        
        time.sleep(5)
        if os.path.exists(file_path):
            # Отправляем карту
            photo = FSInputFile(file_path)
            await message.answer_photo(photo=photo)
    
            # Создаем переменную для накопления всей информации о маркерах для этой карты
            all_places_info = ""
            marker_number = 1
    
            # После отправки карты собираем информацию о маркерах
            start_index = (i - 1) * chunk_size
            end_index = min(len(sor), i * chunk_size)
    
            for j in range(start_index, end_index):
                lat, lng = sor[j]
                place_info = places_results[j]  # Информация о маркере
                name = place_info['name']  # Название заведения
                rating = place_info.get('rating', 'Рейтинг не указан')  # Получаем рейтинг
                address = place_info.get('address', 'Адрес не указан')  # Адрес заведения
    
                # Накапливаем информацию о маркерах
                all_places_info += f"№ {marker_number}: {name}, адрес: {address}, рейтинг: {rating}\n"
                marker_number += 1  # Увеличиваем номер маркера после каждого
    
            # Отправляем информацию о маркерах для этой карты одним сообщением
            await message.answer(all_places_info)
    
            # Очищаем переменную для накопления данных перед следующей картой
            all_places_info = ""
    
            # Удаляем файл после отправки
            try:
                os.remove(file_path)
                print(f"Файл {file_path} удалён.")
            except OSError as e:
                print(f"Ошибка при удалении файла {file_path}: {e}")
        else:
            print(f"Файл {file_path} не найден, пропускаем.")


def generate_places_api_query(client, place, radius, prefer):
    """
    Генерирует корректный URL-запрос для Google Places API с использованием OpenAI.

    :param client: Инициализированный клиент OpenAI.
    :param place: Координаты места (широта и долгота).
    :param radius: Радиус поиска в метрах.
    :param prefer: Предпочтения пользователя (например, тип мест).
    :return: Сгенерированный URL-запрос для Google Places API.
    """
    prompt = f"""
    Отправляй хорошие и правильные url заросы , если там написано цифра буквами в запросе указывай цифрой обязательно.
    Без ОПИСАНИЯ ПОЖАЛУЙСТА ТОЛЬКО URL отправь 
    Самое важное убедись что в твоем ответе кроме URL ничего нету , так как твой url запрос сразу выполняется и из за того что ты описание кидаешь , происходят ошибки.
    Убедись что без всяких описаний делаешь только URL запрос.
    Используй вот этот вот ключ - ? - google places API
    Ты виртуальный помощник, который помогает пользователям генерировать корректные запросы для Google Places API. Вот основные шаги, которые ты должен выполнять:

1. Интерпретация запроса пользователя: Понять, что именно хочет пользователь — например, найти ближайшие кафе, школы или другие места.
2. Формирование корректного URL для Google Places API на основе координат {place}, радиуса {radius} и предпочтений {prefer}.
3. Используй Google Places API для поиска объектов, таких как "{prefer}" в радиусе {radius} метров от координат {place}.
4. Генерация запроса только в виде URL для Google Places API.

Пример:
https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={place}&radius={radius}&keyword={prefer}&key={googlemaps_api_key}



    """
    
    response = client.chat.completions.create(
        #model="gpt-3.5-turbo-1106",
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты ассистент, который помогает формировать запросы для Google Maps API."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7,
        n=1
    )

    # Извлечение URL из ответа
    generated_query = response.choices[0].message.content.strip()
    
    # Печатаем сгенерированный запрос для отладки
    print("Сгенерированный запрос:", generated_query)
    
    return generated_query

def get_places(query):
    """
    Выполняет запрос к Google Places API и возвращает список мест с рейтингом и адресом.
    """
    response = requests.get(query)

    if response.status_code == 200:
        places_data = response.json()

        if 'results' in places_data:
            places = []
            for place in places_data['results']:
                name = place.get('name', 'Название не указано')
                lat = place['geometry']['location']['lat']
                lng = place['geometry']['location']['lng']
                rating = place.get('rating', 'Рейтинг не указан')  # Получаем рейтинг
                address = place.get('vicinity', 'Адрес не указан')  # Получаем адрес

                # Возвращаем данные в виде словаря
                places.append({
                    "name": name,
                    "coordinates": (lat, lng),
                    "rating": rating,
                    "address": address
                })

            return places
        else:
            return []
    else:
        print(f"Ошибка при запросе мест: {response.status_code}")
        return []




# Сделать всех ebnut' , Bam-bum 

def get_directions(place, destination):
    """
    Получает маршрут от точки place до точки destination с помощью Google Directions API.
    :param place: Исходная точка (координаты пользователя).
    :param destination: Конечная точка (координаты места).
    :return: Описание маршрута или сообщение об ошибке.
    """
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={place}&destination={destination}&key={googlemaps_api_key}"
    response = requests.get(directions_url)

    if response.status_code == 200:
        directions_data = response.json()

        if directions_data["status"] == "OK":
            # Извлечение информации о маршруте
            route = directions_data["routes"][0]
            leg = route["legs"][0]

            distance = leg["distance"]["text"]
            duration = leg["duration"]["text"]
            steps = leg["steps"]

            # Формирование текста с маршрутом
            directions_text = f"Расстояние: {distance}, Время: {duration}\n\nШаги маршрута:\n"

            # Извлекаем пошаговые инструкции
            for step in steps:
                instructions = step["html_instructions"]
                distance_step = step["distance"]["text"]
                directions_text += f"{instructions} ({distance_step})\n"

            return directions_text
        else:
            return "Не удалось построить маршрут."
    else:
        print(f"Ошибка при запросе маршрута: {response.status_code}")
        return None



# Функция для распознавания речи из аудиофайла
def recognize_audio(file_path):
    # Конвертируем из ogg в wav с помощью pydub
    audio = AudioSegment.from_ogg(file_path)
    audio.export("temp.wav", format="wav")
    
    # Используем SpeechRecognition для распознавания речи
    try:
        with sr.AudioFile("temp.wav") as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="ru-RU")
            return text
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка при запросе к сервису: {e}"
    finally:
        # Ожидаем, что файл больше не используется и можем его удалить
        if os.path.exists("temp.wav"):
            try:
                os.remove("temp.wav")
            except PermissionError:
                print("Файл всё ещё используется и не может быть удалён")



@dp.message(F.text.contains("Отмена ❌"))
async def otmenafunc(message: Message):
    await message.answer("Вы отменили действие!", reply_markup=ReplyKeyboardRemove())
    return

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


# Не уходи смиренно 
# Основной код , который нужно будет показать - 2gis.