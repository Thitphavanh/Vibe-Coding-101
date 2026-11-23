# คู่มือนำ Vibe Coding 101 — Blog ขึ้นเซิร์ฟเวอร์ด้วย Apache2 + mod_wsgi

เอกสารนี้พาทำตั้งแต่เซิร์ฟเวอร์เปล่า จนเปิดใช้งานที่ `http://159.89.198.240/` ได้
โดยใช้ **Apache2 + mod_wsgi** และฐานข้อมูล **SQLite** (ตามที่ตั้งไว้ใน `core/settings.py`)
เข้าใช้งานผ่าน **IP อย่างเดียว** ยังไม่มีโดเมนและ SSL

**ข้อมูลหลักที่ใช้ในคู่มือนี้**

| รายการ                      | ค่า                                                                |
| --------------------------------- | --------------------------------------------------------------------- |
| IP ของเซิร์ฟเวอร์   | `159.89.198.240`                                                    |
| โดเมน                        | ไม่มี — เข้าผ่าน `http://159.89.198.240/`             |
| ชื่อเครื่อง (hostname) | `vibe-coding`                                                       |
| ผู้ใช้ที่รันระบบ  | `vibe`                                                              |
| ที่เก็บโค้ด            | `/home/vibe/Vibe-Coding-101`                                        |
| virtualenv                        | `/home/vibe/venv`                                                   |
| ไฟล์ settings                 | `core/settings.py` (อ่านค่าจาก `.env`)                  |
| ไฟล์ WSGI                     | `core/wsgi.py`                                                      |
| ฐานข้อมูล                | SQLite ไฟล์ `db.sqlite3` ในโฟลเดอร์โปรเจกต์   |
| Git repo                          | `<URL ของ git repo>` (ใส่ URL จริงของโปรเจกต์) |

> **แนะนำ Ubuntu 24.04 ขึ้นไป** (Python 3.12) — Django 5.2 ต้องใช้ Python 3.10 ขึ้นไป
> และ `libapache2-mod-wsgi-py3` ของ apt ถูก build มากับ python3 ของระบบ
> venv จึงต้องเป็น Python รุ่นเดียวกับ `python3` ของระบบ ไม่อย่างนั้น Apache จะขึ้น error ตอนโหลด

---

## 0. ใส่ SSH Key และเข้าเซิร์ฟเวอร์จากเครื่องเรา

ใช้ SSH Key แทนการพิมพ์รหัสผ่าน (สร้าง Key ด้วย PuTTYgen บน Windows ไว้ก่อนแล้ว)

**0.1 ใส่ Public key ลงเซิร์ฟเวอร์** — เปิด **Web Console** ในหน้า Droplet ของ DigitalOcean แล้ววางคำสั่งนี้
(แทน `ssh-rsa AAAA...` ด้วยข้อความ Public key ทั้งบรรทัดจากกล่องด้านบนของ PuTTYgen ห้ามใช้ไฟล์จากปุ่ม Save public key):

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-rsa AAAA...ทั้งบรรทัด... rsa-key-20261123" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

ตรวจว่าใส่แล้ว:

```bash
cat ~/.ssh/authorized_keys
```

**0.2 แปลง Private key เป็นแบบ OpenSSH** — คำสั่ง `ssh` อ่านไฟล์ `.ppk` ไม่ได้
เปิด PuTTYgen → **Load** → เลือกไฟล์ `.ppk` → **Conversions → Export OpenSSH key** → กด **Yes** → ตั้งชื่อไฟล์ `id_rsa` (ไม่มีนามสกุล)

**0.3 เข้าเซิร์ฟเวอร์จาก Windows PowerShell:**

```powershell
Copy-Item <โฟลเดอร์ที่เซฟ>\id_rsa $HOME\.ssh\id_rsa
ssh root@159.89.198.240
```

**เข้าจาก Mac (Terminal):**

```bash
mkdir -p ~/.ssh
mv ~/Downloads/id_rsa ~/.ssh/id_rsa
chmod 600 ~/.ssh/id_rsa
ssh root@159.89.198.240
```

ครั้งแรกจะถาม `Are you sure you want to continue connecting` ให้พิมพ์ `yes`
ถ้าขึ้น `root@vibe-coding:~#` แปลว่าเข้าได้แล้ว

> ถ้าขึ้น `Permission denied (publickey)` ให้เช็กว่ามีไฟล์ `id_rsa` ในโฟลเดอร์ `.ssh` ของเครื่องเรา
> และ `authorized_keys` บนเซิร์ฟเวอร์มี Public key ของเราจริง

