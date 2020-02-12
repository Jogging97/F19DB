from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from wtforms import Form, StringField, SelectField

app = Flask(__name__)
app.secret_key = 'CS542'

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/music'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Tables #


# tracks handles many-to-many relationship between Track and Playlist
pl_tracks = db.Table('pl_tracks',
                     db.Column('rID', db.Integer),
                     db.Column('tPosition', db.Integer),
                     db.Column('pName', db.String),
                     db.Column('uUsername', db.String),
                     db.ForeignKeyConstraint(['pName', 'uUsername'], ['playlist.pName', 'playlist.uUsername']),
                     db.ForeignKeyConstraint(['tPosition', 'rID'], ['track.tPosition', 'track.rID']),
                     db.PrimaryKeyConstraint('tPosition', 'pName', 'uUsername', 'rID', name='tracks_pk_constraint'))


class Playlist(db.Model):
    __tablename__ = 'playlist'
    __table_args__ = (db.ForeignKeyConstraint(['uUsername'], ['users.uUsername']),
                      db.PrimaryKeyConstraint('pName', 'uUsername', name='playlist_pk_constraint'))

    pName = db.Column(db.String)
    uUsername = db.Column(db.String)
    tracks = db.relationship('Track', secondary=pl_tracks, lazy='subquery',
                             backref=db.backref('track', lazy=True))


class Track(db.Model):
    __tablename__ = 'track'
    __table_args__ = (db.ForeignKeyConstraint(['rID'], ['release.rID']),
                      db.PrimaryKeyConstraint('rID', 'tPosition', name='track_pk_constraint'),
                      db.UniqueConstraint('rID', 'tPosition', name='track_unique_constraint'))
    rID = db.Column(db.Integer)
    tPosition = db.Column(db.Integer)
    tURL = db.Column(db.Text)
    tName = db.Column(db.Text)
    tDuration = db.Column(db.Text)


class User(db.Model):
    __tablename__ = 'users'
    uUsername = db.Column(db.Text, primary_key=True)
    uName = db.Column(db.Text, nullable=False)
    uPassword = db.Column(db.Text)

    reviews = db.relationship('Review', backref=db.backref('user'))
    logs = db.relationship('Log', backref=db.backref('user'))


class Release(db.Model):
    __tablename__ = 'release'
    __table_args__ = (db.ForeignKeyConstraint(['aID'], ['artist.aID']),
                      db.ForeignKeyConstraint(['lID'], ['label.lID']),
                      db.ForeignKeyConstraint(['gName'], ['genre.gName']))

    rID = db.Column(db.Integer, primary_key=True)
    rDate = db.Column(db.Text)
    rStyle = db.Column(db.Text)
    rCountry = db.Column(db.Text)
    rCount = db.Column(db.Integer, nullable=False)
    rName = db.Column(db.Text, nullable=False)
    aID = db.Column(db.Integer)
    lID = db.Column(db.Integer)
    gName = db.Column(db.Text)
    rReviewCount = db.Column(db.Integer)


class Artist(db.Model):
    __tablename__ = 'artist'
    aID = db.Column(db.Integer, primary_key=True)
    aName = db.Column(db.Text, nullable=False)

    members = db.relationship('Member', backref=db.backref('artist'))
    releases = db.relationship('Release', backref=db.backref('artist'))


class Member(db.Model):
    __tablename__ = 'member'
    __table_args__ = (db.ForeignKeyConstraint(['aID'], ['artist.aID']),
                      db.PrimaryKeyConstraint('aID', 'mName', name='member_pk_constraint'))
    aID = db.Column(db.Integer)
    mName = db.Column(db.Text, nullable=False)


class Label(db.Model):
    __tablename__ = 'label'
    lID = db.Column(db.Integer, primary_key=True)
    lName = db.Column(db.Text, nullable=False)
    lURL = db.Column(db.Text)

    releases = db.relationship('Release', backref=db.backref('label'))


class Genre(db.Model):
    __tablename__ = 'genre'
    gName = db.Column(db.Text, primary_key=True)
    gURL = db.Column(db.Text)

    releases = db.relationship('Release', backref=db.backref('genre'))


