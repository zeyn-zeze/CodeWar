from flask import Flask, render_template,request ,url_for,redirect,flash,session
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
import email_validator
import random

# Kullanıcı kayıt formu
class RegisterForm(Form):
    name = StringField("İsim - Soyisim", validators=[validators.Length(min=4, max=25)])
    username = StringField("Kullanıcı Adı", validators=[validators.Length(min=5, max=35)])
    email = StringField("E-mail", validators=[validators.Email(message="Lütfen geçerli bir email adresi girin")])
    password = PasswordField("Parola:", validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname="confirm", message="Parolanız Uyuşmuyor")
        ])
    confirm = PasswordField("Parola doğrula ")

class LoginForm(Form):
     username = StringField("Kullanıcı Adı")
     password = StringField("Parola")

app = Flask(__name__)
app.secret_key = "test"
app.config["MYSQL_HOST"] = "localhost" #sunucu adresi yazılır
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "kullanıcılar"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route('/')
def ana_sayfa():

    return render_template('index.html')



# register page
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla kayıt oldunuz...","success")
    
        return redirect(url_for("login"))
    else:
     return render_template("register.html", form= form)
    
@app.route("/login", methods =["GET","POST"])

def login():
    form= LoginForm(request.form)
    if request.method =="POST":
     username = form.username.data
     password_entered = form.password.data

     cursor = mysql.connection.cursor()
     sorgu = "Select * From users where username = %s"
     result = cursor.execute(sorgu,(username,))
     
     if result > 0 : 
         
         data = cursor.fetchone()
         real_password = data["password"]
         if sha256_crypt.verify(password_entered,real_password):
             flash("Başarıyla giriş yapıldı ...","success")
             session["logged_in"] = True #giriş anahtar değeri
             session["username"] = username
             return redirect(url_for("ana_sayfa"))
         else:
             flash("Parolanızı Yanlış Girdiniz...","danger")
             return redirect(url_for("login"))     
     else:
          flash("Böyle bir kullanıcı bulunamadı","danger")
          return redirect(url_for("login"))
    return render_template("login.html",form= form)

#logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("ana_sayfa"))



data = ["Python", "C", "C++", "Java", "JavaScript", "R", "Kotlin", "Swift", "PHP", "Pascal", "Ruby", "Objective-C", "Go", "SQL", "Typescript",]


tur = 0 

@app.route('/secim', methods=['GET', 'POST'])
def secim():
    if not session.get('logged_in'):
        flash("Lütfen giriş yapınız!", "danger")
        return redirect(url_for('login'))  # Redirect to the login page if not logged in
    else:
        global tur
        if request.method == 'POST':
            secilen = request.form['selected']
            diger = random.choice(data)
            data.remove(diger)
            tur += 1
            if not data:               
                return render_template('result.html', data=secilen)
            return render_template('secim.html', data1=secilen, data2=diger, round=tur, resim1="static/" + secilen.lower() + ".png", resim2="static/" + diger.lower() + ".png")
        else:
            ilkiki = random.sample(data,2)
            for item in ilkiki:
                if item in data:
                    data.remove(item)

            if data:
                return render_template('secim.html', data1=ilkiki[0], data2=ilkiki[1], round=tur, resim1="static/" + ilkiki[0].lower() + ".png", resim2="static/" + ilkiki[1].lower() + ".png")
            else:
                flash("No choices available!", "danger")
                return render_template('result.html')
 



if __name__ == "__main__":
    app.run(debug=True)