## 1. ตั้งค่าเซิร์ฟเวอร์เบื้องต้น

ล็อกอินเข้าเซิร์ฟเวอร์ด้วย root (ใช้ SSH Key จากข้อ 0):

```bash
ssh root@159.89.198.240
```

อัปเดตระบบ:

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

ตั้งชื่อเครื่อง (hostname):

```bash
sudo hostnamectl set-hostname vibe-coding
hostname
```

แก้ไฟล์ `/etc/hosts`:

```bash
sudo nano /etc/hosts
```

เพิ่มบรรทัดนี้ก่อนบรรทัด `127.0.0.1`:

```text
159.89.198.240 vibe-coding
```

*(กด `Ctrl+X` > `Y` > `Enter` เพื่อบันทึก)*

ตั้งเขตเวลาเป็นเวลาไทย (cron สำรองข้อมูลในข้อ 13 จะรันตามเวลานี้):

```bash
sudo timedatectl set-timezone Asia/Bangkok
```

## 2. สร้างผู้ใช้ใหม่

สร้างผู้ใช้ `vibe` สำหรับรันโปรเจกต์:

```bash
sudo adduser vibe
# ใส่รหัสผ่านและข้อมูลตามขั้นตอน
```

ให้สิทธิ์ sudo:

```bash
sudo adduser vibe sudo
```

สลับไปใช้ผู้ใช้ใหม่:

```bash
su - vibe
```

## 3. ตั้งค่า Firewall (UFW)

```bash
sudo apt-get install ufw
sudo ufw default allow outgoing
sudo ufw default deny incoming
sudo ufw allow 22           # SSH
sudo ufw allow 8000         # ทดสอบชั่วคราว
sudo ufw allow http         # พอร์ต 80
sudo ufw enable
sudo ufw status
```

## 4. ติดตั้ง Git, Python และ Virtual Environment

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv sqlite3
```

ตรวจว่าติดตั้งแล้ว:

```bash
git --version        # ควรเป็น git version 2.x
python3 --version    # ต้องเป็น 3.10 ขึ้นไป
```

ตั้งชื่อและอีเมลให้ Git (ใช้ตอน commit บนเซิร์ฟเวอร์ ตั้งครั้งเดียว):

```bash
git config --global user.name "<ชื่อบัญชี GitHub>"
git config --global user.email "<อีเมลที่ผูกกับ GitHub>"
```

> ถ้าไม่อยากให้อีเมลจริงปรากฏใน commit ให้ใช้อีเมล noreply ของ GitHub แทน
> (Settings → Emails → Keep my email addresses private)

สร้าง Virtual Environment:

```bash
cd ~
python3 -m venv venv
```

## 5. ดึงโปรเจกต์ลงเซิร์ฟเวอร์ด้วย Git Clone

```bash
cd ~
git clone <URL ของ git repo> Vibe-Coding-101
```

ถ้า repo เป็น **private** แนะนำให้ใช้ SSH key:

```bash
ssh-keygen -t ed25519 -C "vibe-coding-server"
cat ~/.ssh/id_ed25519.pub     # นำไปใส่ GitHub → Settings → SSH and GPG keys
git clone git@github.com:<owner>/<repo>.git Vibe-Coding-101
```

**โครงสร้างไฟล์บนเซิร์ฟเวอร์หลัง clone:**

```bash
/home/vibe/
    venv/
    Vibe-Coding-101/
        manage.py
        requirements.txt
        .env.example
        core/               # settings.py, urls.py, wsgi.py
        blog/               # models, views, admin, templates, คำสั่ง seed_ai_posts
        templates/          # base.html, index.html, partials/
        static/             # css/style.css, js/, img/
        media/              # thumbnail บทความ + รูปที่อัปโหลดผ่าน Summernote — สร้างเองถ้ายังไม่มี
        db.sqlite3          # ฐานข้อมูล — จะถูกสร้างตอน migrate (ข้อ 8)