class Review(db.Model):
    __tablename__ = 'review'
    __table_args__ = (db.ForeignKeyConstraint(['rID'], ['release.rID']),
                      db.ForeignKeyConstraint(['uUsername'], ['users.uUsername']),
                      db.PrimaryKeyConstraint('rID', 'uUsername', name='review_pk_constraint'),
                      db.CheckConstraint('r_Rating' in (1, 2, 3, 4, 5), name='review_chk_constraint'))

    rID = db.Column(db.Integer)
    uUsername = db.Column(db.Text)
    rDate = db.Column(db.Date)
    rText = db.Column(db.Text)
    r_Rating = db.Column(db.Integer)


class Log(db.Model):
    __tablename__ = 'log'
    __table_args__ = (db.ForeignKeyConstraint(['uUsername'], ['users.uUsername']),
                      db.PrimaryKeyConstraint('uUsername', 'lDate', 'lMessage', name='log_pk_constraint'))

    uUsername = db.Column(db.Text, nullable=False)
    lDate = db.Column(db.Date, nullable=False)
    lMessage = db.Column(db.Text, nullable=False)


# Search Form #

class MusicSearchForm(Form):
    select = SelectField('Search for music:')
    search = StringField('')



@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        uUsername_ = request.form['uUsername']
        uPassword_ = request.form['password']

        user = User.query.filter(User.uUsername == uUsername_, User.uPassword == uPassword_).limit(1).all()

        if len(user) > 0:
            return render_template('songs.html', songs=[])
        else:
            flash('Wrong Credentials: Try Again')
            return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        uUsername_ = request.form['uUsername']
        password1_ = request.form['password1']
        password2_ = request.form['password2']

        user = User.query.filter(User.uUsername == uUsername_).limit(1).all()

        if len(user) > 0:
            flash('Change Username: There is already other account with the same username.')
            return render_template('signup.html')
        else:
            if password1_ != password2_:
                flash("Error: Passwords do not match")
                return render_template('signup.html')

            else:
                # Add the username and password to the database
                newUser = User(uUsername=uUsername_, uPassword=password1_, uName='t')

                db.session.add(newUser)
                db.session.commit()
                flash('New user successfully registered')
                return render_template('login.html')


# 1. search releases by title / artist name / genre
@app.route('/releases', methods = ['GET', 'POST'])
def releases():
    if request.method == 'GET':
        return render_template('releases.html', releases=[])

    else:
        aName = request.form['artist']
        rName = request.form['album']
        gName = request.form['genre']

        releases_results = []
        releases = {}

        if len(rName) > 0 and len(gName) == 0 and len(aName) == 0:
            releases = Release.query.filter(Release.rName.match(rName)).join(Artist, Artist.aID == Release.aID).limit(10).all()

        elif len(rName) == 0 and len(gName) > 0 and len(aName) == 0:
            releases = Release.query.filter(Release.gName.match(gName)).join(Artist, Artist.aID == Release.aID).limit(10).all()

        elif len(rName) == 0 and len(gName) == 0 and len(aName) > 0:

            releases = Release.query.join(Artist, Artist.aID == Release.aID).filter(Artist.aName == aName).limit(10).all()

        elif len(rName) > 0 and len(gName) > 0 and len(aName) == 0:
            releases = Release.query.filter(Release.rName.match(rName), Release.gName == gName).join(Artist, Artist.aID == Release.aID).limit(50).all()

        elif len(rName) > 0 and len(gName) == 0 and len(aName) > 0:
            releases = Release.query.join(Artist, Release.aID == Artist.aID).filter(Release.rName.match(rName),
                                                                                    Artist.aName == aName).limit(10).all()

        elif len(rName) == 0 and len(gName) > 0 and len(aName) > 0:
            releases = Release.query.join(Artist, Release.aID == Artist.aID).filter(Release.gName.match(gName),
                                                                                    Artist.aName == aName).limit(10).all()

        elif len(rName) > 0 and len(gName) > 0 and len(aName) > 0:
            releases = Release.query.join(Artist, Release.aID == Artist.aID).filter(Release.rName.match(rName),
                                                                                    Release.gName == gName,
                                                                                    Artist.aName == aName).limit(10).all()

        for r in releases:
            review = Review.query.filter(Review.uUsername == 'user123', Review.rID == r.rID).limit(1).all()
            release_dict = {'rID': r.rID, 'rDate': r.rDate, 'rStyle': r.rStyle, 'rCountry': r.rCountry,
                            'rCount': r.rCount, 'rName': r.rName, 'aID': r.aID, 'lID': r.lID,
                            'gName': r.gName, 'rReviewCount': r.rReviewCount, 'aName': r.artist.aName}
            
            if len(review) > 0:
                release_dict['rText'] = review[0].rText
                release_dict['rRating'] = review[0].r_Rating
            else:
                release_dict['rText'] = ''
                release_dict['rRating'] = ''
            
            releases_results.append(release_dict)

        return render_template('releases.html', releases=releases_results)


