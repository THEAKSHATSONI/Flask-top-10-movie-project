from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import desc
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


#--------------------- API Key by themoviedb ----------------------#
API = "fde443e5cbc57122dd15a46d3604e90e"


#--------------------- Application start ---------------------------#
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

db = SQLAlchemy()
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie.db"
# initialize the app with the extension
db.init_app(app)


#------------------- database ORM ------------------------#
class Movie(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.String)
    description = db.Column(db.String)
    rating = db.Column(db.String)
    ranking = db.Column(db.String)
    review = db.Column(db.String)
    img_url = db.Column(db.String)


with app.app_context():
    db.create_all()


#----------------------- wtform -------------------#
class rating_and_review(FlaskForm):

    rating_update = StringField(label="Your rating out of 10. e.g. 7.5",validators=[DataRequired()])
    review_update = StringField(label="Your Review", validators=[DataRequired()])
    submit_button = SubmitField(label='Submit')

class movie_add(FlaskForm):

    movie_title = StringField(label="Movie Title",validators=[DataRequired()])
    submit_button = SubmitField(label='Add Movie')


# for reading the database
with app.app_context():
    movie_data = db.session.query(Movie).order_by(desc(Movie.rating)).all()


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.commit()


for data in movie_data:
    print(data)

@app.route("/")
def home():
    return render_template("index.html",datas=movie_data)



@app.route("/delete/<int:id>")
def delete(id):

    with app.app_context():
        movie_to_delete = Movie.query.get(id)
        print(movie_to_delete)
        db.session.delete(movie_to_delete)
        db.session.commit()

    return redirect(url_for("home"))



@app.route("/add", methods=["POST","GET"])
def add():

    movie_add_form = movie_add()
    print(movie_add_form.movie_title.data)
    print(request.method )

    if request.method == "POST":
        url = "https://api.themoviedb.org/3/search/multi"
        param = {
                    "api_key": API,
                    "query": movie_add_form.movie_title.data
                }

        web_data = requests.get(url,params=param)

        return render_template('select.html',web_data=web_data.json()['results'])

    return render_template("add.html",form=movie_add_form)



@app.route('/select/<int:id>')
def select(id):

    url = f"https://api.themoviedb.org/3/movie/{id}?api_key={API}"
    print(url)

    print(requests.get(url).json())


    new_movie = Movie(
                    title = requests.get(url).json()["title"],
                    img_url = f"https://image.tmdb.org/t/p/w500{ requests.get(url).json()['poster_path'] }",
                    rating = requests.get(url).json()["vote_average"],
                    ranking = 10,
                    year = requests.get(url).json()["release_date"],
                    description = requests.get(url).json()["overview"]
                    )

    print(new_movie)

    with app.app_context():
        db.session.add(new_movie)
        db.session.commit()

    movie_id = db.session.query(Movie).filter_by(title= requests.get(url).json()["title"]).first()
    print("movie_id",)

    return redirect(url_for('edit',id = movie_id.id))

@app.route("/edit/<int:id>",methods=["POST","GET"])
def edit(id):

    form = rating_and_review()

    if request.method == "POST":

        with app.app_context():

            movie_to_update =Movie.query.filter_by(id=id).first()
            # print(movie_to_update.rating)

            movie_to_update.rating = form.rating_update.data
            # print(movie_to_update.rating)

            movie_to_update.review = form.review_update.data
            # print(movie_to_update.review)

            db.session.commit()

            return redirect(url_for('home'))

    return render_template("edit.html",form=form,data=movie_data,id=id)




if __name__ == '__main__':
    app.run(debug=True)
