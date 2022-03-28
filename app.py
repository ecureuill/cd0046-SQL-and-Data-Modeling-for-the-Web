#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, make_response, jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
import logging
from logging import Formatter, FileHandler
from datetime import datetime
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object('config')

handler = logging.FileHandler("test.log")  # Create the file logger
app.logger.addHandler(handler)             # Add it to the built-in logger
app.logger.setLevel(logging.DEBUG)  

db = SQLAlchemy(app)

migrate = Migrate(app, db)
moment = Moment(app)
from model import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # app.logger.error("Something has gone very wrong")
  # app.logger.warning("You've been warned")
  # app.logger.info("Here's some info")
  # app.logger.debug("Meaningless debug information")
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  try:
    areas = Venue.query.distinct(Venue.city, Venue.state).all();
    data=[]
    for area in areas:
      area_dict = {
        "city": area.city,
        "state": area.state,
      }
      venues = Venue.query.filter_by(city=area.city, state=area.state)
      venue_list= [];
      for venue in venues:
        upcoming = Show.query.filter(Show.start_time>=datetime.today(),Show.venue_id==venue.id).count()
        venue_list.append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": upcoming,
        })
      area_dict["venues"] = venue_list
      data.append(area_dict)

  except Exception as e:
    print(e)
  finally:
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  venue_list=[]
  for venue in venues:
    upcoming = Show.query.filter(Show.start_time>=datetime.today(),Show.venue_id==venue.id).count()
    venue_list.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcoming,
    })

  response={
    "count": len(venues),
    "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    
  venue_data = Venue.query.filter_by(id=venue_id).first()
  upcoming = db.session.query(Show.start_time, Artist.id, Artist.name, Artist.image_link).join(Venue, Artist).filter(Show.start_time>=datetime.today(),Show.venue_id==venue_data.id).all()
  past = db.session.query(Show.start_time, Artist.id, Artist.name, Artist.image_link).join(Venue, Artist).filter(Show.start_time < datetime.today(),Show.venue_id==venue_data.id).all()
  
  upcoming_shows = []
  for start_time, artist_id, artist_name, image_link in upcoming:
    upcoming_shows.append(
      {
        "artist_id": artist_id,
        "artist_name": artist_name,
        "artist_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )

  past_shows = []
  for start_time, artist_id, artist_name, image_link in past:
    past_shows.append(
      {
        "artist_id": artist_id,
        "artist_name": artist_name,
        "artist_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )


  data={
    "id":venue_data.id,
    "name":venue_data.name,
    "genres": venue_data.genres.split(","),
    "address":venue_data.address,
    "city":venue_data.city,
    "state":venue_data.state,
    "phone":venue_data.phone,
    "website_link":venue_data.website_link,
    "facebook_link":venue_data.facebook_link,
    "seeking_talent":venue_data.looking,
    "seeking_description": venue_data.seeking_description,
    "image_link":venue_data.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form=VenueForm(request.form)
    venue = Venue(
      name=form.name.data,
      address=form.address.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      website_link=form.website_link.data,
      facebook_link=form.facebook_link.data,
      looking=form.seeking_talent.data,
      seeking_description=form.seeking_description.data,
      image_link=form.image_link.data,
      genres = ','.join(form.genres.data)
    )

    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not been listed!')
    abort(500)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('show_venue', venue_id=venue.id))
  finally:
    db.session.close()
  
@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    venue_name = venue.name
    db.session()
    delete_shows = Show.query.filter_by(venue_id=venue_id).delete()
    db.session.delete(venue)
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
    abort(404)
  else:
    return make_response(jsonify({}), 204)
  finally:
    db.session.close()


  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all();
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  artist_list=[]
  for artist in artists:
    upcoming = Show.query.filter(Show.start_time>=datetime.today(),Show.artist_id==artist.id).count()
    artist_list.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": upcoming,
    })

  response={
    "count": len(artists),
    "data": artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist_data = Artist.query.filter_by(id=artist_id).first()

  upcoming = db.session.query(Show.start_time, Venue.id, Venue.name, Venue.image_link).join(Venue, Artist).filter(Show.start_time>=datetime.today(),Show.artist_id==artist_data.id).all()
  past = db.session.query(Show.start_time, Venue.id, Venue.name, Venue.image_link).join(Venue, Artist).filter(Show.start_time<datetime.today(),Show.artist_id==artist_data.id).all()
  
  upcoming_shows = []
  for start_time, venue_id, venue_name, image_link in upcoming:
    upcoming_shows.append(
      {
        "venue_id": venue_id,
        "venue_name": venue_name,
        "venue_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )

  past_shows = []
  for start_time, venue_id, venue_name, image_link in past:
    past_shows.append(
      {
        "venue_id": venue_id,
        "venue_name": venue_name,
        "venue_image_link": image_link,
        "start_time": format_datetime(str(start_time))
      }
    )

  data={
    "id": artist_id,
    "name":artist_data.name,
    "genres":artist_data.genres.split(","),
    "city":artist_data.city,
    "state":artist_data.state,
    "phone":artist_data.phone,
    "website":artist_data.website_link,
    "facebook_link":artist_data.facebook_link,
    "seeking_venue":artist_data.looking,
    "seeking_description":artist_data.seeking_description,
    "image_link":artist_data.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  print(data)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).first()
  
  form.name.data=artist.name
  form.genres.data=artist.genres
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.website_link.data=artist.website_link
  form.facebook_link.data=artist.facebook_link
  form.seeking_venue.data=artist.looking
  form.seeking_description.data=artist.seeking_description
  form.image_link.data=artist.image_link
  form.genres.data=artist.genres
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.filter_by(id=artist_id).first()
    form=ArtistForm(request.form)
    
    artist.name=form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.website_link=form.website_link.data
    artist.facebook_link=form.facebook_link.data
    artist.looking= form.seeking_venue.data
    artist.seeking_description=form.seeking_description.data
    artist.image_link=form.image_link.data
    artist.genres = ",".join(form.genres.data)

    db.session()
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' was not updated!')
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))
  finally:
    db.session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  form.name.data =venue.name
  form.genres.data = venue.genres
  form.address.data =venue.address
  form.city.data =venue.city
  form.state.data =venue.state
  form.phone.data =venue.phone
  form.website_link.data =venue.website_link
  form.facebook_link.data =venue.facebook_link
  form.seeking_talent.data =venue.looking
  form.seeking_description.data = venue.seeking_description
  form.image_link.data =venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.filter_by(id=venue_id).first()
    form=VenueForm(request.form)
    
    venue.name=form.name.data
    venue.address=form.address.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.phone=form.phone.data
    venue.website_link=form.website_link.data
    venue.facebook_link=form.facebook_link.data
    venue.looking= form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data
    venue.image_link=form.image_link.data
    venue.genres = ','.join(form.genres.data)

    db.session()
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' was not updated!')
    abort(500)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))
  finally:
    db.session.close()


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form=ArtistForm(request.form)
    artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      website_link=form.website_link.data,
      facebook_link=form.facebook_link.data,
      looking=form.seeking_venue.data,
      seeking_description=form.seeking_description.data,
      image_link=form.image_link.data,
      genres = ','.join(form.genres.data)
    )

    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
    flash('An error occurred. Artist ' + request.form['name'] + ' could not been listed!')
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('show_artist', venue_id=artist.id))
  finally:
    db.session.close()
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = db.session.query(Show, Venue.name, Artist.name, Artist.image_link).join(Venue, Artist)

  # displays list of shows at /shows

  data_show=[]
  for show, venue_name, artist_name, image_link in shows:
    data_show.append({
    "venue_id":show.venue_id,
    "venue_name":venue_name,
    "artist_id":show.artist_id,
    "artist_name":artist_name,
    "artist_image_link":image_link,
    "start_time":format_datetime(str(show.start_time))
    })

  return render_template('pages/shows.html', shows=data_show)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  
  try:
    form = ShowForm(request.form)
    show = Show(
      venue_id=form.venue_id.data,
      artist_id=form.artist_id.data,
      start_time=form.start_time.data,
      )

    db.session.add(show)
    db.session.commit()
  except Exception as e:
    db.session.rollback()
    print(e)
    flash('An error occurred. Show could not been listed!')
    abort(500)
  else:
    flash('Show was successfully listed!')
    return redirect(url_for('shows', show_id=show.id))
  finally:
    db.session.close()

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
