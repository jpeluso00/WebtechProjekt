from wsgiref import validate
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FileField, MultipleFileField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf.file import FileRequired, FileAllowed
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 
import os
from datetime import datetime
import time
#from flask_uploads import UploadSet, IMAGES
#UPLOAD_FOLDER = "C:\\User\\jpelu\\Desktop\\Fotoalbum\\templates\\UserFoto"
app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
### SQLALCHEMY
#Jack Desktop
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "Userdatabase.sqlite")
#app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
#Jack REWE Laptop
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:/Users/a183573/Desktop/Fotoalbum/Daten/database.db"
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:/Users/Aaron/Desktop/Fotoalbum/Fotoalbum/Daten/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(30))
    uploads = db.relationship("Upload", backref="user")
    uploads = db.relationship("Alben", backref="user")
    def __init__(self, username, email, password):
        self.username=username
        self.email=email
        self.password = password
class Upload(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    filename = db.Column(db.String(50))
    pfad = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
class Alben(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    description = db.Column(db.String)
    user_id =  db.Column(db.Integer, db.ForeignKey("user.id"))
class Fotoinalbum(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    alben_id =  db.Column(db.Integer, db.ForeignKey("alben.id"))
    upload_id = db.Column(db.Integer, db.ForeignKey("upload.id"))
class Shared(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    alben_id =  db.Column(db.Integer, db.ForeignKey("alben.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
class Comments(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(120))
    alben_id =  db.Column(db.Integer, db.ForeignKey("alben.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    publishdate = db.Column(db.DateTime)
    datum = db.Column(db.String)
class Sharedalbum(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    alben_id =  db.Column(db.Integer, db.ForeignKey("alben.id"))
    owner_id = db.Column(db.Integer)
db.create_all()
### Login Manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
### FlaskForm
#images = UploadSet('images', IMAGES)
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15) ])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')
class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15) ])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
class UploadForm(FlaskForm):
    file = FileField('Foto', validators=[FileRequired(), FileAllowed( ["jpg", "jpeg", "png", "jfif"] , "Es können nur Bilder hochgeladen werden.")])
class SelectionForm(FlaskForm):
    selection = MultipleFileField('selection', validators=[FileRequired(), FileAllowed( ["jpg", "jpeg", "png", "jfif"] , "Es können nur Bilder hochgeladen werden.")])
class AlbumForm(FlaskForm):
    title = StringField('titel', validators=[InputRequired()])
    description = StringField('description', validators=[InputRequired()])
class ShareForm(FlaskForm):
    friendname = StringField('friendname', validators=[InputRequired(), Length(min=4, max=15) ])
class KommentarForm(FlaskForm):
    kommentar = StringField('kommentar', validators=[InputRequired(), Length(max=120) ])
#        self.filenamee =filenamee
#        self.dataa = data
### Routing
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/Impressum")
def impressum():
    return render_template("Impressum.html")
@app.route("/Datenschutz")
def Datenschutz():
    return render_template("Datenschutz.html")
@app.route("/registrieren", methods=['GET', 'POST'])
def registrieren():
    form = RegisterForm()
    if current_user.is_authenticated:
        return("FEHLER")
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return(redirect(url_for("konto")))
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return render_template("registrieren.html", form=form)
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return("Sie sind bereits angemeldet!")
    elif form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user: 
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for("konto"))
        return '<h1> invalid username or password </h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return render_template("login.html", form=form)
@app.route("/hochladen", methods=["GET", "POST"])
@login_required
def hochladen():
    form = UploadForm()
    updated = None
    liste = [0]
    if request.method == "POST":
        file = form.file.data
        stmt = db.select(User, Upload).where(Upload.user_id == current_user.id).order_by(Upload.id)
        filename = file.filename
        for row in db.session.execute(stmt):
            liste.append(row.Upload.id)
        if form.validate_on_submit():
            endung = filename.split(".")
            filename = secure_filename("static/UserFoto/" + str(liste[-1]+1) + "." + str(endung[-1]))
            file.save("static/UserFoto/" + str(liste[-1]+1) + "." + str(endung[-1]))
            pfad1 = "/UserFoto/" + str(liste[-1]+1) + "." + str(endung[-1])
            userid =  current_user.id  
            db.session.add(Upload(filename = file.filename, pfad = pfad1  , user_id = userid))
            db.session.commit()
            stmt = db.select(User, Upload).where(Upload.user_id == current_user.id).order_by(Upload.id)
            filename = file.filename
            for row in db.session.execute(stmt):
                bildis= list()
                bildis.append(row.Upload.filename)
                updated = bildis[-1]
        return render_template("success.html", updated = updated, form = form, i = len(bildis))
    return render_template("upload.html", form=form)
@app.route("/konto")
@login_required
def konto():
    return render_template("konto.html")
@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for("home"))
    else:
        return("Sie sind nicht angemeldet")
@app.route("/Galerie", methods=["GET", "POST"])
@login_required
def galerie():
    form = AlbumForm()
    stmt = db.select(Upload).where(Upload.user_id == current_user.id).order_by(Upload.id)
    i=0
    bilder = list()
    for row in db.session.execute(stmt):
        i += 1
        bilder.append(row.Upload.pfad) 
    if request.method == "POST":
        if form.validate_on_submit():
            userid =  current_user.id
            title =   form.title.data
            db.session.add(Alben(name = form.title.data , description = form.description.data, user_id = userid))
            db.session.commit()
            stmt = db.select(Alben).where(Alben.user_id == current_user.id).order_by(Alben.id)
            for row in db.session.execute(stmt):
                bildis= list()
                bildis.append(row.Alben.id)
                updated = bildis[-1]
            for k in range(0,len(request.form.getlist('selc'))):
                bild = int(request.form.getlist('selc')[k]) +1 
                db.session.add(Fotoinalbum(alben_id =  updated, upload_id = bild))                
                db.session.commit()
        return render_template("albensuccess.html", title = title, bildis = bildis )
    return render_template("galerie.html", i=i, bilder = bilder, form=form)
@app.route("/alben", methods=["GET", "POST"])
@login_required
def alben():
    i=0
    n=0
    bildis = list()
    titel=list()
    caption = list()
    thumbnails=list()
    thumbnailpfad = list()
    albumid = list()
    stmt = db.select(Alben).where(Alben.user_id == current_user.id).order_by(Alben.id)
    for row in db.session.execute(stmt):
        bildis.append(row.Alben.id)
        titel.append(row.Alben.name)
        caption.append(row.Alben.description)
        i+=1
    for k in range(0,len(bildis)):
        stmt = db.select(Fotoinalbum).where(Fotoinalbum.alben_id == bildis[k]).order_by(Fotoinalbum.id)
        for row in db.session.execute(stmt):
            if len(thumbnails) <= k:
                thumbnails.append(row.Fotoinalbum.upload_id)
            else:
                pass
    for h in range(0,len(thumbnails)):
        stmt = db.select(Upload).where(Upload.id == thumbnails[h]).order_by(Upload.id)
        for low in db.session.execute(stmt):
            thumbnailpfad.append(low.Upload.pfad)
    return render_template("alben.html", i=i, thumbnailpfad = thumbnailpfad, bildis=bildis, titel=titel, caption = caption)
@app.route("/album<seite>", methods=["GET", "POST"])
@login_required
def album(seite):
    form = KommentarForm()
    berechtigt = 0
    stmt = db.select(Alben).where(Alben.id == seite).order_by()
    for row in db.session.execute(stmt):
        berechtigt = row.Alben.user_id
        titel = row.Alben.name
        caption = row.Alben.description
    if current_user.id == berechtigt:
        m= 0
        bilderinalbum = list()
        pfade = list()
        user_info = list()
        comment_text = list()
        pubdate = list()
        stmt = db.select(Fotoinalbum).where(Fotoinalbum.alben_id == seite).order_by(Fotoinalbum.id)
        if request.method == "POST":
            if form.validate_on_submit:
                text = form.kommentar.data 
                alben_id = seite 
                user_id = current_user.id 
                db.session.add(Comments(text = text , alben_id = alben_id, user_id = user_id, publishdate = datetime.now(), datum = time.strftime('%d-%m-%Y', time.localtime())))
                db.session.commit()
            else:
                return("FEHLER")
        for row in db.session.execute(stmt):
            bilderinalbum.append(row.Fotoinalbum.upload_id)   
        for z in range(0,len(bilderinalbum)):
            stmt = db.select(Upload).where(Upload.id == bilderinalbum[z]).order_by(Upload.id)
            for low in db.session.execute(stmt):
                pfade.append(low.Upload.pfad)
            m = len(pfade)
        dba = db.select(Comments).where(Comments.alben_id == seite).order_by(Comments.id)
        for cow in db.session.execute(dba):
            dbc = db.select(User).where(User.id == cow.Comments.user_id).order_by(User.id)
            for row in db.session.execute(dbc):
                user_info.append(row.User.username)
            comment_text.append(cow.Comments.text)
            pubdate.append(cow.Comments.datum)
        z = len(comment_text)
        form.kommentar.data = None
        return render_template("album.html", seite=seite,pfade = pfade, m = m,z=z, titel=titel, caption = caption, form=form, user_info = user_info, comment_text = comment_text, pubdate = pubdate )
    elif current_user.id != berechtigt:
        return("Keine Berechtigungen für das Album!")
@app.route("/sharealben", methods=["GET", "POST"])
@login_required
def sharealben():
    i=0
    form=ShareForm()
    n=0
    owner_user = None
    bild = list()
    bildis = list()
    titel=list()
    caption = list()
    thumbnails=list()
    thumbnailpfad = list()
    albumid = list()
    berechtigt = "1"
    stmt = db.select(Alben).where(Alben.user_id == current_user.id).order_by(Alben.id)
    for row in db.session.execute(stmt):
        bildis.append(row.Alben.id)
        titel.append(row.Alben.name)
        caption.append(row.Alben.description)
        i+=1
    for k in range(0,len(bildis)):
        stmt = db.select(Fotoinalbum).where(Fotoinalbum.alben_id == bildis[k]).order_by(Fotoinalbum.id)
        for row in db.session.execute(stmt):
            if len(thumbnails) <= k:
                thumbnails.append(row.Fotoinalbum.upload_id)
            else:
                pass
    for h in range(0,len(thumbnails)):
        stmt = db.select(Upload).where(Upload.id == thumbnails[h]).order_by(Upload.id)
        for low in db.session.execute(stmt):
            thumbnailpfad.append(low.Upload.pfad)
    #Album teilen Fehler: Bereits hinzugefügt, User existiert nicht
    if request.method == "POST":
        berechtigt="1"
        if form.validate_on_submit:
            for k in range(0,len(request.form.getlist('selection'))):
                bilder = int(request.form.getlist('selection')[k])
                bild.append(bildis[bilder])
            for j in range(0,len(bild)):
                stmt = db.select(Alben).where(Alben.id == bild[j]).order_by(Alben.id)
            for row in db.session.execute(stmt):
                owner_user = row.Alben.user_id
                stmt = db.select(User).where(User.username == form.friendname.data).order_by(User.id)
            for row in db.session.execute(stmt):
                userid = row.User.id
            stmt = db.select(Alben).where(Alben.user_id == current_user.id).order_by(Alben.id)
            for row in db.session.execute(stmt):
                bildis.append(row.Alben.id)
                print(bildis)
            stmt = db.select(Sharedalbum).where(Sharedalbum.user_id == userid).order_by(Sharedalbum.id)
            for row in db.session.execute(stmt):
                for v in range(0,len(bild)):
                    if  row.Sharedalbum.alben_id == bild[v]:
                        print("Album",row.Sharedalbum.alben_id)
                        print("Bildi ",bildis[v])
                        berechtigt = "0"
                    else:
                        pass   
            if berechtigt == "1":
                for p in range(0,len(bild)):
                    db.session.add(Sharedalbum(user_id = userid, alben_id = bild[p], owner_id = current_user.id ))
                    db.session.commit()
        form.friendname.data = None
    return render_template("sharealben.html", i=i, thumbnailpfad = thumbnailpfad, bildis=bildis, titel=titel, caption = caption, form=form, berechtigt = berechtigt)
@app.route("/sharedalben", methods=["GET", "POST"])
@login_required
def sharedalben():
    i=0
    n=0
    bildis = list()
    titel=list()
    caption = list()
    thumbnails=list()
    thumbnailpfad = list()
    albumid = list()
    usernames = list()
    ownerid = list()
    stmt = db.select(Sharedalbum).where(Sharedalbum.user_id == current_user.id).order_by(Sharedalbum.id)
    for row in db.session.execute(stmt):
        albumid.append(row.Sharedalbum.alben_id)
        ownerid.append(row.Sharedalbum.owner_id)
        i+=1
    for c in range(0,len(albumid)):
        stmt = db.select(Alben).where(Alben.id == albumid[c]).order_by(Alben.id)
        for row in db.session.execute(stmt):
            bildis.append(row.Alben.id)
            titel.append(row.Alben.name)
            caption.append(row.Alben.description)
    for q in range(0,len(ownerid)):
        stmt = db.select(User).where(User.id == ownerid[q]).order_by(User.id)
        for row in db.session.execute(stmt):
            usernames.append(row.User.username)
    for k in range(0,len(bildis)):
        stmt = db.select(Fotoinalbum).where(Fotoinalbum.alben_id == bildis[k]).order_by(Fotoinalbum.id)
        for row in db.session.execute(stmt):
            if len(thumbnails) <= k:
                thumbnails.append(row.Fotoinalbum.upload_id)
            else:
                pass
    for h in range(0,len(thumbnails)):
        stmt = db.select(Upload).where(Upload.id == thumbnails[h]).order_by(Upload.id)
        for low in db.session.execute(stmt):
            thumbnailpfad.append(low.Upload.pfad)
    return render_template("sharedalben.html", i=i, thumbnailpfad = thumbnailpfad, bildis=bildis, titel=titel, caption = caption, usernames = usernames)

if __name__ == '__main__':
    app.run(debug=True)