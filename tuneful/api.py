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
    

@app.route("/api/songs", methods = ["POST"])
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
    fileKeys = data["file"].keys()
    print(fileKeys)
    song = models.Song(id = data["id"], fileId=data["file"]["id"])
    session.add(song)
    session.commit()
    
    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("song_get", id=song.id)}
    return Response(data, 201, headers=headers, mimetype="application/json")
    