```

> Tailwind CSS โหลดผ่าน CDN ใน `templates/base.html` จึง **ไม่ต้องติดตั้ง Node.js / npm** บนเซิร์ฟเวอร์

ตั้งเจ้าของไฟล์:

```bash
sudo chown -R vibe:vibe /home/vibe/Vibe-Coding-101
```

## 6. ติดตั้ง Dependencies

```bash
source ~/venv/bin/activate
pip install --upgrade pip
pip install -r /home/vibe/Vibe-Coding-101/requirements.txt
```

## 7. ตั้งค่า Django (`.env`)

ค่าตั้งทั้งหมดอ่านจากไฟล์ `.env` ที่ `core/settings.py` โหลดเอง ไม่ต้องแก้ในโค้ด:

```bash
cd ~/Vibe-Coding-101
cp .env.example .env
~/venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
nano .env                 # ใส่ค่าจริง
chmod 600 .env            # อ่านได้เฉพาะเจ้าของ
```

ค่าที่ **ต้อง** ตั้ง:

| ตัวแปร      | ตั้งเป็น                               |
| ----------------- | ---------------------------------------------- |
| `SECRET_KEY`    | คีย์ใหม่จากคำสั่งด้านบน |
| `DEBUG`         | `False`                                      |
| `ALLOWED_HOSTS` | `159.89.198.240` (ห้ามใส่ `*`)      |

ไฟล์ `.env` ที่ได้:

```ini
DEBUG=False
SECRET_KEY=<คีย์ที่สร้างจากคำสั่งด้านบน>
ALLOWED_HOSTS=159.89.198.240
```

`STATIC_ROOT` (`staticfiles/`) และ `MEDIA_ROOT` (`media/`) ตั้งไว้ใน `core/settings.py` แล้ว ไม่ต้องแก้อะไร

## 8. Migrate, Static และข้อมูลตั้งต้น

```bash
source ~/venv/bin/activate
cd ~/Vibe-Coding-101
mkdir -p media

python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

ใส่บทความตัวอย่าง (ไม่บังคับ):

```bash
python manage.py seed_ai_posts --count 12 --author <username ที่สร้างไว้>
```

ตรวจความพร้อมก่อนเปิดใช้จริง:

```bash
python manage.py check --deploy
```

> คำเตือนเรื่อง HTTPS (`SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`,
> `CSRF_COOKIE_SECURE`) จะยังขึ้นอยู่ — เป็นเรื่องปกติเพราะคู่มือนี้ใช้ IP ผ่าน `http://` อย่างเดียว

ทดสอบรันเซิร์ฟเวอร์:

```bash
python manage.py runserver 0.0.0.0:8000
```

*(เปิดดูผ่านเบราว์เซอร์ที่ `http://159.89.198.240:8000/` แล้วกด `Ctrl+C` เพื่อปิด —
ตอนนี้ไฟล์ใน `/static/` จะยังไม่ขึ้นเพราะ `DEBUG=False` จะใช้ได้เมื่อเสิร์ฟผ่าน Apache ในข้อ 9)*

## 9. ติดตั้ง Apache2 และ mod_wsgi

```bash
sudo apt-get install apache2 libapache2-mod-wsgi-py3 -y
sudo a2enmod wsgi
```

สร้างไฟล์ config ของ Apache:

```bash
sudo nano /etc/apache2/sites-available/vibe-coding.conf
```

**วางโค้ดนี้ลงไป:**

```apache
# user=vibe สำคัญ — ถ้าไม่ใส่ daemon จะรันเป็น www-data แล้วอ่าน .env (chmod 600 ของ vibe) ไม่ได้
# และเขียน db.sqlite3 / media ไม่ได้
WSGIDaemonProcess vibe_app user=vibe group=www-data python-path=/home/vibe/Vibe-Coding-101 python-home=/home/vibe/venv

<VirtualHost *:80>
    ServerName 159.89.198.240

    # อัปโหลดได้สูงสุด 10 MB (thumbnail และรูปใน Summernote ซึ่งจำกัดไว้ที่ 5 MB)
    LimitRequestBody 10485760

    # Static Files
    Alias /static /home/vibe/Vibe-Coding-101/staticfiles
    <Directory /home/vibe/Vibe-Coding-101/staticfiles>
        Require all granted
    </Directory>

    # Media Files (thumbnail บทความ + รูปที่อัปโหลดผ่าน Summernote)
    Alias /media /home/vibe/Vibe-Coding-101/media
    <Directory /home/vibe/Vibe-Coding-101/media>
        Require all granted
    </Directory>

    <Directory /home/vibe/Vibe-Coding-101/core>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # WSGI Configuration
    WSGIScriptAlias / /home/vibe/Vibe-Coding-101/core/wsgi.py
    WSGIProcessGroup vibe_app

    ErrorLog ${APACHE_LOG_DIR}/vibe_error.log
    CustomLog ${APACHE_LOG_DIR}/vibe_access.log combined
</VirtualHost>
```

เปิดใช้ site:

