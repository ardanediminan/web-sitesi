from flask import Flask, request, redirect, url_for, session, send_from_directory, render_template_string, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "local_dev_key")

SITE_PASSWORD = os.environ.get("SITE_PASSWORD", "ardababapro3169")

BASE_UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_logged_in() -> bool:
    return session.get("logged_in", False)


LOGIN_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Giriş</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .card {
            background: white;
            padding: 32px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            width: 100%;
            max-width: 380px;
        }
        h1 { margin-top: 0; }
        input, button {
            width: 100%;
            padding: 12px;
            margin-top: 12px;
            border-radius: 10px;
            border: 1px solid #d0d7e2;
            box-sizing: border-box;
        }
        button {
            background: #2563eb;
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
        }
        .flash {
            background: #fee2e2;
            color: #991b1b;
            padding: 10px;
            border-radius: 10px;
            margin-top: 12px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Site Girişi</h1>
        <p>Devam etmek için parolayı gir.</p>
        <form method="POST">
            <input type="password" name="password" placeholder="Parola" required>
            <button type="submit">Giriş Yap</button>
        </form>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="flash">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
    </div>
</body>
</html>
"""


DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Görsel Yükleme Paneli</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            margin: 0;
            padding: 24px;
            color: #1f2937;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
        }
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        .btn {
            display: inline-block;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 10px;
            padding: 10px 16px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-danger { background: #dc2626; }
        .card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
            margin-bottom: 20px;
        }
        input, select {
            width: 100%;
            padding: 12px;
            margin-top: 10px;
            margin-bottom: 12px;
            border-radius: 10px;
            border: 1px solid #d0d7e2;
            box-sizing: border-box;
        }
        .folder-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
        }
        .folder-card {
            background: #ffffff;
            border-radius: 14px;
            padding: 18px;
            border: 1px solid #e5e7eb;
        }
        .flash {
            background: #dcfce7;
            color: #166534;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 16px;
        }
        .muted {
            color: #6b7280;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="topbar">
            <h1>Görsel Yükleme Paneli</h1>
            <a class="btn btn-danger" href="{{ url_for('logout') }}">Çıkış Yap</a>
        </div>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="flash">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="card">
            <h2>Yeni Klasör Oluştur</h2>
            <form method="POST" action="{{ url_for('create_folder') }}">
                <input type="text" name="folder_name" placeholder="Klasör adı" required>
                <button class="btn" type="submit">Klasör Oluştur</button>
            </form>
        </div>

        <div class="card">
            <h2>Görsel Yükle</h2>
            <form method="POST" action="{{ url_for('upload_image') }}" enctype="multipart/form-data">
                <label>Klasör seç</label>
                <select name="folder_name" required>
                    <option value="">Klasör seç</option>
                    {% for folder in folders %}
                        <option value="{{ folder }}">{{ folder }}</option>
                    {% endfor %}
                </select>
                <label>Görsel seç</label>
                <input type="file" name="images" multiple required>
                <button class="btn" type="submit">Yükle</button>
            </form>
            <p class="muted">Desteklenen formatlar: png, jpg, jpeg, gif, webp</p>
        </div>

        <div class="card">
            <h2>Klasörler</h2>
            {% if folders %}
                <div class="folder-list">
                    {% for folder in folders %}
                        <div class="folder-card">
                            <h3>{{ folder }}</h3>
                            <a class="btn" href="{{ url_for('view_folder', folder_name=folder) }}">Klasörü Aç</a>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p>Henüz klasör yok.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


FOLDER_TEMPLATE = """
<!doctype html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ folder_name }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f7fb;
            margin: 0;
            padding: 24px;
        }
        .container {
            max-width: 1100px;
            margin: 0 auto;
        }
        .btn {
            display: inline-block;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 10px;
            padding: 10px 16px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 16px;
        }
        .images {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        }
        .card img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 12px;
        }
        .name {
            margin-top: 10px;
            font-size: 14px;
            color: #374151;
            word-break: break-word;
        }
    </style>
</head>
<body>
    <div class="container">
        <a class="btn" href="{{ url_for('dashboard') }}">← Panele Dön</a>
        <h1>{{ folder_name }}</h1>
        {% if images %}
            <div class="images">
                {% for image in images %}
                    <div class="card">
                        <img src="{{ url_for('uploaded_file', folder_name=folder_name, filename=image) }}" alt="{{ image }}">
                        <div class="name">{{ image }}</div>
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <p>Bu klasörde henüz görsel yok.</p>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if password == SITE_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Parola yanlış.")

    return render_template_string(LOGIN_TEMPLATE)


@app.route("/dashboard")
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    folders = sorted(
        [f for f in os.listdir(BASE_UPLOAD_FOLDER) if os.path.isdir(os.path.join(BASE_UPLOAD_FOLDER, f))]
    )
    return render_template_string(DASHBOARD_TEMPLATE, folders=folders)


@app.route("/create-folder", methods=["POST"])
def create_folder():
    if not is_logged_in():
        return redirect(url_for("login"))

    folder_name = secure_filename(request.form.get("folder_name", "").strip())
    if not folder_name:
        flash("Geçerli bir klasör adı gir.")
        return redirect(url_for("dashboard"))

    folder_path = os.path.join(BASE_UPLOAD_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    flash(f"'{folder_name}' klasörü oluşturuldu.")
    return redirect(url_for("dashboard"))


@app.route("/upload", methods=["POST"])
def upload_image():
    if not is_logged_in():
        return redirect(url_for("login"))

    folder_name = secure_filename(request.form.get("folder_name", "").strip())
    if not folder_name:
        flash("Bir klasör seç.")
        return redirect(url_for("dashboard"))

    folder_path = os.path.join(BASE_UPLOAD_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    files = request.files.getlist("images")
    uploaded_count = 0

    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(folder_path, filename)
            file.save(save_path)
            uploaded_count += 1

    if uploaded_count == 0:
        flash("Yüklenebilir geçerli görsel bulunamadı.")
    else:
        flash(f"Toplam {uploaded_count} görsel yüklendi.")

    return redirect(url_for("view_folder", folder_name=folder_name))


@app.route("/folder/<folder_name>")
def view_folder(folder_name):
    if not is_logged_in():
        return redirect(url_for("login"))

    safe_folder = secure_filename(folder_name)
    folder_path = os.path.join(BASE_UPLOAD_FOLDER, safe_folder)

    if not os.path.isdir(folder_path):
        flash("Klasör bulunamadı.")
        return redirect(url_for("dashboard"))

    images = sorted([
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and allowed_file(f)
    ])

    return render_template_string(FOLDER_TEMPLATE, folder_name=safe_folder, images=images)


@app.route("/uploads/<folder_name>/<filename>")
def uploaded_file(folder_name, filename):
    folder = secure_filename(folder_name)
    return send_from_directory(os.path.join(BASE_UPLOAD_FOLDER, folder), filename)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
