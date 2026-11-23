# Vibe Coding 101 — Blog

บล็อกสอนเขียนโค้ดภาษาไทย สร้างด้วย Django สำหรับผู้เริ่มต้นไปจนถึงระดับกลาง มีระบบหมวดหมู่ ค้นหา แบ่งหน้า และแก้ไขเนื้อหาแบบ rich text ผ่าน Django admin

## ภาพรวมฟีเจอร์

- **บล็อก** — หน้าแรกแสดง hero, บทความแนะนำ (featured) 3 เรื่อง และบทความล่าสุด 6 เรื่อง; หน้ารายละเอียดนับยอดวิว, แสดงบทความก่อนหน้า/ถัดไป และบทความที่เกี่ยวข้องในหมวดเดียวกัน
- **หมวดหมู่ (Category)** — จัดกลุ่มบทความ กรองรายการบทความตามหมวดได้ผ่าน query string
- **ค้นหา** — ค้นจากชื่อเรื่อง สรุป และเนื้อหาบทความ (`?q=`)
- **Pagination** — แบ่งหน้าละ 6 บทความ ลิงก์เปลี่ยนหน้าคงค่าคำค้นหา/หมวดหมู่ที่เลือกไว้เสมอ
- **Summernote** — แก้ไขเนื้อหาบทความแบบ rich text (WYSIWYG) ใน Django admin พร้อมอัปโหลดรูปภาพแนบ
- **Admin** — จัดการ Category และ Post ผ่าน Django admin (แก้ไขสถานะ/บทความแนะนำแบบ inline, ค้นหา, กรองตามสถานะ/หมวดหมู่/วันที่)

## เทคโนโลยีที่ใช้

| เทคโนโลยี | เวอร์ชัน | หมายเหตุ |
|---|---|---|
| Python | 3.12.14 | |
| Django | 5.2.17 | เว็บเฟรมเวิร์กหลัก |
| django-summernote | 0.8.20.0 | rich text editor สำหรับเนื้อหาบทความ |
| Pillow | 12.3.0 | ประมวลผลรูปภาพ (ImageField) |
| python-dotenv | 1.2.3 | โหลดตัวแปรแวดล้อมจาก `.env` |
| SQLite | (built-in) | ฐานข้อมูลสำหรับ dev |
| Tailwind CSS | Play CDN (ล่าสุด, ไม่ล็อกเวอร์ชัน) | โหลดผ่าน `cdn.tailwindcss.com` ใน `base.html` |
| IBM Plex Sans Thai | Google Fonts | ฟอนต์หลักของเว็บไซต์ |

## วิธีติดตั้ง

### macOS / Linux

```bash
git clone <URL ของ repo นี้>
cd Vibe-Coding-101

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# นำค่าที่ได้ไปแทนที่ SECRET_KEY ในไฟล์ .env

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_ai_posts --count 12 --author <username ที่สร้างไว้>
python manage.py runserver
```

### Windows (PowerShell)

```powershell
git clone <URL ของ repo นี้>
cd Vibe-Coding-101

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

copy .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# นำค่าที่ได้ไปแทนที่ SECRET_KEY ในไฟล์ .env

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_ai_posts --count 12 --author <username ที่สร้างไว้>
python manage.py runserver
```

เปิดเบราว์เซอร์ไปที่ `http://127.0.0.1:8000/` และ `http://127.0.0.1:8000/admin/` (ล็อกอินด้วย superuser ที่สร้างไว้)

## โครงสร้างโปรเจกต์

```
Vibe-Coding-101/
├── manage.py                       # entry point สำหรับรันคำสั่ง Django ทั้งหมด
├── requirements.txt                # รายการ dependency และเวอร์ชันที่ล็อกไว้
├── .env.example                    # ตัวอย่างตัวแปรแวดล้อม คัดลอกเป็น .env ก่อนรัน
├── .gitignore                      # ไฟล์/โฟลเดอร์ที่ไม่ให้ git ติดตาม
├── db.sqlite3                      # ฐานข้อมูล SQLite ของ dev (ไม่ขึ้น git)
├── core/                           # โปรเจกต์ Django หลัก
│   ├── settings.py                 # ตั้งค่าแอป, database, static/media, summernote
│   ├── urls.py                     # URL routing ระดับโปรเจกต์ (admin, summernote, blog)
│   ├── wsgi.py                     # entry point สำหรับ production server เช่น gunicorn
│   └── asgi.py                     # entry point สำหรับ async server
├── blog/                           # แอป Django หลักของบล็อก
│   ├── models.py                   # โมเดล Category และ Post
│   ├── views.py                    # หน้าแรก, รายการบทความ, หน้ารายละเอียด
│   ├── urls.py                     # URL routing ของแอป blog
│   ├── admin.py                    # ตั้งค่า Django admin และ summernote สำหรับ Post
│   ├── migrations/                 # ประวัติการเปลี่ยนแปลงโครงสร้างฐานข้อมูล
│   ├── management/
│   │   └── commands/
│   │       └── seed_ai_posts.py    # คำสั่งใส่ข้อมูลบทความตัวอย่างเกี่ยวกับ AI
│   └── templates/blog/
│       ├── post_list.html          # เทมเพลตหน้ารายการบทความ (ค้นหา/กรอง/pagination)
│       └── post_detail.html        # เทมเพลตหน้ารายละเอียดบทความ
├── templates/                      # เทมเพลตระดับโปรเจกต์
│   ├── base.html                   # เลย์เอาต์หลัก (navbar, footer, Tailwind CDN)
│   ├── index.html                  # หน้าแรก (hero, featured, บทความล่าสุด)
│   └── partials/
│       ├── navbar.html             # แถบเมนูด้านบน แบบ responsive มี hamburger menu
│       └── footer.html             # ส่วนท้ายเว็บไซต์
├── static/                         # ไฟล์ static ระดับโปรเจกต์ (css/js/img)
└── media/                          # ไฟล์ที่ผู้ใช้อัปโหลด เช่น thumbnail ของบทความ
```

