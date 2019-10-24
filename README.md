# Flask Web Scraper

Project ini adalah web yang berisi berita/informasi mengenai travelling yang di-scrape dari kanal-kanal berita di Indonesia.

### Prerequisites

Python 3.6.8

```
Download di https://www.python.org/downloads/
```

### Cara Install dan Setelahnya

Python 3.6.8

```
Install di windows seperti biasa. Centang add path jika ada.
Setelah Install buat sebuah Virtual Environment.
Environment adalah lingkungan pekerjaan khusus dibuat sesuai kebutuhan.
```

Install Virtual Environment

```
1. Instal Virtual Environment Maker dengan command "pip install virtualenv"
2. Buat Environment dengan command "python3 -m venv <nama environment>"
3. Aktivasi environment dengan command "<nama environment>\Scripts\Activate"
4. Instal package di vritual environment dengan command "pip install <nama package>==<versi package>"
```

Packages Requirement List

```
beautifulsoup4==4.8.1
bs4==0.0.1
Click==7.0
Flask==1.1.1
gunicorn==19.9.0
itsdangerous==1.1.0
Jinja2==2.10.3
lxml==4.4.1
MarkupSafe==1.1.1
pipdeptree==0.13.2
soupsieve==1.9.4
urllib3==1.25.6
Werkzeug==0.16.0
Datetime
Re

*Jika tidak ada versi package, maka package sudah built-in saat membuat virtual environment
```

## Cara Pakai dan testing

```
Untuk menjalankan dan memakai web:
1. Buka CMD, arahkan ke folder yang terdapat app.py di dalamnya
2. Jalankan dengan command "python app.py"
3. Buka alamat ip yang disediakan oleh program
4. Jika ingin menampilkan error, tambahkan "debug=True" pada baris app.run(<taruh di sini>)
```

## Authors

* **Rangga Aziz** - *Initial work* - [rangganast](https://github.com/rangganast)
