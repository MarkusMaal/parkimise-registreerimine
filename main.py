# flaski server
from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL
import os, hashlib, datetime

# serveri seadistamine
app = Flask(__name__)
serverport = 4262
serverhost = "localhost"

# juhusliku võtme genereerimine
os.urandom(24)
SECRET_KEY = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
app.config['SECRET_KEY'] = SECRET_KEY

# MySQL serveriga ühendamine
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'majakaSS123'
app.config['MYSQL_DB'] = 'parkimine'

mysql = MySQL(app)


def Ava_Dokument(failinimi):
    f = open(failinimi, "r", encoding="UTF-8")
    out = f.read()
    f.close()
    return out


def TöötleParkimiseLehte(numbrimärk, alustatud, nimi):
    leht = Ava_Leht("leheküljed/uus_parkimine.html")
    leht = leht.replace("{0}", session["username"])
    leht = leht.replace("{1}", numbrimärk)
    leht = leht.replace("{3}", nimi)
    if alustatud:
        leht = leht.replace("{2}", " disabled")
    else:
        leht = leht.replace("{2}", "")
    return leht


def Ava_Leht(lehenimi):
    return Ava_Dokument("küljendus/päis.html") + Ava_Dokument(lehenimi) + Ava_Dokument("küljendus/jalus.html")


def kontrolli_sobivust(number):
    if not len(number) == 6:
        return False
    else:
        tähestik = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(3):
            sobiv = False
            for n in range(10):
                if number[i] == str(n):
                    sobiv = True
            if not sobiv:
                return False
            sobiv = False
            for täht in tähestik:
                if number[i+3] == täht:
                    sobiv = True
            if not sobiv:
                return False
        return True



