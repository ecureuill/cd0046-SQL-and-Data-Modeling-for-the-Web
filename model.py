from app import db

class Venue(db.Model):
    __tablename__ = 'venue'
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
    shows = db.relationship('show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<id: {self.id}, name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artist'
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
    shows = db.relationship('show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    atist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)