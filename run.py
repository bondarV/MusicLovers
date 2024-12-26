from musician_select import app, db
from musician_select.models import Alias,Musician
from sqlalchemy import select
if __name__ == '__main__':
    app.run(debug=True)
