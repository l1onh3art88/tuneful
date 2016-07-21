import os
from tuneful import app, models
from tuneful.database import session
from flask_script import Manager


manager = Manager(app)

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
@manager.command    
def seed():
    FileA = models.File(name="beyonce.mp3")
    songA = models.Song(file=FileA)
    session.add(songA)
    session.commit()

if __name__ == '__main__':
    manager.run()
   
