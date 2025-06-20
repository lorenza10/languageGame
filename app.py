from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wonderwords import RandomSentence
from translate import Translator
import json
import random
import config


app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key

# Create a Form Class
# class NamerForm(FlaskForm):
#     name = StringField ("What is your name?", validators=[DataRequired()])
#     submit = SubmitField("Submit")


class TranslateForm(FlaskForm):
    input_sentence = StringField ("Translate this sentense")
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

    # GET request: generate a new challenge
    s = RandomSentence()
    newSentence = s.sentence()

    # Load languages
    with open('languagecodes.json', 'r') as file:
        data = json.load(file)

    randNum = random.randrange(1, 137)
    languageCode = data[randNum]["code"]
    language = data[randNum]["language"]

    # Store language for POST comparison
    session['language'] = language
    # print(language)

    # Translate the sentence
    translator = Translator(to_lang=languageCode)
    try:
        translation = translator.translate(newSentence)
    except Exception as e:
        print(f"Translation error: {e}")
        translation = "[Error translating]"

    # Get result message from session (if any)
    result = session.pop('result', None)

    return render_template("index.html", translation=translation, form=form, result=result)

