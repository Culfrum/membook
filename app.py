from flask import Flask, request, render_template, redirect, url_for, abort
import requests
auth = ('hackathon_33', 'hackathon_33_25')  # данные для аутентификации
app = Flask('main')  # инициализация

wars = [
    'Великая отечественная война',
    'Боевые действия в Афганистане',
    'Вооруженный конфликт в Чеченской Республике и на прилегающих к ней территориях Российской Федерации',
    'Выполнение специальных задач на территории Сирийской Арабской Республики',
    'Выполнение специальных задач на территории Таджикистана, Ингушетии, в Грузино-Абхазских событиях',
    'Специальная военная операция на Украине'
]  # Список войн и конфликтов

name = 'main'
GET = 'GET'  # Флаг GET для запросов
POST = 'POST'  # Флаг POST для запросов
a = 'a'  # Флаг "А" для аккаунтов (устанавливает права администратора на пользователя)
u = 'u'  # флаг "П" для аккаунтов (устанавливает стандартные права пользователя)

pass_file = open("database/passwords.txt", 'r', encoding='utf-8')  # открываем файл для паролей
user_file = open("database/logins.txt", 'r', encoding='utf-8')  # открываем файл для логинов

passwords = pass_file.read().splitlines()  # разделяем на строки
user_raw = user_file.read().splitlines()  # разделяем на строки

perm = {}  # Список авторизованных IP (Формат:{'ip адрес': 'права (a - администратор, u - пользователь)'])
usernames = []  # список логинов
user_perm = {}  # список доступов (Формат:{'логин': 'права (a - администратор, u - пользователь)'])

for i in user_raw:  # итерируем строки
    usernames.append(i.split(':')[0])  # добавляем логины
    user_perm.update({i.split(':')[0]: i.split(':')[1]})  # добавляем права доступа


def find(lst, search):  # функция поиска
    ab = [False, -1]
    for index in range(len(lst)):
        if lst[index] == search:
            ab = [True, index]
    return ab


@app.route('/list', methods=[GET])  # список погибших
def lists():
    soldiers = requests.get('https://geois2.orb.ru/api/resource/8850/feature/', auth=auth).json()  # получаем список
    tabstr = []  # создание таблица
    for solder in soldiers:  # проверка
        info_tbl = [-1, "", "", "", ""]  # заготовка строки
        for key, info in solder.items():  # образование строки
            if key == 'id':
                info_tbl[0] = info
            if key == 'fields':
                for kkey, iinfo in info:
                    match kkey:
                        case 'fio':
                            info_tbl[1] = iinfo
                        case 'n_raion':
                            info_tbl[2] = iinfo
                        case 'years':
                            info_tbl[3] = iinfo
                        case 'kontrakt':
                            info_tbl[4] = iinfo
        if info_tbl[0] != -1:  # если айди валиден то добавляем строку
            tabstr.append(info_tbl)
    return render_template('table.html', tab=tabstr)


@app.route('/', methods=[GET])  # основная страница
def main():
    return render_template('main.html')


@app.route('/menu', methods=[GET])  # меню пользователя
def menu():
    ip = request.remote_addr
    for ip_per, perms in perm.items():  # проверка на авторизацию
        if ip == ip_per:
            if perms == a:  # Если админ
                return render_template('menu_admin.html')  # то открываем меню админа
            else:
                return render_template('menu_basic.html')  # иначе открываем меню обычного пользователя
    abort(404)  # если не авторизован вернуть 404


@app.route('/login', methods=[GET, POST])  # Страница для авторизации на сайте
def login():
    ip = request.remote_addr
    if request.method == POST:  # Обрабатываем получение данных об аккаунте
        username = request.form['username']  # получаем логин
        password = request.form['password']  # получаем пароль
        log = find(usernames, username) == find(passwords, password)  # проверяем соответствие паролей и логинов
        find_s = find(usernames, username)[1] != -1 and find(passwords, password) != -1  # проверяем на существование их
        if log and find_s:  # если пароль и логин существует и они валидны авторизуем пользователя
            user_index = user_perm[username]  # проверяем доступы пользователя
            perm.update({ip: user_index})  # добавляем пользователя в соответствии с его доступом
            return redirect(url_for('menu'))
        else:  # иначе пароль или логин не верен
            return render_template('login.html', err_ret="Неверные данные!")
    return render_template('login.html')


if name == 'main':
    app.run(debug=True)  # запуск сайта
