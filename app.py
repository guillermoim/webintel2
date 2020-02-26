from flask import Flask, render_template, flash, redirect, url_for, request, session

from wtforms import Form, StringField, validators

app = Flask(__name__)

class Formulario(Form):

    search = StringField(label='Search term...', validators=[validators.DataRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():

    form = Formulario(request.form)

    if request.method=='POST' and form.validate():
        results = ['res0', 'res2']
        return render_template('results.html', form=form, results=results)

    return render_template('home.html', form = form)

@app.route('/about')
def about():

    return render_template('about.html')


if __name__=='__main__':
    app.run(debug=True)