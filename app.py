from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wonderwords import RandomSentence
from translate import Translator
import json
import random
import os
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devkey123')

# Logging for debugging
logging.basicConfig(level=logging.INFO)

class TranslateForm(FlaskForm):
    input_sentence = StringField("Translate this sentence")
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

    max_attempts = 10
    for _ in range(max_attempts):
        choice = random.choice(data)
        languageCode = choice["code"]
        language = choice["language"]

        if len(languageCode) == 2:
            break
    else:
        language = "english"
        languageCode = "en"

    session['language'] = language

    try:
        translator = Translator(to_lang=languageCode)
        translation = translator.translate(newSentence)
    except Exception as e:
        logging.error(f"Translation error: {e}")
        translation = "[Error translating]"

    result = session.pop('result', None)

    return render_template("index.html", translation=translation, form=form, result=result)