```bash
sudo a2ensite vibe-coding
sudo a2dissite 000-default.conf
sudo apache2ctl configtest      # ต้องขึ้น Syntax OK
sudo systemctl restart apache2
```

ปิดคำเตือน `AH00558 … fully qualified domain name` (ไม่บังคับ):

```bash
echo "ServerName 159.89.198.240" | sudo tee /etc/apache2/conf-available/servername.conf
sudo a2enconf servername && sudo systemctl reload apache2
```

## 10. ตั้งค่า Permission ขั้นสุดท้าย

```bash
sudo chmod 755 /home/vibe
cd /home/vibe/Vibe-Coding-101

# รูปที่อัปโหลด — Apache ต้องอ่านได้ และ Django ต้องเขียนได้
sudo chown -R vibe:www-data media
sudo chmod -R 775 media

# ไฟล์ static ที่ collectstatic สร้าง
sudo chown -R vibe:www-data staticfiles
sudo chmod -R 755 staticfiles

# ฐานข้อมูล SQLite — เฉพาะผู้ใช้ vibe (daemon ของ Django) อ่าน/เขียน
# โฟลเดอร์โปรเจกต์ต้องเป็นของ vibe ด้วย เพราะ SQLite สร้างไฟล์ journal ข้าง db.sqlite3
chmod 600 db.sqlite3

# ปิดพอร์ต 8000
sudo ufw delete allow 8000
```

## 11. ตรวจว่าเว็บใช้งานได้

```bash
curl -I http://159.89.198.240/          # ต้องได้ 200
curl -I http://159.89.198.240/blog/     # ต้องได้ 200
curl -I http://159.89.198.240/admin/    # ต้องได้ 302 (ไปหน้า login)
```

แล้วเปิด `http://159.89.198.240/` และ `http://159.89.198.240/admin/` ในเบราว์เซอร์
ล็อกอินด้วย superuser จากข้อ 8 แล้วลองอัปโหลดรูปในบทความเพื่อเช็กว่าเขียน `media/` ได้

> **ควรรู้:** การเข้าผ่าน IP ใช้ได้แค่ `http://` — รหัสผ่านตอนล็อกอิน `/admin/` จะถูกส่งแบบไม่เข้ารหัส
> ถ้าจะเปิดใช้จริงจัง ควรจดโดเมน ชี้ DNS มาที่ `159.89.198.240` แล้วติดตั้ง SSL (เช่น Let's Encrypt)
> จากนั้นเพิ่มโดเมนใน `ServerName` / `ALLOWED_HOSTS` และตั้งค่า HTTPS ตามหัวข้อ
> "สิ่งที่ต้องทำเพิ่มก่อนขึ้น production" ใน `README.md`

## 12. อัปเดตโค้ดภายหลัง (Git Pull)

```bash
cd /home/vibe/Vibe-Coding-101
git pull
source ~/venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart apache2
```

## 13. สำรองข้อมูลอัตโนมัติ (cron)

```bash
mkdir -p ~/backups
crontab -e
```

เพิ่ม:

```cron
# สำรองฐานข้อมูลทุกคืน ตี 2 (เก็บ 14 วัน)
0 2 * * * sqlite3 /home/vibe/Vibe-Coding-101/db.sqlite3 ".backup '/home/vibe/backups/db-$(date +\%F).sqlite3'" && find /home/vibe/backups -name 'db-*.sqlite3' -mtime +14 -delete
# สำรองรูปที่อัปโหลด ทุกวันอาทิตย์ ตี 3
0 3 * * 0 tar -czf /home/vibe/backups/media-$(date +\%F).tar.gz -C /home/vibe/Vibe-Coding-101 media
```

> ใช้ `.backup` ของ `sqlite3` แทนการ `cp` ไฟล์ตรงๆ เพราะได้สำเนาที่สมบูรณ์แม้มีการเขียนข้อมูลอยู่
> ควรคัดลอกไฟล์สำรองเก็บนอกเซิร์ฟเวอร์ด้วย
>
> กู้คืนฐานข้อมูล:
>
> ```bash
> sudo systemctl stop apache2
> cp /home/vibe/backups/db-YYYY-MM-DD.sqlite3 /home/vibe/Vibe-Coding-101/db.sqlite3
> chmod 600 /home/vibe/Vibe-Coding-101/db.sqlite3
> sudo systemctl start apache2
> ```

---

**หมายเหตุ:** ถ้ามีข้อผิดพลาด ดู log ได้ที่:

```bash
sudo tail -f /var/log/apache2/vibe_error.log
```
