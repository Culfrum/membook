from flask import Flask, request, render_template, redirect, url_for, abort
import requests

auth = ('hackathon_33', 'hackathon_33_25')  # данные для аутентификации
app = Flask('main')  # инициализация

tags_old = [
    "P_NUM",
    "P_RAION",
    "P_FIO",
    "P_YEARS",
    "P_INFO",
    "P_KONTRAKT",
    "P_NAGRADS",
    "P_CX",
    "P_CY"
]  # Набор тегов для создания/изменения записи

add = '''{
    "extensions": {
        "attachment": null,
        "description": null
    },
    "fields": {
        "num": P_NUM,
        "n_raion": P_RAION,
        "fio": P_FIO,
        "years": P_YEARS,
        "info": P_INFO,
        "kontrakt": P_KONTRAKT,
        "nagrads": P_NAGRADS
    },
    "geom": "POINT (P_CX  P_CY)"
}'''  # Заготовка для отправки запроса о создании/изменении записи

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
reque = {}

for i in user_raw:  # итерируем строки
    usernames.append(i.split(':')[0])  # добавляем логины
    user_perm.update({i.split(':')[0]: i.split(':')[1]})  # добавляем права доступа


def find(lst, search):  # функция поиска
    ab = [False, -1]
    for index in range(len(lst)):
        if lst[index] == search:
            ab = [True, index]
    return ab


def form(args):  # формируем запрос на добавление/изменение записи
    global tags_old, add
    reqst = add
    for nums in range(len(tags_old)):
        if type(args[nums]) is str:  # если строка ставим символы для json
            reqst = reqst.replace(tags_old[nums], chr(34) + args[nums] + chr(34))
        else:  # иначе как число
            reqst = reqst.replace(tags_old[nums], str(args[nums]))
    return reqst


@app.route('/list', methods=[GET])
def lists():
    soldiers = requests.get('https://geois2.orb.ru/api/resource/8850/feature/', auth=auth).json()  # получаем список
    tabstr = []  # создание таблица
    for soldier in soldiers:  # проверка
        info_tbl = [-1, "", "", "", ""]  # заготовка строки
        id_s = -1
        for key, info in soldier.items():  # образование строки
            if key == 'id':
                id_s = info
            if key == 'fields':
                info_soldier = soldier['fields']
                info_tbl = [
                    id_s,
                    info_soldier['fio'],
                    info_soldier['n_raion'],
                    info_soldier['years'],
                    info_soldier['kontrakt']
                ]
        if info_tbl[0] != -1:  # если айди валиден то добавляем строку
            tabstr.append(info_tbl)
    return render_template('table.html', tab=tabstr)


@app.route('/soldiers/<id_s>', methods=[GET])
def main_search(id_s):
    try:
        soldiers = requests.get('https://geois2.orb.ru/api/resource/8850/feature/', auth=auth).json()  # получаем список
        info_soldier = {}
        for soldier in soldiers:  # проверка
            for key, info in soldier.items():
                if key == "id" and info == int(id_s):
                    info_soldier = soldier['fields']
        return render_template(
            'info.html',
            fio=info_soldier['fio'],
            war=info_soldier['kontrakt'],
            raion=info_soldier['n_raion'],
            year=info_soldier['years'],
            nagrads=info_soldier['nagrads'],
            info=info_soldier['info']
            )
    except KeyError:
        return render_template('none.html')


@app.route('/menu/requests/list', methods=[GET])
def main_requests_list():
    ip = request.remote_addr
    for ip_per, perms in perm.items():  # проверка на авторизацию
        if ip == ip_per:
            if perms.split(':')[0] != a:  # Если не админ
                return abort(404)  # возвращаем код 404
    tabstr = []  # создание таблицы
    ild = 0
    for req, type_r in reque.items():  # проверка

        info_tbl = [ild, req, type_r]  # заготовка строки
        if info_tbl[0] != "":  # если айди валиден то добавляем строку
            tabstr.append(info_tbl)
        ild += 1
    return render_template('req.html', tab=tabstr)


