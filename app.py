from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wonderwords import RandomSentence
from googletrans import Translator
import json
import random
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


class TranslateForm(FlaskForm):
    input_sentence = StringField("Guess the language", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/', methods=['GET', 'POST'])
def translate():
    form = TranslateForm()

    if request.method == 'POST' and form.validate_on_submit():
        userAnswer = form.input_sentence.data
        language = session.get('language')

        if userAnswer and language and userAnswer.strip().lower() == language.strip().lower():
            session['result'] = '✅ You guessed correctly!'
        else:
            session['result'] = f"❌ No, it was <strong>{language}</strong>"

        return redirect(url_for('translate'))

    s = RandomSentence()
    newSentence = s.sentence()

    with open('languagecodes.json', 'r') as file:
        data = json.load(file)

    randNum = random.randrange(1, len(data))
    languageCode = data[randNum]["code"]
    language = data[randNum]["language"]

    session['language'] = language

    translator = Translator()
    try:
        translation_obj = translator.translate(newSentence, dest=languageCode)
        translation = translation_obj.text
    except Exception as e:
        print(f"Translation error: {e}")
        translation = "[Error translating]"

    result = session.pop('result', None)

    return render_template("index.html", translation=translation, form=form, result=result)
