from flask import Flask, request, render_template
import requests
auth = ('-', '-')
app = Flask('main')
wars = [
    'Великая отечественная война',
    'Боевые действия в Афганистане',
    'Вооруженный конфликт в Чеченской Республике и на прилегающих к ней территориях Российской Федерации',
    'Выполнение специальных задач на территории Сирийской Арабской Республики',
    'Выполнение специальных задач на территории Таджикистана, Ингушетии, в Грузино-Абхазских событиях',
    'Специальная военная операция на Украине'
]
name = 'main'


@app.route('/list', methods=['GET'])
def index_list():
    soldiers = requests.get('https://geois2.orb.ru/api/resource/8850/feature/', auth=auth).json()
    tabstr = []
    for solder in soldiers:
        info_tbl = [-1, "", "", "", ""]
        for key, info in solder.items():
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
        if info_tbl[0] != -1:
            tabstr.append(info_tbl)
    return render_template('table.html', tab=tabstr)


@app.route('/', methods=['GET'])
def index_main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def index_login():
    if request.method == "POST":
        pass
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def index_register():
    if request.method == "POST":
        pass
    return render_template('register.html')


if name == 'main':
    app.run(debug=True)
