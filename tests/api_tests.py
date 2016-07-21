import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())
    
    
    
    def test_get_empty_songs(self):
        """ Getting posts from an empty database"""
        response = self.client.get("/api/songs", headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data,[])
    
    def test_get_songs(self):
        """ Gets songs from populated database """
        
        FileA = models.File(name="beyonce.mp3")
        FileB=  models.File(name="charliePuth.mp3")
        songA = models.Song(file=FileA)
        songB = models.Song(file=FileB)
        
        session.add_all([songA, songB])
        session.commit()
        response = self.client.get("/api/songs", headers=[("Accept", "application/json")])
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(len(data), 2)
        songA=data[0]
        self.assertEqual(songA["file"]["id"], FileA.id)
        songB=data[1]
        self.assertEqual(songB["file"]["id"], FileB.id)
        
    def test_get_song(self):
        
        """ Getting a single song from a populated database """
        fileA = models.File(name="hello.mp3")
        songA = models.Song(file=fileA)
        fileB = models.File(name="bye.mp3")
        songB = models.Song(file=fileB)
        
        session.add_all([songA, songB])
        session.commit()
        
        response = self.client.get("/api/songs/{}".format(songA.id), headers = [
            ("Accept", "application/json")]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        song = json.loads(response.data.decode("ascii"))
        
        self.assertEqual(song["file"]["id"], songA.file_id)
        self.assertEqual(song["file"]["name"], songA.file.name)
        
    def test_song_post(self):
        """ Posting a song to the database """
        data={
            "id" : 1,
            "file":{
                "id": 1,
                "name" : "hello.mp3"
            }
        }
        
        response = self.client.post("api/songs",
            data = json.dumps(data),
            content_type = "application/json",
            headers = [("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(urlparse(response.headers.get("Location")).path, "/api/songs/1")
        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["file"]["id"], 1)
        self.assertEqual(data["file"]["name"], "hello.mp3")
        
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)
        
        song = songs[0]
        
        self.assertEqual(song.file.name, "hello.mp3")
    
    def test_delete_song(self):
        """ Deleting a single song from a populated database """
        fileA = models.File(name = "hello.mp3")
        fileB = models.File(name = "bye.mp3")
        songA = models.Song(file = fileA)
        songB = models.Song(file = fileB)
        
        session.add_all([songA, songB])
        session.commit()
        
        response = self.client.delete("/api/songs/{}".format(songA.id), headers=[
            ("Accept", "application/json")]
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")
        
        song = json.loads(response.data.decode("ascii"))
        self.assertEqual(song["file"]["name"], fileB.name)