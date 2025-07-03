import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "varsayilan_cok_guclu_gizli_anahtar_lutfen_degistirin")

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

print("🧪 DEBUG: Flask başlatılıyor...")
print(f"🧪 DEBUG: Ortam değişkenleri - MONGO_HOST: {MONGO_HOST}, MONGO_PORT: {MONGO_PORT}")
print(f"🧪 DEBUG: Ortam değişkenleri - MONGO_USERNAME: {MONGO_USERNAME}, MONGO_PASSWORD: {'****' if MONGO_PASSWORD else 'Yok'}")

client = None
db = None
users_collection = None
dreams_collection = None

if MONGO_USERNAME and MONGO_PASSWORD:
    mongo_uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/admin?authSource=admin"
    print(f"🧪 DEBUG: Mongo URI => mongodb://{MONGO_USERNAME}:****@{MONGO_HOST}:{MONGO_PORT}/admin?authSource=admin")
else:
    mongo_uri = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/"
    print(f"🧪 DEBUG: Mongo URI => {mongo_uri}")
    print("⚠️  WARNING: Kimlik bilgileri eksik olabilir, bağlantı başarısız olabilir.")

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ DEBUG: MongoDB bağlantısı başarılı!")
    db = client['dreamlist_db']
    users_collection = db['users']
    dreams_collection = db['dreams']
    print("✅ DEBUG: Koleksiyonlar bağlandı.")
except ConnectionFailure as e:
    print(f"❌ CRITICAL ERROR: MongoDB'ye bağlanılamadı (ConnectionFailure): {e}")
    db = None
except OperationFailure as e:
    print(f"❌ CRITICAL ERROR: MongoDB kimlik doğrulama hatası (OperationFailure): {e}")
    db = None
except Exception as e:
    print(f"❌ CRITICAL ERROR: Beklenmedik hata: {e}")
    db = None
finally:
    if db is None:
        print("⚠️  WARNING: Veritabanı bağlantısı kurulamadı. Uygulama sınırlı işlevsellikle çalışacak.")

@app.route("/")
def home():
    if db is None:
        flash("Veritabanı bağlantısı kurulamadı. Lütfen sunucu loglarını kontrol edin.", "error")
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if db is None:
        flash("Veritabanı bağlantısı yok. Kayıt yapılamıyor.", "error")
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if users_collection.find_one({"email": email}):
            flash("Bu email zaten kayıtlı.", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({"email": email, "password": hashed_password})
        flash("Kayıt başarılı! Lütfen giriş yapın.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if db is None:
        flash("Veritabanı bağlantısı yok. Giriş yapılamıyor.", "error")
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session["email"] = email
            flash("Giriş başarılı!", "success")
            return redirect(url_for("create"))
        else:
            flash("Hatalı email veya şifre.", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("email", None)
    flash("Başarıyla çıkış yaptınız.", "info")
    return redirect(url_for("home"))

@app.route("/create", methods=["GET", "POST"])
def create():
    if db is None:
        flash("Veritabanı bağlantısı yok. Hayal oluşturulamıyor.", "error")
        return redirect(url_for("home"))
    if "email" not in session:
        flash("Lütfen giriş yapın.", "info")
        return redirect(url_for("login"))
    if request.method == "POST":
        hayal = request.form["dream"]
        dreams_collection.insert_one({"email": session["email"], "dream": hayal})
        flash("Hayaliniz başarıyla eklendi!", "success")
        return redirect(url_for("detail"))
    return render_template("create.html")

@app.route("/detail")
def detail():
    if db is None:
        flash("Veritabanı bağlantısı yok. Detaylar görüntülenemiyor.", "error")
        return redirect(url_for("home"))
    if "email" not in session:
        flash("Lütfen giriş yapın.", "info")
        return redirect(url_for("login"))
    user_dreams = dreams_collection.find({"email": session["email"]})
    return render_template("detail.html", dreams=user_dreams)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)