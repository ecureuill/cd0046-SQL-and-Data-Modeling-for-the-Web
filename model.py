from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)

migrate = Migrate(app, db)
moment = Moment(app)

# class Genres(db.Model):
#     __tablename__ = 'Genres'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     # venues = relationship('Venues', secondary=VenueGenres, backref='Genres')

# class VenueGenres(db.Model):
#     __tablename__ = 'VenueGenres'
#     id = db.Column(db.Integer, primary_key=True, index=True)
#     venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
#     genre_id = db.Column(db.Integer, db.ForeignKey('Genres.id'), nullable=False)

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    looking = db.Column(db.Boolean)
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    # genres = db.relationship('Genres', secondary=VenueGenres, backref='Venue')
    shows = db.relationship('Show', backref='Venue', lazy=True)

# class ArtistGenres(db.Model):
#     __tablename__ = 'ArtistGenres'
#     id = db.Column(db.Integer, primary_key=True, index=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
#     genre_id = db.Column(db.Integer, db.ForeignKey('Genres.id'), nullable=False)

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    phone = db.Column(db.String(15))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    # genres = db.relationship('Genres', secondary=ArtistGenres, backref='Artist')
    shows = db.relationship('Show', backref='Artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    atist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