## ตารางสรุป URL

| URL | View | คำอธิบาย |
|---|---|---|
| `/` | `blog.views.index` | หน้าแรก: hero, บทความแนะนำ 3 เรื่อง, บทความล่าสุด 6 เรื่อง |
| `/blog/` | `blog.views.post_list` | รายการบทความทั้งหมด แบ่งหน้าละ 6 เรื่อง |
| `/blog/?q=<คำค้นหา>` | `blog.views.post_list` | ค้นหาบทความจากชื่อเรื่อง/สรุป/เนื้อหา |
| `/blog/?category=<slug>` | `blog.views.post_list` | กรองบทความตามหมวดหมู่ |
| `/blog/?page=<เลขหน้า>` | `blog.views.post_list` | เปลี่ยนหน้า (คงค่า q/category เดิมไว้) |
| `/blog/<slug>/` | `blog.views.post_detail` | หน้ารายละเอียดบทความ (นับยอดวิวอัตโนมัติ) |
| `/admin/` | Django admin | จัดการ Category และ Post หลังบ้าน |
| `/summernote/` | django-summernote | endpoint สำหรับอัปโหลดไฟล์แนบในตัวแก้ไข rich text |

## วิธีรัน seed_ai_posts

คำสั่งนี้เพิ่มข้อมูลบทความตัวอย่างเกี่ยวกับ AI จำนวน 12 เรื่อง พร้อม 6 หมวดหมู่ (Machine Learning, Deep Learning, Generative AI, Prompt Engineering, AI Ethics, AI Tools) โดยต้องมี superuser อยู่ในระบบก่อน:

```bash
python manage.py createsuperuser   # ถ้ายังไม่มี user
python manage.py seed_ai_posts --count 12 --author admin
```

อาร์กิวเมนต์ที่ใช้ได้:

| อาร์กิวเมนต์ | ค่าเริ่มต้น | คำอธิบาย |
|---|---|---|
| `--count` | `12` | จำนวนบทความที่จะสร้าง (มีข้อมูลเตรียมไว้สูงสุด 12 เรื่อง) |
| `--clear` | ปิดอยู่ | ลบ Post และ Category เดิมทั้งหมดก่อนสร้างข้อมูลใหม่ |
| `--author` | `admin` | username ของผู้เขียนบทความ ต้องมีอยู่จริงในระบบ |

คำสั่งนี้ทำงานแบบ idempotent (ใช้ `get_or_create` อิง title) รันซ้ำได้โดยไม่สร้างข้อมูลซ้ำ

## สิ่งที่ต้องทำเพิ่มก่อนขึ้น production

ตรวจด้วย `python manage.py check --deploy` แล้วต้องแก้ตามนี้ (ทุกข้อเกี่ยวกับตอนที่ไซต์วิ่งบน HTTPS จริงแล้วเท่านั้น):

- **DEBUG** — ตั้ง `DEBUG=False` ใน `.env` ของ production เสมอ
- **SECRET_KEY** — สร้างค่าใหม่เฉพาะ production ด้วย `get_random_secret_key()` ห้ามใช้ค่าเดียวกับ dev หรือค่าใน `.env.example`
- **ALLOWED_HOSTS** — เปลี่ยนจาก `*` เป็นโดเมนจริงเท่านั้น เช่น `ALLOWED_HOSTS=vibecoding101.dev,www.vibecoding101.dev`
- **SECURE_SSL_REDIRECT** — ตั้งเป็น `True` เมื่อมี HTTPS ให้ทุก request ถูก redirect ไป https อัตโนมัติ
- **SECURE_HSTS_SECONDS** — ตั้งค่า (เช่น `31536000`) หลังยืนยันแล้วว่าทั้งไซต์วิ่งบน HTTPS ล้วน ตั้งผิดจังหวะจะ lock ผู้ใช้ออกจาก HTTP ถาวร
- **SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE** — ตั้งเป็น `True` ทั้งคู่ ให้ cookie ส่งได้เฉพาะผ่าน HTTPS
- **X_FRAME_OPTIONS** — ปัจจุบันตั้งเป็น `SAMEORIGIN` โดยตั้งใจ เพราะ django-summernote รัน editor อยู่ใน iframe ต้องคงค่านี้ไว้ (ห้ามเปลี่ยนเป็น `DENY` ไม่งั้น summernote จะพังใน admin)
- **ฐานข้อมูล** — ย้ายจาก SQLite ไปใช้ PostgreSQL หรือฐานข้อมูลที่รองรับ concurrent write สำหรับ production
- **Static/Media files** — รัน `python manage.py collectstatic` และเสิร์ฟผ่าน WhiteNoise/Nginx/CDN; media (รูปที่ผู้ใช้อัปโหลด) ควรย้ายไป object storage เช่น S3 แทนดิสก์ของเซิร์ฟเวอร์
- **WSGI server** — รันผ่าน gunicorn/uwsgi หลัง reverse proxy (Nginx) แทน `runserver` ที่ใช้ได้เฉพาะ dev
- **Backup** — ตั้ง backup ฐานข้อมูลและ media เป็นประจำ
- **Logging/Monitoring** — ตั้งค่า logging และเครื่องมือ error monitoring (เช่น Sentry) ก่อนเปิดใช้งานจริง
