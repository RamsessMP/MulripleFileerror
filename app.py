from flask import Flask, render_template, request, redirect, url_for #микрофреймворк, получение данных из запроса, отображение HTML, перенаправление на другую страницу
from flask_sqlalchemy import SQLAlchemy #Библиотека для работы с БД
from flask_wtf import FlaskForm #библиотека для работы с формами
from wtforms import StringField, SubmitField #импорт типов полей (строка и кнопка отправки)
from wtforms.validators import DataRequired #проверка поля формы на заполнение
from flask_wtf.file import MultipleFileField,  FileField#файловый тип поля
from werkzeug.utils import secure_filename #для защиты сервера от имени файла
import json
import os #получение пути файлов

#создаем объект сайта, сообщаем его с БД и создаем объект класса SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)

class Notesdb(db.Model): #создаем класс по базе с заметками. Переменная = Поле БД
    __tablename__ = 'Notes' #указываем имя таблицы, если имя файла БД не соответсвует имени таблицы БД
    id = db.Column(db.Integer(), nullable = False, unique = True, primary_key = True, autoincrement=True)
    Title = db.Column(db.Text())
    Text = db.Column(db.Text())
    Image = db.Column(db.Text())

class NewNote(FlaskForm): # класс для создания новой заметки (с помощью wtf форм)
    title = StringField()
    text = StringField(validators=[DataRequired()])
    image = MultipleFileField()
    #image = FileField()
    submit = SubmitField(label='sumbit') 


@app.route('/') #Главная страница
def index():
    lstnotes = Notesdb.query.all() #обращаемся к классу по нашей БД, получаем всю таблицу Notes [<Notesdb 0>, <Notesdb 1>]
    return render_template('mainpage.html', lstnotes=lstnotes)

#ссылка на страницу создания заметки
@app.route('/newnote', methods = ['GET', 'POST']) # декоратор принимает и get, и post запросы. Post-запрос - отправка заметки на сервер (в БД)
def newnote():
    form = NewNote() #объект класса NewNote

    if form.validate_on_submit(): #если форма была отправлена и прошла проверку
        title, text = form.title.data, form.text.data #сохраняем данные из полей формы в переменные

        #filename = secure_filename(image.filename) 
        #image.save(os.path.join(app.static_folder, 'images', filename))

        #поддерживаем сохранение и вывод нескольких файлов на странице, а не первого выбранного
        imgsroad = [] #список для хранения в БД названий изображений
        images = request.files.getlist('image') #получаем список из файлов, загруженных в поле image
        for image in images:
            if image: #если изображение было загруженно
                filename = secure_filename(image.filename) #secure_filename - создаем и изменяем имя файла. 
                                                   #.filename используется только для полей типа FileStorage
                image.save(os.path.join(app.static_folder, 'images', filename)) #объединяем имя папки и имя загруженного файла и сохраняем файл по этому пути
                                #app.static_folder - абсолютный путь     
                imgsroad.append(filename) 
        
        imgsroadjs = json.dumps(imgsroad)#sqlite3 не поддерживает list, делаем  json
        #сохранение новой заметки в БД
        #note = Notesdb(Title=title, Text=text, Image=filename)
        note = Notesdb(Title=title, Text=text, Image=imgsroadjs)
        db.session.add(note)
        db.session.commit()

        return redirect(url_for('index')) #render_teplate просто возвращает страницу, а redirect перенаправляет (меняется адресс)

    return render_template('newnote.html', form=form)

if __name__ == "__main__":
    app.config['WTF_CSRF_ENABLED']=False
    app.run(debug=True)