@app.route('/', methods=[GET])
def main():
    ip = request.remote_addr
    for ip_per, perms in perm.items():  # проверка на авторизацию
        if ip == ip_per:
            return render_template('main_auth.html')
    return render_template('main.html')


@app.route('/menu', methods=[GET])
def menu():
    ip = request.remote_addr
    for ip_per, perms in perm.items():  # проверка на авторизацию
        if ip == ip_per:
            if perms.split(':')[0] == a:  # Если админ
                return render_template('menu_admin.html')  # то открываем меню админа
            else:
                return render_template('menu_basic.html')  # иначе открываем меню обычного пользователя
    abort(404)  # если не авторизован вернуть 404


@app.route('/requests/new', methods=[GET, POST])
def new():
    ip = request.remote_addr
    for ip_per, perms in perm.items():  # проверка на авторизацию
        if ip == ip_per:
            if perms.split(':')[0] == a:  # Если админ
                if request.method == POST:
                    args = [
                        int(request.form['num']),
                        request.form['rai'],
                        request.form['fio'],
                        request.form['yea'],
                        request.form['inf'],
                        request.form['knt'],
                        request.form['nag'],
                        int(request.form['p1']),
                        int(request.form['p2'])
                    ]
                    data = form(args)
                    ans = requests.post('https://geois2.orb.ru/api/resource/8850/feature/', data=data, auth=auth)
                    print(ans.content)
                return render_template('new.html')  # то открываем меню админа
            if perms.split(':')[0] == u:  # Если админ
                if request.method == POST:
                    args = [
                        int(request.form['num']),
                        request.form['rai'],
                        request.form['fio'],
                        request.form['yea'],
                        request.form['inf'],
                        request.form['knt'],
                        request.form['nag'],
                        int(request.form['p1']),
                        int(request.form['p2'])
                    ]
                    data = form(args)
                    reque.update({data: "new"})
                    print(reque)
                return render_template('new.html')  # то открываем меню админа
    abort(404)  # если не авторизован вернуть 404


@app.route('/requests/remove', methods=[GET, POST])
def remove():
    ip = request.remote_addr
    for ip_per, perms in perm.items():  # проверка на авторизацию
        if ip == ip_per:
            if perms.split(':')[0] == a:  # Если админ
                if request.method == POST:
                    data = '[{"id": ' + f'{request.form['id']}' '}]'
                    requests.delete(f'https://geois2.orb.ru/api/resource/8850/feature/', data=data, auth=auth)
                return render_template('del.html')  # то открываем меню админа
            if perms.split(':')[0] == u:  # Если админ
                if request.method == POST:
                    data = '[{"id": ' + f'{request.form['id']}' '}]'
                    reque.update({data: "del"})
                    print(reque)
                return render_template('del.html')  # то открываем меню админа
    abort(404)  # если не авторизован вернуть 404


@app.route('/login', methods=[GET, POST])
def login():
    ip = request.remote_addr
    if request.method == POST:  # Обрабатываем получение данных об аккаунте
        username = request.form['username']  # получаем логин
        password = request.form['password']  # получаем пароль
        log = find(usernames, username) == find(passwords, password)  # проверяем соответствие паролей и логинов
        find_s = find(usernames, username)[1] != -1 and find(passwords, password) != -1  # проверяем на существование их
        if log and find_s:  # если пароль и логин существует и они валидны авторизуем пользователя
            user_index = user_perm[username]  # проверяем доступы пользователя
            perm.update({ip: f'{user_index}:{username}'})  # добавляем пользователя в соответствии с его доступом
            return redirect(url_for('menu'))
        else:  # иначе пароль или логин не верен
            return render_template('login.html', err_ret="Неверные данные!")
    for ip_per, perms in perm.items():  # проверка на авторизацию
        if ip == ip_per:
            if perms.split(':')[0] == a:  # Если админ
                ret = "Вы уже авторизованы! Ваш уровень доступа: Администратор"
                return render_template('login.html', err_ret=ret)
            else:  # иначе пользователь
                ret = "Вы уже авторизованы! Ваш уровень доступа: Пользователь"
                return render_template('login.html', err_ret=ret)
    return render_template('login.html')


if name == 'main':
    app.run(debug=True)  # запуск сайта
