#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.String())
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    @hybrid_property
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'address': self.address,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres.split(','),
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'num_upcoming_shows': self.get_upcoming_shows_count()
        }

    @hybrid_property
    def format_short(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': self.get_upcoming_shows_count()
        }


    #   Using hybrid_property to be able call these function in the controllers below
    @hybrid_property
    def format_full(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(','),
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'past_shows': [show.format for show in self.get_past_shows()],
            'upcoming_shows': [show.format for show in self.get_upcoming_shows()],
            'past_shows_count': self.get_past_shows_count(),
            'upcoming_shows_count': self.get_upcoming_shows_count()
        }

    #   This function will call upon `get_venues_in_area` as a helper function to ease formatting venues by cities and states
    @hybrid_property
    def format_by_area(self):
        return {
            'city': self.city,
            'state': self.state,
            'venues': [venue.format_short for venue in self.get_venues_in_area()]
        }

    #   A helper function when I am trying to format correctly the venues so they display per city and state
    def get_venues_in_area(self):
        return Venue.query.filter(Venue.city == self.city, Venue.state == self.state).all()

    def get_past_shows(self):
        return Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == self.id).all()

    def get_upcoming_shows(self):
        return Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == self.id).all()

    def get_past_shows_count(self):
        return len(Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == self.id).all())

    def get_upcoming_shows_count(self):
        return len(Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == self.id).all())



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    @hybrid_property
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'genres': self.genres.split(','),
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'num_upcoming_shows': self.get_upcoming_shows_count()
        }

    @hybrid_property
    def format_short(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': self.get_upcoming_shows_count()
        }

    @hybrid_property
    def format_full(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(','),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'past_shows': [show.format for show in self.get_past_shows()],
            'upcoming_shows': [show.format for show in self.get_upcoming_shows()],
            'past_shows_count': self.get_past_shows_count(),
            'upcoming_shows_count': self.get_upcoming_shows_count()
        }

    def get_past_shows(self):
        return Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == self.id).all()

    def get_upcoming_shows(self):
        return Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == self.id).all()

    def get_past_shows_count(self):
        return len(Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == self.id).all())

    def get_upcoming_shows_count(self):
        return len(Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == self.id).all())


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    @hybrid_property
    def format(self):
        return {
            'id': self.id,
            'venue_id': self.venue_id,
            'venue_name': self.get_venue_name(),
            'venue_image_link': self.get_venue_image(),
            'artist_id': self.artist_id,
            'artist_name': self.get_artist_name(),
            'artist_image_link': self.get_artist_image(),
            'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        }

    def get_venue_name(self):
        venue = Venue.query.get(self.venue_id)
        return venue.name

    def get_artist_name(self):
        artist = Artist.query.get(self.artist_id)
        return artist.name

    def get_artist_image(self):
        artist = Artist.query.get(self.artist_id)
        return artist.image_link

    def get_venue_image(self):
        venue = Venue.query.get(self.venue_id)
        return venue.image_link

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # Query to capture Lists of venues in each area
  venues_by_area = Venue.query.distinct(Venue.city, Venue.state).all()
  # Loop through each area to format correctly for display
  data = [venue.format_by_area for venue in venues_by_area]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_string = request.form.get('search_term', None)
  venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_string))).all()
  response = {
    "count": len(venues),
    "data": [venue.format_short for venue in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  if venue is None:
      flash('An error occurred. Venue does not exist!')
      return render_template('pages/home.html')
  data = venue.format_full
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  try:
    new_data = VenueForm(request.form)
    venue = Venue(name=new_data.name.data,
        city=new_data.city.data,
        state=new_data.state.data,
        address=new_data.address.data,
        phone=new_data.phone.data,
        genres=','.join(new_data.genres.data),
        facebook_link=new_data.facebook_link.data,
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + new_data.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + new_data.name.data + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      Venue.query.filter(Venue.id == venue_id).delete()
      db.session.commit()
      flash('Venue number ' + venue_id + ' was successfully deleted')
  except:
      db.session.rollback()
      flash('An error occurred! Venue number ' + venue_id + ' was not deleted')
  finally:
      db.session.close()
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  data = [artist.format_short for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  search_string = request.form.get('search_term', None)
  artists = Artist.query.filter(Artist.name.ilike("%{}%".format(search_string))).all()
  response = {
    "count": len(artists),
    "data": [artist.format_short for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  artist = Artist.query.get(artist_id)
  if artist is None:
        flash('An error occurred. Artist does not exist!')
        return render_template('pages/home.html')
  data = artist.format_full
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  if artist is None:
        flash('An error occurred. Artist does not exist!')
        return render_template('pages/home.html')
  artist = artist.format
  form = ArtistForm(data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist_form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    artist.name = artist_form.name.data
    artist.city = artist_form.city.data
    artist.state = artist_form.state.data
    artist.phone = artist_form.phone.data
    artist.facebook_link = artist_form.facebook_link.data
    artist.genres = ','.join(artist_form.genres.data)
    db.session.add(artist)
    db.session.commit()
    # on successful db update, flash success
    flash('Artist ' + artist_form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    # DONE: on unsuccessful db update, flash an error instead.
    flash('An error occurred. Artist ' + artist_form.name.data + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  if venue is None:
        flash('An error occurred. Venue does not exist!')
        return render_template('pages/home.html')
  venue = venue.format
  form = VenueForm(data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue_form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue.name = venue_form.name.data
    venue.city = venue_form.city.data
    venue.state = venue_form.state.data
    venue.phone = venue_form.phone.data
    venue.address = venue_form.address.data
    venue.facebook_link = venue_form.facebook_link.data
    venue.genres = ','.join(venue_form.genres.data)
    db.session.add(venue)
    db.session.commit()
    # on successful db update, flash success
    flash('Venue ' + venue_form.name.data + ' was successfully updated!')
  except:
    db.session.rollback()
    # DONE: on unsuccessful db update, flash an error instead.
    flash('An error occurred. Venue ' + venue_form.name.data + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    new_data = ArtistForm(request.form)
    artist = Artist(name=new_data.name.data,
        city=new_data.city.data,
        state=new_data.state.data,
        phone=new_data.phone.data,
        genres=','.join(new_data.genres.data),
        facebook_link=new_data.facebook_link.data,
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + new_data.name.data + ' was successfully listed!')
  except:
    db.session.rollback()
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + new_data.name.data + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = db.session.query(Show).order_by(Show.start_time)
  data=[show.format for show in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    new_data = ShowForm(request.form)
    show = Show(
            artist_id=new_data.artist_id.data,
            venue_id=new_data.venue_id.data,
            start_time=new_data.start_time.data
        )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

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