# avaleht
# sisu muutub vastavalt sellele, kas kasutaja on sisse loginud või mitte
@app.route("/")
def index():
    if len(session) > 0:
        out = Ava_Dokument("küljendus/päis.html")
        out += "<p>Tere tulemast, " + session["username"] + "!</p>"
        out += Ava_Dokument("küljendus/private_h.html")
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM PARKIMINE;''')
        kirjed = cursor.fetchall()
        kirjed_eksisteerivad = False
        if session["admin"] == 1:
            for kirje in kirjed:
                    out += "<tr>"
                    out += "<td>" + str(kirje[0]) + "</td>"
                    cursor.execute('SELECT KASUTAJA FROM KASUTAJAD WHERE ID = ' + str(kirje[1]) + ';')
                    out += "<td>" + str(cursor.fetchall()[0][0]) + " (ID: " + str(kirje[1]) + ")</td>"
                    out += "<td>" + str(kirje[5]) + "</td>"
                    out += "<td>" + str(kirje[2]) + "</td>"
                    out += "<td>" + str(kirje[3]) + "</td>"
                    if kirje[4] == None:
                        out += "<td>Parkimist pole lõpetatud</td>"
                    else:
                        out += "<td>" + str(kirje[4]) + "</td>"
                    out += "</tr>"
                    kirjed_eksisteerivad = True
            out += Ava_Dokument("küljendus/private_f.html")
        else:
            return redirect(url_for('lisa'))
        out += Ava_Dokument("küljendus/jalus.html")
        return out
    else:
        return Ava_Leht("leheküljed/public.html")


# lõpeta parkimine
@app.route("/end", methods=["POST", "GET"])
def end():
    if len(session) > 0:
        if request.method == "GET":
            parkimise_id = request.args["pid"]
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM PARKIMINE WHERE ID = ' + parkimise_id + ';')
            if cursor.fetchall()[0][1] == session["kasutaja_id"]:
                cursor.execute('UPDATE PARKIMINE SET LÕPPAEG = NOW() WHERE ID = ' + parkimise_id)
                mysql.connection.commit()
                cursor.close()
            return redirect(url_for('index'))

    else:
        return redirect(url_for('index'))


# lõpeta parkimine
@app.route("/lopeta")
def lopeta():
    if len(session) > 0:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM PARKIMINE WHERE KASUTAJA_ID = " + str(session["kasutaja_id"]))
        minu_parkimised = cursor.fetchall()
        parkimise_id = -1
        for parkimine in minu_parkimised:
            if parkimine[4] == None:
                parkimise_id = parkimine[0]
        päring = "UPDATE PARKIMINE SET LÕPPAEG = NOW() WHERE ID = " + str(parkimise_id)
        cursor.execute(päring)
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for('index'))


# lisa parkimine
@app.route("/lisa", methods=['POST', "GET"])
def lisa():
    if len(session) > 0:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM PARKIMINE WHERE KASUTAJA_ID = " + str(session["kasutaja_id"]))
        minu_parkimised = cursor.fetchall()
        aktiivne_parkimine = False
        parkimise_id = -1
        numbrimärk = "999XXX"
        nimi = ""
        algusaeg = datetime.time(0, 0, 0)
        for parkimine in minu_parkimised:
            if parkimine[4] == None:
                parkimise_id = parkimine[0]
                numbrimärk = parkimine[2]
                algusaeg = parkimine[3]
                nimi = parkimine[5]
                aktiivne_parkimine = True
        if request.method == 'POST':
            numbrimärk = request.form['autonr']
            nimi = request.form['nimi']
            if kontrolli_sobivust(numbrimärk):
                if not aktiivne_parkimine:
                    päring = "INSERT INTO PARKIMINE (KASUTAJA_ID, AUTO_NR, ALGUSAEG, NIMI) VALUES ("
                    päring += str(session["kasutaja_id"]) + ", \""
                    päring += numbrimärk + "\", "
                    päring += "now(), \""
                    päring += request.form["nimi"] + "\""
                    päring += ");"
                    cursor.execute(päring)
                    mysql.connection.commit()
                    cursor.close()
                    algusaeg = datetime.datetime.today()
                    return TöötleParkimiseLehte(numbrimärk, True, nimi) + '''
                            <a href="/lopeta">Lõpeta parkimine</a>
                        </form>
                        ''' + "<script>parkimisaeg = new Date(" + str(datetime.date.today().year) + ", " + str(datetime.date.today().month)  + ", " + str(datetime.date.today().day) + ", " +\
                        str(algusaeg.hour) + ", " + str(algusaeg.minute) + ", " + str(algusaeg.second) + "); </script>"
            else:
                return Ava_Leht("leheküljed/vale_nr.html")
        if not aktiivne_parkimine:
            return TöötleParkimiseLehte("999XXX", False, nimi) + '''
                <input type="submit" value="Alusta"/>
            </form>
            '''
        else:
            return TöötleParkimiseLehte(numbrimärk, True, nimi) + '''
                <a href="/lopeta">Lõpeta parkimine</a>
            </form>
            ''' + "<script>parkimisaeg = new Date(" + str(datetime.date.today().year) + ", " + str(datetime.date.today().month) + ", " + str(datetime.date.today().day) + ", " +\
                        str(algusaeg.hour) + ", " + str(algusaeg.minute) + ", " + str(algusaeg.second) + "); </script>"
    else:
        return redirect(url_for('index'))


# logi välja
@app.route('/logout')
def logout():
    session.clear()
    return Ava_Leht("leheküljed/logout.html")


# logi sisse kasutajaga
@app.route('/login', methods=['POST', "GET"])
def login():
    if request.method == 'POST':
        usr = request.form['username']
        pwd = request.form['passwd']
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT * FROM KASUTAJAD;''')
        kirjed = cursor.fetchall()
        if len(kirjed) == 0:
            return Ava_Dokument("küljendus/päis.html") + "<h2>Sisselogimine ebaõnnestus</h2><p>Andmebaasis puuduvad kasutajad. " \
                                               "Pöörduge administraatori poole.</p><a " \
                                               "href=\"/\">Tagasi avalehele</a> " +\
                                                Ava_Dokument("küljendus/jalus.html")
        else:
            sisselogitud = False
            for kirje in kirjed:
                if kirje[1] == request.form["username"] and kirje[2] == hashlib.md5((kirje[1] + request.form["passwd"]).encode('utf-8')).hexdigest():
                    session['username'] = kirje[1]
                    session['kasutaja_id'] = kirje[0]
                    session['admin'] = kirje[3]
                    sisselogitud = True
            if sisselogitud:
                return redirect(url_for('index'))
            else:
                return Ava_Dokument("küljendus/päis.html") + "<h2>Sisselogimine ebaõnnestus</h2><p>Vale kasutajanimi või " \
                                                   "parool</p><a " \
                                                   "href=\"/\">Tagasi avalehele</a> " +\
                                                    Ava_Dokument("küljendus/jalus.html")
    return Ava_Leht("leheküljed/login.html")


# registreeri uus kasutaja
@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        usr = request.form['user']
        pwd = request.form['passwd']
        cpwd = request.form['passwd2']
        if not cpwd == pwd:
            return Ava_Leht("veateated/vale_parool.html")
        päring = "INSERT INTO KASUTAJAD (KASUTAJA, VÕTI) VALUES (\""
        päring += usr + "\", "
        päring += "MD5(CONCAT(\"" + usr + "\", \"" + pwd + "\"))"
        päring += ");"
        cursor = mysql.connection.cursor()
        cursor.execute(päring)
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return Ava_Leht("leheküljed/registreeri.html")


# veateated
@app.errorhandler(404)
def e404(e):
    return Ava_Leht("veateated/404.html"), 404


@app.errorhandler(400)
def e404(e):
    return Ava_Leht("veateated/400.html"), 400


@app.errorhandler(500)
def e500(e):
    return Ava_Leht("veateated/500.html"), 500


if __name__ == "__main__":
    app.run(host=serverhost, port=serverport)
