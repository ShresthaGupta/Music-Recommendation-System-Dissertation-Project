# from check import data
from typing import Dict, Any

import spotipy
from flask import Flask, render_template, url_for, redirect, session, request,flash
from flask_sqlalchemy import SQLAlchemy
from spotipy.oauth2 import SpotifyClientCredentials
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from engine import recommend_songs, data,catch_recommended

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="9eb499b93cb44edebec7c7391b421341",
                                                           client_secret="03e2d9e4eb0746f98a4f7abddf2008b7"))
import datetime
from cold_start import get_artists, get_tracks, more_songs,uri_data,range_years

# global variables
songs = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'amrpaglimum'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class user(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True)
    email = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(256))
    count = db.Column(db.Integer, default=0)
    dob = db.Column(db.String(15))


class data(db.Model):
    __tablename__ = 'userdata'
    data_id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(20),default=None)
    artist = db.Column(db.String(200),default=None)
    liked_songs = db.Column(db.String(10000),default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    request = db.relationship("user", backref=backref("account", uselist=False))


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/logout")
def logout():
    login = user.query.filter_by(id=session['userid']).first()
    if login is not None:
        session['login'] = False
        session['userid'] = None
        session.clear()
    return redirect(url_for('home'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]
        login = user.query.filter_by(username=uname).first()
        if login is not None:
            if check_password_hash(login.password, passw):
                session['login'] = True
                session['userid'] = login.id
                if login.count == 0:
                    login.count = login.count + 1
                    db.session.add(login)
                    db.session.commit()
                    genres = ['pop', 'hip-hop','r and b', 'soul', 'jazz', 'rock', 'edm', 'folk', 'alternative', 'metal',
                              'punk', 'latin', 'hindustani', 'filmi']
                    genre = {
                        'genre': genres
                    }
                    return render_template('home.html', result=genre)
                else:
                    login.count = login.count + 1
                    db.session.add(login)
                    db.session.commit()
                    return redirect('/profile')
            else:
               flash('wrong password!','danger')
        else:
            flash('wrong username!register yourself 1st','danger')
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']
        dob = request.form['dob']

        hash_passw = generate_password_hash(passw, method='sha256')
        reg1 = user.query.filter_by(username=uname).first()
        reg2 = user.query.filter_by(email=mail).first()
        if reg1 or reg2 is None:
            register = user(username=uname, email=mail, password=hash_passw, dob=dob)
            db.session.add(register)
            db.session.commit()
            flash("Successfully Registered! To proceed,login", 'success')
            return redirect(url_for("login"))
        else:
                flash("Already Registered Proceed to login", 'success')
    return render_template("register.html")

#gets genre from end-user and sends artist names from dataset based on that genre
@app.route('/rating',methods=["GET", "POST"])
def rating():
    global result1
    if session['login']:
        if request.method == 'POST':
            rating = request.form
        else:
            rating = request.args.get('genre')
        id1=session['userid']
        #addition of genre to db
        gen = data.query.filter_by(user_id=id1).first()
        if gen is None:
            gen1 = data(user_id=id1, genre=rating)
            db.session.add(gen1)
            db.session.commit()
        else:
            gen.genre = rating
            db.session.add(gen)
            db.session.commit()
        user1 = user.query.filter_by(id=id1).first()
        dob = user1.dob
        dobyear = int(dob.split('-')[0])
        years=range_years(dobyear)
        result1 = get_artists(rating,years)
        return render_template('artist.html', result=result1)
    else:
        return redirect(url_for('login'))


#gets artist from user and send some songs of that artist in a particular range of year
@app.route('/artist', methods=['POST', 'GET'])
def artist():
    if session['login']:
        if request.method == 'POST':
            artist = request.form['artist']
        else:
            artist = request.args.get('artist')
        user1 = data.query.filter_by(user_id=session['userid']).first()
        user1.artist=artist
        gen = user1.genre
        db.session.add(user1)
        db.session.commit()
        user2 = user.query.filter_by(id=session['userid']).first()
        dob = user2.dob
        dobyear = int(dob.split('-')[0])
        years = range_years(dobyear)
        songs = get_tracks(artist,'artist',years)
        song_length = len(songs)
        if (song_length > 10):
            song_length = 10
        artistedSongs_dict = {
            'songs': songs,
            'songs_length':song_length
        }
        return render_template('rating.html', result=artistedSongs_dict)

    else:
        return redirect(url_for('login'))
        #return artist

@app.route('/result', methods=['POST', 'GET'])
def result():
    if session['login']:
        if request.method == 'POST':
            requested = request.form
            if requested is not None:
                liked_uri = [v for k, v in requested.items()]
                x = liked_uri
                user = data.query.filter_by(user_id=session['userid']).first()
                if user.liked_songs is not None:
                    liked_songs_string=user.liked_songs
                    liked_songs_list=liked_songs_string.split(',')
                    combined_uris = liked_songs_list + liked_uri
                    x=list(set(combined_uris))
                liked_songs = ','.join(map(str, x))
                user.liked_songs = liked_songs
                db.session.add(user)
                db.session.commit()
                song_details = more_songs(liked_uri)
                display = catch_recommended(song_details)
                displayDict = {'display': display}
                return render_template('recommended.html', songs=displayDict)
    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if session['login']:
        user_iden=user.query.filter_by(id=session['userid']).first()
        name=user_iden.username
        gc = 0
        ac = 0
        lc = 0
        genre_list = []
        artist_list = []
        my_playlist = []
        playlist_length = 0
        user_data=data.query.filter_by(user_id=session['userid']).first()
        if user_data is not None:
            artist=user_data.artist
            genre=user_data.genre
            uris=user_data.liked_songs
        if genre is not None:
            gc = 1
            genre_list=get_tracks(genre,'genre',None)
            if artist is not None:
                ac = 1
                artist_list=get_tracks(artist,'artist',None)
                artist_len=len(artist_list)
                if(artist_len > 10):
                    artist_len=10
                if uris is not None:
                    lc = 1
                    uri_list = uris.split(",")
                    my_liked_songs = uri_data(uri_list)
                    display = catch_recommended(my_liked_songs)
                    my_playlist = my_liked_songs + display
                    playlist_length = len(my_playlist)

        playlist_dict = {
            'user':name,
            'playlist':my_playlist,
            'length':playlist_length,
            'artist':artist,
            'artist_songs':artist_list,
            'artist_len':artist_len,
            'genre':genre,
            'genre_songs':genre_list,
            'gc':gc,
            'ac':ac,
            'rc':lc
                        }
        if user_iden.count in range(0,2):
            return render_template('profile1.html', songs = playlist_dict)
        else:
            return render_template('profile2.html', songs=playlist_dict)

    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    db.create_all()
    app.run()