# 2. search tracks by title / artist name / release / genre
@app.route('/s_search', methods = ['GET', 'POST'])
def s_search():
    if request.method == 'GET':
        return render_template('songs.html', songs=[])

    else:
        tName = request.form['song']
        aName = request.form['artist']
        rName = request.form['album']
        gName = request.form['genre']

        tracks_results = []
        tracks = {}

        if len(tName) > 0 and len(rName) == 0 and len(gName) == 0 and len(aName) == 0:
            tracks = Track.query.filter(Track.tName == tName).join(Release, Track.rID == Release.rID).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) == 0 and len(rName) > 0 and len(gName) == 0 and len(aName) == 0:
            tracks = Track.query.join(Release, Track.rID == Release.rID).filter(Release.rName == rName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) == 0 and len(rName) == 0 and len(gName) == 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) > 0 and len(rName) > 0 and len(gName) == 0 and len(aName) == 0:
            tracks = Track.query.join(Release, Track.rID == Release.rID).filter(Track.tName == tName,
                                                                                Release.rName == rName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) > 0 and len(rName) == 0 and len(gName) > 0 and len(aName) == 0:
            tracks = Track.query.join(Release, Track.rID == Release.rID).filter(Track.tName == tName,
                                                                                Release.gName == gName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) > 0 and len(rName) == 0 and len(gName) == 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Track.tName == tName,
                                                                                            Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) == 0 and len(rName) > 0 and len(gName) > 0 and len(aName) == 0:
            tracks = Track.query.join(Release, Track.rID == Release.rID).filter(Release.rName == rName,
                                                                                Release.gName == gName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) == 0 and len(rName) > 0 and len(gName) == 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Release.rName == rName,
                                                                                            Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) == 0 and len(rName) == 0 and len(gName) > 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Release.gName == gName,
                                                                                            Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) > 0 and len(rName) > 0 and len(gName) > 0 and len(aName) == 0:
            tracks = Track.query.join(Release, Track.rID == Release.rID).filter(Track.tName == tName,
                                                                                Release.rName == rName,
                                                                                Release.gName == gName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) > 0 and len(rName) > 0 and len(gName) == 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Track.tName == tName,
                                                                                            Release.rName == rName,
                                                                                            Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) > 0 and len(rName) == 0 and len(gName) > 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Track.tName == tName,
                                                                                            Release.gName == gName,
                                                                                            Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) == 0 and len(rName) > 0 and len(gName) > 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Release.rName == rName,
                                                                                            Release.gName == gName,
                                                                                            Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        elif len(tName) > 0 and len(rName) > 0 and len(gName) > 0 and len(aName) > 0:
            tracks = Track.query.join(Release).join(Artist, Release.aID == Artist.aID).filter(Track.tName == tName,
                                                                                            Release.rName == rName,
                                                                                            Release.gName == gName,
                                                                                            Artist.aName == aName).add_columns(Release.rName, Track.tName, Track.tPosition, Track.tDuration, Track.rID).limit(50).all()

        for t in tracks:
            print(dir(t))
            tracks_dict = {'tPosition': t.tPosition, 'tName': t.tName,
                        'tDuration': t.tDuration, 'rName': t.rName, 'rID': t.rID}
            tracks_results.append(tracks_dict)

        playlists_list = []
        playlists = Playlist.query.filter(Playlist.uUsername == 'user123').all()
        for p in playlists:
            playlists_list.append({'pName': p.pName})

        return render_template('songs.html', songs=tracks_results, playlists=playlists_list)


