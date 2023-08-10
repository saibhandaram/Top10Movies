from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6WlSihBXox7C0sKR6b'
Bootstrap5(app)

db = SQLAlchemy()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-movies-collection.db"

db.init_app(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    ranking = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()


class MovieForm(FlaskForm):
    title = StringField("Movie Title")
    year = StringField("Year")
    description = StringField("Description", validators=[validators.DataRequired()])
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    ranking = StringField("Ranking")
    img_url = StringField("Image Url")
    submit = SubmitField("Done")


# Adding Records to DB
#
# with app.app_context():
#     new_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(new_movie)
#     db.session.commit()


@app.route("/")
def home():
    all_movies = []
    with app.app_context():
        result = db.session.execute(db.select(Movie))
        # print(result)
        all_movies = result.scalars().all()
    return render_template("index.html", movies=all_movies)


@app.route("/add", methods=['GET', 'POST'])
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        with app.app_context():
            new_movie = Movie(
                title=form.title.data,
                year=form.year.data,
                description=form.description.data,
                rating=form.rating.data,
                review=form.review.data,
                ranking=form.ranking.data,
                img_url=form.img_url.data
            )
            db.session.add(new_movie)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form)


@app.route("/edit/<int:movie_id>", methods=['GET', 'POST'])
def update_rating(movie_id):
    print(movie_id)
    if request.method == 'GET':
        with app.app_context():
            result = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
        return render_template('edit.html', mov_id=result)
    else:
        with app.app_context():
            movie_to_update = db.session.execute(db.select(Movie).where(Movie.id == movie_id)).scalar()
            movie_to_update.review = request.form['new_review']
            movie_to_update.rating = request.form['new_rating']
            db.session.commit()
        return redirect(url_for('home'))


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
