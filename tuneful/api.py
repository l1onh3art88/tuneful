import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

song_schema ={
    "properties":{
        "file": {
            "name": {"type": "string"}
        }
    },
    "required": ["file"]
   
    
}
@app.route("/api/songs", methods = ["GET"])
@decorators.accept("application/json")
def songs_get():
    """ Displays songs """
    
    songs = session.query(models.Song).order_by(models.Song.id)
    
    #Converts Songs to Json and returns the appropriate response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
    

@app.route("/api/songs/<int:id>", methods=["GET"])
@decorators.accept("application/json")
def song_get(id):
    """ Single song endpoint """
    #Finds post from database based on id
    song = session.query(models.Song).get(id)
    
    #Checks whether post actually exists
    if not song:
        message = "Could not find song with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype = "application/json")
        
    #Returns post as JSON
    
    data = json.dumps(song.as_dictionary())
    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs", methods = ["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    """ Adds a new song"""
    data = request.json
     
    #Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    
    try: 
        validate(data, song_schema)
    except ValidationError as error:
        data={"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    #Add song to the database
  
    file = models.File(id = data["file"]["id"], name = data["file"]["name"])
    song = models.Song(id = data["id"], file=file )
    session.add(song)
    session.commit()
    
    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("song_get", id=song.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")
    
@app.route("/api/songs/<int:id>", methods = ["DELETE"])
@decorators.accept("application/json")
def delete_song(id):
    """ Delete a single song """
    song = session.query(models.Song).get(id)
    
    if not song:
        message = "Could not find post with id {}".format(id)
        data = json.dumps({"message": message})
        return Response(data,404, mimetype = "application/json")
        
    #Delete the post
    session.delete(song)
    session.commit()
    songs = session.query(models.Song).first()
    data=json.dumps(songs.as_dictionary())
    return Response(data, 200, mimetype = "application/json")