# Takes a username and a release ID and returns the given user's
# review of the given release.
@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'GET':
        uUsername_ = 'user123'

        reviews = Review.query.filter_by(uUsername=uUsername_).join(Release, Release.rID == Review.rID).add_columns(Release.rName, Review.rText, Review.r_Rating).all()

        review_list = []
        for r in reviews:
            review_dict = {'rName': r.rName, 'rText': r.rText, 'rRating': r.r_Rating}
            review_list.append(review_dict)

        return render_template('reviews.html', reviews=review_list)

    else:
        uUsername_ = 'user123'
        rID_ = request.form['rID']
        rText_ = request.form['rText']
        rRating_ = request.form['rating']

        review = Review.query.filter_by(uUsername=uUsername_, rID=rID_).limit(1).all()

        if len(review) > 0:
            # Update
            review[0].rText = rText_
            review[0].r_Rating = rRating_
            review[0].rDate = '1998-04-07'
            db.session.commit()
        else:
            # Insert
            newReview = Review(rID=rID_, uUsername=uUsername_, rDate='2000-12-31',
                               rText=rText_, r_Rating=rRating_)

            db.session.add(newReview)
            db.session.commit()

        return render_template('releases.html', releases=[])

@app.route('/playlist', methods=['GET', 'POST'])
def playlist(rm=''):
    if request.method == 'GET' or rm == 'GET':
        uUsername_ = 'user123'

        playlists = Playlist.query.filter_by(uUsername=uUsername_).join(pl_tracks, 
                    and_(Playlist.uUsername == pl_tracks.c.uUsername, Playlist.pName == pl_tracks.c.pName)).join(Track,
                    and_(Track.rID == pl_tracks.c.rID, Track.tPosition == pl_tracks.c.tPosition)).all()

        playlist_list = []

        for p in playlists:
            tracks = []
            for t in p.tracks:
                r = Release.query.filter(Release.rID == t.rID).limit(1).all()
                tracks.append({'rName': r[0].rName, 'tName': t.tName, 'rID': t.rID, 'tPosition': t.tPosition})
            playlist_dict = {'pName': p.pName, 'uUsername': p.uUsername, 'pTracks': tracks}
            playlist_list.append(playlist_dict)

        return render_template('playlist.html', playlists=playlist_list)
        
    else:
        # Create a playlist for user with name
        uUsername_ = 'user123'
        pName_ = request.form['pName']

        newPlaylist = Playlist(uUsername=uUsername_, pName=pName_)
        db.session.add(newPlaylist)
        db.session.commit()

        return render_template('songs.html')

@app.route('/playlistcontains', methods = ['GET', 'POST'])
def playlistcontains():
    operation_ = request.form['operation']
    rID_ = request.form['rID']
    tPosition_ = request.form['tPosition']
    pName_ = request.form['pName']
    uUsername_ = 'user123'

    if operation_ == 'insert':
        q = pl_tracks.insert().values({'rID': rID_, 'tPosition': tPosition_, 'pName': pName_, 'uUsername': uUsername_})
        db.session.execute(q)
        db.session.commit()
        return render_template('songs.html', songs=[])
    else:
        q = pl_tracks.delete().where(and_(pl_tracks.c.rID == rID_, pl_tracks.c.tPosition == tPosition_,
                                 pl_tracks.c.pName == pName_, pl_tracks.c.uUsername == uUsername_))
        db.session.execute(q)
        db.session.commit()
        return playlist('GET')
        return render_template('playlist.html')


if __name__ == '__main__':
    app.run(debug=True)

"""
from app import db

db.create_all()
"""
