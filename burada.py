from asyncio.windows_events import NULL
from contextlib import redirect_stderr
#from crypt import methods
from hashlib import sha256
from turtle import title
from unicodedata import name
from unittest import result
from datetime import datetime
 
from webbrowser import get
from exceptiongroup import catch
#from django.shortcuts import render
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,IntegerField,PasswordField,validators
from flask_wtf.file import FileField, FileAllowed, FileRequired
from passlib.hash import sha256_crypt
import email_validator
from functools import wraps
import psycopg2
import psycopg2.extras



def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "loggin_in" in session:
            return f(*args,**kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapınız","danger")
            return redirect(url_for("login"))
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "loggin_admin" in session:
            return f(*args,**kwargs)
        else:
            flash("Bu sayfayı görüntülemek için yönetici olmanız gerekmektedir","danger")
            return redirect(url_for("index"))
    return decorated_function

#kullanıcı kayıt formu

class RegistrationForm(Form):
    name=StringField("İsim Soyisim",validators=[validators.Length(min=4,max=25)])
    username=StringField("Kullanıcı adı",validators=[validators.Length(min=5,max=25)])
    email=StringField("Email",validators=[validators.Email(message="lütfen geçerli bir email adresi giriniz..")])
    password=PasswordField("Parola",validators=[validators.Length(min=4,max=25),validators.DataRequired(message="Lütfen bir parola belirleyiniz"), validators.EqualTo(fieldname="confirm",message="Parolanız uyuşmuyor") ])
    
    confirm=PasswordField("Parola Doğrula")

class LoginForm(Form):
    username=StringField("Kullanıcı adı")
    password=PasswordField("Parola")

app = Flask(__name__)
app.secret_key = 'e-ticaret'
conn=psycopg2.connect(dbname="e-ticaret",
                      user="postgres",
                      password="1234",
                      host="localhost",
                      cursor_factory=psycopg2.extras.DictCursor)

cur=conn.cursor()
conn.autocommit = True

conn2=psycopg2.connect(dbname="beleseCom2",
                      user="postgres",
                      password="1234",
                      host="localhost",
                      cursor_factory=psycopg2.extras.DictCursor)

cur2=conn2.cursor()
conn2.autocommit = True

@app.route("/delete/<string:model_no>",methods=["GET","POST"])
@admin_required
def delete(model_no):
    
    sorgu="Delete from bilgisayarlar where model_no='"+ model_no+ "'"
    cur.execute(sorgu)
    sorgu="delete FROM public.bilgisayar_uniq where model_no='"+ model_no+ "' and site_ismi='burada.com'"
    print(sorgu)
    cur2.execute(sorgu)
    sorgu="SELECT * FROM public.bilgisayarlar where model_no='"+model_no+"'"
    print(sorgu)
    cur2.execute(sorgu)
    bilgisayarlar=cur2.fetchone()
    print(bilgisayarlar)
    if bilgisayarlar["en_dusuk_fiyat_site"]=='burada':
        sorgu ="select * from bilgisayar_uniq where model_no='"+ model_no+ "' order by fiyat"
        cur2.execute(sorgu)
        enDusuk=cur2.fetchone()
        
        if enDusuk!=None:
            print(enDusuk)
            site=str(enDusuk["site_ismi"]).split(".")[0]
            sorgu="UPDATE public.bilgisayarlar SET  en_dusuk_fiyat="+str(enDusuk["fiyat"])+", en_dusuk_fiyat_site='"+site+"' ,eklenme_tarihi='"+str(datetime.now())+"' WHERE model_no='"+model_no+"';"
            print(sorgu)
            cur2.execute(sorgu)
        else:
            print("girdim")
            sorgu="delete FROM public.bilgisayarlar where model_no='"+ model_no+ "' "
            cur2.execute(sorgu)
    
    flash(model_no+" model numaralı bilgisayar silindi...","success")
    return redirect(url_for("admin"))

@app.route("/update/<string:model_no>",methods=["GET","POST"])
@admin_required
def update(model_no):

    if request.method=="GET":
        sorgu="select * from bilgisayarlar where model_no =%s "
        
        result=cur.execute(sorgu,(model_no,))
        result=cur.fetchone()
        sorgu="select * from bilgisayarlar where model_no =%s "
        cur.execute(sorgu,(model_no,))
        if len(result)>0:
            computer=cur.fetchone()
            form=ComputerForm()
            form.marka.data=computer['marka']
            form.baslik.data=computer['urun_aciklamasi']
            form.model_no.data=computer['model_no']
            form.model_adi.data=computer['model_adi']
            
            form.ram.data=computer['ram']
            form.isletim_sistemi.data=computer['isletim_sistemi']
            form.islemci_tipi.data=computer['islemci_tipi']
            
            form.islemci_nesli.data=computer['islemci_nesli']
            form.ekran_boyutu.data=computer['ekran_boyutu']
            form.disk_turu.data=computer['disk_turu']
            
            form.disk_boyutu.data=computer['disk_boyutu']
            form.fiyat.data=computer['fiyat']
            form.gorsel.data=computer['gorsel_link']
            form.puan.data=computer['puan']
            return render_template("update.html",form=form)
    
        else:
            flash("Böyle bir bilgisayar yok...","danger")
            return redirect(url_for("admin"))
    else:
        form=ComputerForm(request.form)
        
        baslik=form.baslik.data
        marka=form.marka.data
        model_no=form.model_no.data
        model_adi=form.model_adi.data
        
        ram=form.ram.data
        isletim_sistemi=form.isletim_sistemi.data
        islemci_tipi=form.islemci_tipi.data
        
        islemci_nesli=form.islemci_nesli.data
        ekran_boyutu=form.ekran_boyutu.data
        disk_turu=form.disk_turu.data
        
        disk_boyutu=form.disk_boyutu.data
        fiyat=form.fiyat.data
        puan=form.puan.data
        gorsel=form.gorsel.data
        
        sorgu="UPDATE public.bilgisayarlar SET islemci_nesli=%s, gorsel_link=%s,  marka=%s, ekran_boyutu=%s, islemci_tipi=%s, isletim_sistemi=%s, disk_boyutu=%s, disk_turu=%s, ram=%s, model_no=%s, urun_aciklamasi=%s, fiyat=%s, model_adi=%s,puan=%s where model_no =%s"
        
        cur.execute(sorgu,(islemci_nesli,gorsel,marka,ekran_boyutu,islemci_tipi,isletim_sistemi,disk_boyutu,disk_turu,ram, model_no, baslik, fiyat, model_adi,puan,model_no))
        baslik_site=baslik+" burada"
        #sorgu="UPDATE public.bilgisayar_uniq SET  model_no='"+model_no+"', urun_aciklamasi='"+baslik+"', urun_aciklamasi_site='"+baslik_site+"', fiyat="+str(fiyat)+" WHERE model_no='"+model_no+"';"
        sorgu="UPDATE public.bilgisayar_uniq SET  fiyat="+str(fiyat)+" WHERE model_no='"+model_no+"' and site_ismi='burada.com';"

        cur2.execute(sorgu)
        sorgu="SELECT * FROM public.bilgisayar_uniq where model_no='"+model_no+"' order by fiyat"
        cur2.execute(sorgu)
        bilgisayarlar=cur2.fetchone()
        
        sorgu="UPDATE public.bilgisayarlar SET islemci_nesli=%s, gorsel_link=%s,  marka=%s, ekran_boyutu=%s, islemci_tipi=%s, isletim_sistemi=%s, disk_boyutu=%s, disk_turu=%s, ram=%s, model_no=%s, urun_aciklamasi=%s, en_dusuk_fiyat=%s,en_dusuk_fiyat_site=%s, model_adi=%s where model_no =%s"
        
        cur2.execute(sorgu,(islemci_nesli,gorsel,marka,ekran_boyutu,islemci_tipi,isletim_sistemi,disk_boyutu,disk_turu,ram, model_no, baslik, bilgisayarlar["fiyat"],bilgisayarlar["site_ismi"] ,model_adi,model_no))
        
        flash("Bilgisayar başarıyla güncellendi","success")
        return redirect(url_for("admin"))

@app.route("/add",methods=["GET","POST"])
@admin_required
def add():
    form=ComputerForm(request.form)
    if request.method=="POST" :
        baslik=form.baslik.data
        marka=form.marka.data
        model_no=form.model_no.data
        model_adi=form.model_adi.data
        
        ram=form.ram.data
        isletim_sistemi=form.isletim_sistemi.data
        islemci_tipi=form.islemci_tipi.data
        
        islemci_nesli=form.islemci_nesli.data
        ekran_boyutu=form.ekran_boyutu.data
        disk_turu=form.disk_turu.data
        
        disk_boyutu=form.disk_boyutu.data
        fiyat=form.fiyat.data
        gorsel=form.gorsel.data
        puan=form.puan.data
        
        sorgu="INSERT INTO public.bilgisayarlar(islemci_nesli, gorsel_link, eklenme_tarihi,  marka, ekran_boyutu, islemci_tipi, isletim_sistemi, disk_boyutu, disk_turu, ram, model_no, urun_aciklamasi, fiyat, model_adi,puan) VALUES ('"+islemci_nesli+"', '"+gorsel+"', '"+str(datetime.now())+"', ' "+marka+"', ' "+ekran_boyutu+"', '"+islemci_tipi+"', '"+isletim_sistemi+"', ' "+disk_boyutu+"',' " +disk_turu+"', ' "+ram+"', '"+model_no+"', '"+baslik+"', "+str(fiyat)+", '"+model_adi+"', "+str(puan)+");"
       # sorgu=("INSERT INTO public.bilgisayarlar(islemci_nesli, gorsel_link, eklenme_tarihi,  marka, ekran_boyutu, islemci_tipi, isletim_sistemi, disk_boyutu, disk_turu, ram, model_no, urun_aciklamasi, fiyat, model_adi) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %d, %s);")
       
        #cur.execute(sorgu,(islemci_nesli,gorsel,datetime.now(),marka,ekran_boyutu,islemci_tipi,isletim_sistemi,disk_boyutu,disk_turu,ram, model_no, baslik, fiyat, model_adi))
        #sorgu="INSERT INTO public.bilgisayarlar(islemci_nesli, gorsel_link, eklenme_tarihi, puan, marka, ekran_boyutu, islemci_tipi, isletim_sistemi, disk_boyutu, disk_turu, ram, model_no, urun_aciklamasi, fiyat, model_adi) VALUES (%s,%s,%s,4,%s,%s,%s,%s,%s,%s,%s,%s,%s,);"
        try:
            cur.execute(sorgu)
            flag=1
        except:
            flag=0
            flash("Bu model numarasına ait bilgisayar bulunuyor..","danger")
        if flag==1:
            sorgu="SELECT * FROM public.bilgisayarlar"
            cur2.execute(sorgu)
            bilgisayarlar=cur2.fetchall()
            a=0
            for i in bilgisayarlar:
                if model_no in i["model_no"]:
                    a=1
                    
            if a==0:
                sorgu="INSERT INTO public.bilgisayarlar(islemci_nesli, gorsel_link, eklenme_tarihi, puan, marka, ekran_boyutu, islemci_tipi, isletim_sistemi, disk_boyutu, disk_turu, ram, model_no, urun_aciklamasi, en_dusuk_fiyat, en_dusuk_fiyat_site, model_adi) VALUES ('"+islemci_nesli+"', '"+gorsel+"', '"+str(datetime.now())+"'," +str(puan)+" ,' "+marka+"', ' "+ekran_boyutu+"', '"+islemci_tipi+"', '"+isletim_sistemi+"', ' "+disk_boyutu+"',' " +disk_turu+"', ' "+ram+"', '"+model_no+"', '"+baslik+"', "+str(fiyat)+",'burada', '"+model_adi+"');"    
                cur2.execute(sorgu)
                sorgu="INSERT INTO public.bilgisayar_uniq(model_no, link, urun_aciklamasi, urun_aciklamasi_site, fiyat, site_ismi)VALUES ('"+model_no+"', 'http://127.0.0.1:1000/detail/"+model_no+"','"+baslik+"','"+baslik+" burada ',  "+str(fiyat)+", 'burada.com');"
                cur2.execute(sorgu)
                
            else:
                sorgu="select * from bilgisayar_uniq where model_no='"+model_no+"' order by fiyat"
                cur2.execute(sorgu)
                bil_uniq=cur2.fetchone()
                print(bil_uniq)
                if fiyat < bil_uniq["fiyat"]:
                    sorgu="INSERT INTO public.bilgisayar_uniq(model_no, link, urun_aciklamasi, urun_aciklamasi_site, fiyat, site_ismi)VALUES ('"+model_no+"' , 'http://127.0.0.1:1000/detail/"+model_no+"','"+baslik+"','"+baslik+" burada ',  "+str(fiyat)+", 'burada.com');"
                    cur2.execute(sorgu)
                    sorgu="UPDATE public.bilgisayarlar SET  en_dusuk_fiyat="+str(fiyat)+", en_dusuk_fiyat_site='burada' ,eklenme_tarihi='"+str(datetime.now())+"' WHERE model_no='"+model_no+"';"    
                    cur2.execute(sorgu)
                    
                else:
                    sorgu="INSERT INTO public.bilgisayar_uniq(model_no, link, urun_aciklamasi, urun_aciklamasi_site, fiyat, site_ismi)VALUES ('"+model_no+"', 'http://127.0.0.1:1000/detail/"+model_no+"','"+baslik+"','"+baslik+" burada ',  "+str(fiyat)+", 'burada.com');"
                    cur2.execute(sorgu)

            flash("Bilgisayar başarıyla eklendi","success")
            return redirect(url_for("admin"))
        #beleCom Sorguları
        
                    
            #print(bilgisayarlar.model_no)
            #sorgu="INSERT INTO public.bilgisayarlar( islemci_nesli, gorsel_link, eklenme_tarihi, puan, marka, ekran_boyutu, islemci_tipi, isletim_sistemi, disk_boyutu, disk_turu, ram, model_no, urun_aciklamasi, en_dusuk_fiyat, en_dusuk_fiyat_site, model_adi) VALUES ('"+islemci_nesli+"', '"+gorsel+"', '"+str(datetime.now())+"'," +str(puan)+" ,'"+marka+"', '"+ekran_boyutu+"', '"+islemci_tipi+"', '"+isletim_sistemi+"', '"+disk_boyutu+"','" +disk_turu+"', '"+ram+"', '"+model_no+"', '"+baslik+"', "+str(fiyat)+", '"+model_adi+"');"
        
        #flash("Bilgisayar başarıyla eklendi","success")
        
        
        


    return render_template("addcomputer.html",form=form)
   

@app.route("/admin",methods=["GET","POST"])
@admin_required
def admin():
    sorgu="SELECT * FROM bilgisayarlar "
    cur.execute(sorgu)
    computers=cur.fetchall()
    
    
    
    return render_template("admin.html",computers=computers)

@app.route("/loginadmin",methods=["GET","POST"])
def loginadmin():
    form=LoginForm(request.form)
    if request.method=="POST":
        password=form.password.data
        username=form.username.data
        if password=="admin" and username=="admin":
                flash("Giriş Başarılı","success")
                session["loggin_admin"]=True

                return redirect(url_for("admin"))
                
        else:
                flash("Yanlış giriş...","danger")
                return redirect(url_for("loginadmin"))
        
    return render_template("adminlogin.html",form =form)

@app.route("/adminlogout")
def adminlogout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/search",methods=["GET","POST"])
def search():
    if request.method=="GET":
        return redirect(url_for("index"))
    else:
        keyword=request.form.get("keyword")
        
        sorgu="select * from bilgisayarlar where urun_aciklamasi like '%"+ keyword+ "%'"
        result=cur.execute(sorgu)
        result=cur.fetchall()
        
        if len(result) ==0:
            flash("Aranan kelimeye uygun bilgisayar bulunamadı...","warning")
            return redirect(url_for("index"))
        else:
            cur.execute(sorgu)
            computers=cur.fetchall();
            return render_template("index.html",computers=computers,Puan=Puan(),disk_turu=diskTuru(), markalar=markalar(),disk_boyutu=isletimSistemi(),
                           ekran_boyutu=ekranBoyutu(),ram=Ram())
        
@app.route("/admin_search",methods=["GET","POST"])
def admin_search():
    if request.method=="GET":
        return redirect(url_for("admin"))
    else:
        keyword=request.form.get("keyword")
        
        sorgu="select * from bilgisayarlar where model_no='"+ keyword+ "'"
        result=cur.execute(sorgu)
        result=cur.fetchall()
        
        if len(result) ==0:
            flash("Aranan model numarasına uygun bilgisayar bulunamadı...","warning")
            return redirect(url_for("admin"))
        else:
            cur.execute(sorgu)
            computers=cur.fetchall();
            print(computers)
            return render_template("admin.html", computers=computers)


@app.route("/detail/<string:model_no>")
def detail(model_no):
    sorgu="select * from bilgisayarlar where model_no ='"+model_no+"'"
    cur.execute(sorgu)
    computerDetail=cur.fetchone()
    
    
    try:
        cur.execute(sorgu)
        computerDetail=cur.fetchone()
        return render_template("detail.html",computerDetail=computerDetail)
    except:
        flash("Böyle bir bilgisayar bulunmamaktadır","danger")
        return redirect(url_for("index"))
        

@app.route("/lowestprice")
def lowprice():
    sorgu=("select * from bilgisayarlar  order by fiyat")
    result=cur.execute(sorgu)
    computers=cur.fetchall() 
    return render_template("index.html",computers=computers,Puan=Puan(),disk_turu=diskTuru(), markalar=markalar(),disk_boyutu=isletimSistemi(),
                           ekran_boyutu=ekranBoyutu(),ram=Ram())

@app.route("/highestprice")
def highestprice():
    sorgu=("select * from  bilgisayarlar  order by fiyat DESC")
    result=cur.execute(sorgu)
    computers=cur.fetchall() 
    return render_template("index.html",computers=computers,Puan=Puan(),disk_turu=diskTuru(), markalar=markalar(),disk_boyutu=isletimSistemi(),
                           ekran_boyutu=ekranBoyutu(),ram=Ram())

@app.route("/newest")
def newest():
    sorgu=("select * from bilgisayarlar  order by eklenme_tarihi DESC")
    result=cur.execute(sorgu)
    computers=cur.fetchall() 
    return render_template("index.html",computers=computers,Puan=Puan(),disk_turu=diskTuru(), markalar=markalar(),disk_boyutu=isletimSistemi(),
                           ekran_boyutu=ekranBoyutu(),ram=Ram())

def markalar():
    sorgu=("SELECT DISTINCT marka FROM bilgisayarlar")
    cur.execute(sorgu)
    marka=cur.fetchall()
    return marka

def isletimSistemi():
    sorgu=("SELECT DISTINCT disk_boyutu FROM bilgisayarlar") 
    result=cur.execute(sorgu)
    disk_boyutu=cur.fetchall()
    return disk_boyutu

def ekranBoyutu():
    sorgu=("SELECT DISTINCT ekran_boyutu FROM bilgisayarlar") 
    result=cur.execute(sorgu)
    ekranBoyutu=cur.fetchall()
    return ekranBoyutu

def Ram():
    sorgu=("SELECT DISTINCT ram FROM bilgisayarlar")
    cur.execute(sorgu)
    Ram=cur.fetchall()
    return Ram

def Puan():
    sorgu=("SELECT DISTINCT puan FROM bilgisayarlar order by puan")
    cur.execute(sorgu)
    Puan=cur.fetchall()
    return Puan

def diskTuru():
    sorgu=("select DISTINCT disk_turu from bilgisayarlar")
    cur.execute(sorgu)
    disk_turu=cur.fetchall()
    return disk_turu


def createString(marka,disk_boyutu,disk_turu,ram,ekran_boyutu,minP,maxP,Puan):
    checked={}
    
    if len(marka)!=0: 
        checked['marka']=marka
    if len(disk_boyutu)!=0: 
        checked['disk_boyutu']=disk_boyutu
    if len(ram)!=0: 
        checked['ram']=ram
    if len(ekran_boyutu)!=0: 
        checked['ekran_boyutu']=ekran_boyutu 
    if len(disk_turu)!=0: 
        checked['disk_turu']=disk_turu 
    if len(Puan)!=0: 
        checked['puan']=Puan 
    print(disk_turu)
    
    string = "select * from bilgisayarlar where "
    a=0
    if minP:
        if a==0:
            string += " bilgisayarlar.fiyat>"+minP
            a+=1
        else:
            string += "and bilgisayarlar.fiyat>"+minP
            
        
    if maxP: 
        if a==0:
            string += " bilgisayarlar.fiyat<"+maxP
            a+=1
        else:
            string += "and bilgisayarlar.fiyat<"+maxP
        
        
    for i in checked:
        if a==0:
            string += "bilgisayarlar." + i + " in ("
        else:
            string += "and bilgisayarlar." + i + " in ("
        for j in checked[i]:
            if i=='ram':
                string += "' " + j + " GB',"
            elif i=="disk_boyutu":
                if j=='1':
                    string += "' " + j + " TB',"
                else:
                    string += "' " + j + " GB',"
                    
            else:
                string += "' " + j + "',"
        string = string[:-1]
        string += ") "   

    print(string)
    return string        



@app.route("/",methods=["GET","POST"])
def index():
    
    
        
    sorgu="SELECT * FROM bilgisayarlar "
    cur.execute(sorgu)
    computers=cur.fetchall()

    if request.method=="POST":
        checked={}
        minP=request.form.get('minPrice');
        maxP=request.form.get('maxPrice');
        marka=request.form.getlist('markaChecked');
        disk_boyutu=request.form.getlist('diskChecked');
        ram=request.form.getlist('ramChecked');
        ekran_boyutu=request.form.getlist('ekranChecked');
        disk_turu=request.form.getlist('diskTuruChecked');
        puan=request.form.getlist('puanChecked');
        print(disk_turu)
        
        
        string=createString(marka,disk_boyutu,disk_turu,ram,ekran_boyutu,minP,maxP,puan)
        try:
            cur.execute(string)
            computers=cur.fetchall()
        except:
            flash("Lütfen bir filtreleme yapınız...","danger")
        
        
    
    return render_template("index.html",computers=computers,Puan=Puan(),disk_turu=diskTuru()
                           , markalar=markalar(),disk_boyutu=isletimSistemi(),
                           ekran_boyutu=ekranBoyutu(),ram=Ram())

@app.route("/register",methods=["GET","POST"])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate() :
        
        name=form.name.data
        email=form.email.data
        password=sha256_crypt.encrypt(form.password.data)
        username=form.username.data
        
        #sorgu="INSERT INTO  kullanici(isim,email,kullanici_adi,sifre) VALUES(%s,%s,%s,%s)"
        
        #cur.execute(sorgu,(name,email,username,password))
        print(name)
        
        sorgu="INSERT INTO  kullanici(isim,email,kullanici_adi,sifre) VALUES('"+name+"','"+email+"','"+username+"','"+password+"')"
        #sorgu="INSERT INTO  kullanici(isim,email,kullanici_adi,sifre) VALUES('sevval','sevvalcimQgmail.com','sevval','12345')"
        cur.execute(sorgu)
        #cur.commit()
        
        flash("Başarıyla Kayıt Oldunuz...","success")
        
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    
    form=LoginForm(request.form)
    
    if request.method=="POST":
        password=form.password.data
        username=form.username.data
        
        sorgu="select * from kullanici where kullanici_adi= %s"
        
        result=cur.execute(sorgu,(username,))
        result=cur.fetchall()
        if len(result)>0:
            sorgu="select * from kullanici where kullanici_adi= %s"
            cur.execute(sorgu,(username,))
            data=cur.fetchone()

            
            real_password=data["sifre"]
            if sha256_crypt.verify(password,real_password):
                flash("Giriş Başarılı","success")
                
                session["loggin_in"]=True
                
                
                return redirect(url_for("index"))
                
            else:
                flash("Parolanızı yanlış girdiniz...","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor","danger")
            return redirect(url_for("login"))
    
    
    
    return render_template("login.html",form=form)

class ComputerForm(Form):
    baslik=StringField("Başlık ",validators=[validators.Length(min=2),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    marka=StringField("Marka ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    model_no=StringField("Model No ",validators=[validators.Length(min=2),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    model_adi=StringField("Model Adı ",validators=[validators.Length(min=2),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    ram=StringField("Ram ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    isletim_sistemi=StringField("İşletim Sistemi ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    islemci_tipi=StringField("İşlemci Tipi ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    islemci_nesli=StringField("İşlemci Nesli ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    ekran_boyutu=StringField("Ekran Boyutu",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    disk_turu=StringField("Disk Türü ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    disk_boyutu=StringField("Disk Boyutu ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    fiyat=IntegerField("Fiyat ",validators=[validators.Length(min=2,max=20),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    puan=IntegerField("Puan ",validators=[validators.Length(min=0,max=5),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])
    gorsel=StringField("Görsel Linki ",validators=[validators.Length(min=2),validators.DataRequired(message="Lütfen bu alanı doldurunuz")])




if __name__=="__main__":
    #app.run(debug=True)
    app.run(port=1000)
    