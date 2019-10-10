from flask import Flask, render_template, request, url_for, redirect
from bs4 import BeautifulSoup
import requests
import urllib
import urllib3
from urllib.parse import urlparse, urlsplit
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/detik', methods=['GET', 'POST'])
def detik():
    # Get URL
    url = 'https://travel.detik.com/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')

    titles = []
    links = []
    photo_links = []
    
    # Get content div
    news_contents = soup.find_all('div', {'class': 'list__news__content'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        # Get Title
        title = soup2.find('a').text
        titles.append(title)

        # Get Link
        link = soup2.find('a')['href']
        links.append(link)

    # Get Image
    photo_div = soup.find_all('div', {'class': 'list__news__photo pull-left'})

    for i in photo_div:
        soup2 = BeautifulSoup(str(i), 'lxml')
        photo = soup2.find('img')['src']
        photo_links.append(photo)

    if request.method == 'POST':
        link = request.form.get('link')
        return redirect(url_for('article', link=link))

    # Send Variables to html template
    return render_template('detik.html', links=links, titles=titles, photo_links=photo_links)

@app.route('/cnn')
def cnn():
    # Get URL
    url = 'https://www.cnnindonesia.com/gaya-hidup/wisata'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')

    titles = []
    links = []
    photo_links = []

    # Get Content div
    news_contents = soup.find(
        'div', {'class': 'list media_rows middle'}).findAll('article')

    for article in news_contents:

        # Get Title
        for i in article.findAll('h2', {'class': 'title'}):
            titles.append(i.text)

        # Get Link
        link = article.findAll('a')
        for i in link:
            links.append(i['href'])

        # Get Image
        img = article.findAll('img')
        for i in img:
            photo_links.append(i['src'])

    # Send Variables to html template
    return render_template('cnn.html', links=links, titles=titles, photo_links=photo_links)

@app.route('/kompas')
def kompas():
    # Get URL
    url = 'https://travel.kompas.com'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')

    titles = []
    links = []
    photo_links = []

    # Find content div
    news_contents = soup.find_all('div', {'class': 'col-bs9-3'})
    
    for article in news_contents:

        # Get Title
        for i in article.findAll('a', 'article__link'):
            titles.append(i.text)

        # Get Link
        link = article.find('a')['href']
        links.append(link)

        # Get Image
        img = article.find('img')['data-src']
        photo_links.append(img)
    
    # Find content div
    news_contents = soup.find_all('div', {'class': 'col-bs9-6'})

    for article in news_contents:

        # Get Title
        title = article.find('a', {'class': 'article__link'})
        titles.append(title.text)

        # Get Link
        link = article.find('a')['href']
        links.append(link)

        # Get Image
        img = article.find('img')['data-src']
        photo_links.append(img)

    # Send Variables to html template
    return render_template('kompas.html', links=links, titles=titles, photo_links=photo_links)

@app.route('/jakartapost')
def jakartapost():
    # Get URL
    url = 'https://www.thejakartapost.com/travel/news'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')

    titles = []
    links = []
    photo_links = []

    # Find content div
    news_contents = soup.find_all(
        'div', {'class': 'col-md-9 col-xs-12 tjp-Travel-entry'})

    for article in news_contents:
        # Find Title
        for text_div in article.findAll('div', {'class': 'detail-latest'}):
            for i in text_div.findAll('a')[1]:
                for title in i:
                    if title != '\n':
                        titles.append(title.strip())

        # Find Link
        for photo_div in article.findAll('div', {'class': 'image-latest'}):
            for link in photo_div.findAll('a'):
                links.append(link['href'])

        # Find Image
        for photo_div in article.findAll('div', {'class': 'image-latest'}):
            for i in photo_div.findAll('a'):
                for img in i.findAll('img', src=True):
                    photo_links.append(img['data-src'])
    
    # Send Variables to html template
    return render_template('jakartapost.html', links=links, titles=titles, photo_links=photo_links)

@app.route('/article')
def article():
    link = request.args.get('link', None)

    # DETIK
    if re.search('detik.com', link):
        req = urllib.request.Request(
            link, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup = BeautifulSoup(con.read(), 'html.parser')

        category = soup.find('h4', {'class': 'mt10'})

        # TRAVEL NEWS
        if category.text == 'TRAVEL NEWS':
            title = soup.find('h2', {'class': 'mt5'}).text

            image = []
            img = soup.find('picture').find('img')['src']
            image.append(img)

            text_div = soup.find(
                'div', {'class': 'itp_bodycontent read__content pull-left'})

            return render_template('article.html', title=title, image=image, text_div=text_div)

        # DOMESTIC DESTINATIONS
        if category.text == 'DOMESTIC DESTINATIONS':
            title = soup.find('h2', {'class': 'mt5'}).text

            image = []
            img = soup.find('picture').find('img')['src']
            image.append(img)

            text_div = soup.find('div', {'id' : 'detikdetailtext'})

            return render_template('article.html', title=title, image=image, text_div=text_div)

        # INTERNATIONAL DESTINATIONS
        if category.text == 'INTERNATIONAL DESTINATIONS':
            title = soup.find('h2', {'class': 'mt5'}).text

            image = []
            img = soup.find('picture').find('img')['src']
            image.append(img)

            text_div = soup.find('div', {'class' : 'itp_bodycontent read__content pull-left'})

            return render_template('article.html', title=title, image=image, text_div=text_div)

        # TRAVEL-TIPS
        if category.text == 'TRAVEL-TIPS':
            title = soup.find('h2', {'class': 'mt5'}).text

            image = []
            img = soup.find('picture').find('img')['src']
            image.append(img)

            text_div = soup.find('div', {'class' : 'itp_bodycontent read__content pull-left'})

            return render_template('article.html', title=title, image=image, text_div=text_div)

        # D'TRAVELERS STORIES
        if category.text == "D'TRAVELERS STORIES":
            title = soup.find('h2', {'class': 'mt5'}).text

            # Scrape images
            image = []
            inline_texts = []

            caption = soup.find('div', {'class', 'read__photo__count'}).text
            whitelist = set(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
            num = ''.join(filter(whitelist.__contains__, caption))

            numbers = '1234567890'
            if num[-2] in numbers:
                count = int(num[-2:])
            else:
                count = int(num[-1])

            for i in range(1, count+1):
                url = link + '/' + str(i)
                http = urllib3.PoolManager()
                response = http.request('GET', url)
                soup2 = BeautifulSoup(response.data)


                div = soup2.findAll('div', {'class': 'ratio16_9 box_img'})
                for i in div:
                    picture_div = i.findAll('picture', {'class': 'img_con'})
                    for img_div in picture_div:
                        img = img_div.find('img')['src']
                        image.append(img)

                inline = soup2.findAll(
                    'div', {'class': 'read__photo__big__caption'})
                for i in inline:
                    inline_texts.append(i.text)

            text_div = soup.find('div', {'class': 'read__content full mt20'})

            return render_template('article.html', title=title, image=image, text_div=text_div, inline_texts=inline_texts)

        # D'TRAVELERS PHOTOS
        if category.text == "D'TRAVELERS PHOTOS":

            # Scrape title
            title = soup.find('h2', {'class': 'mt5'}).text

            # Scrape images
            image = []
            inline_texts = []
            urls = []
            con_ = []

            div_caption = soup.findAll('div', {'class', 'read__photo__count'})
            for i in div_caption:
                caption = i.text

            whitelist = set(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
            num = ''.join(filter(whitelist.__contains__, caption))

            numbers = '1234567890'
            if num[-2] in numbers:
                count = int(num[-2:])
            else:
                count = int(num[-1])

            for i in range(1, count+1):
                url = link + '/' + str(i)
                urls.append(url)

            for url in urls:
                class NoRedirect(urllib.request.HTTPRedirectHandler):
                    def redirect_request(self, req, fp, code, msg, headers, newurl):
                        return None
                
                req = urllib.request.Request(
                    url, headers={'User-Agent': "Magic Browser"})
                opener = urllib.request.build_opener(NoRedirect)
                urllib.request.install_opener(opener)

                try:
                    con = urllib.request.urlopen(url)
                except urllib.error.HTTPError as e:
                    con = e

                soup2 = BeautifulSoup(con.read(), 'html.parser')
                # response = requests.get(url, allow_redirects=False)
                # soup2 = BeautifulSoup(response.text, 'html.parser')

                div = soup2.findAll('div', {'class': 'ratio16_9 box_img'})
                for i in div:
                    picture_div = i.findAll('picture', {'class': 'img_con'})
                    for img_div in picture_div:
                        img = img_div.find('img')['src']
                        image.append(img)
                        

                inline = soup2.findAll(
                    'div', {'class': 'read__photo__big__caption'})
                for i in inline:
                    inline_texts.append(i.text)

                text_div = soup.find(
                    'div', {'class': 'read__content full mt20'})

            return render_template('article.html', title=title, image=image, text_div=text_div, inline_texts=inline_texts)

        # PHOTOS
        if category.text == 'PHOTOS':
            title = soup.find('h2', {'class': 'mt5'}).text

            # Scrape images
            image = []
            inline_texts = []

            caption = soup.find('div', {'class', 'read__photo__count'}).text
            whitelist = set(
                'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890')
            num = ''.join(filter(whitelist.__contains__, caption))
            
            numbers = '1234567890'
            if num[-2] in numbers:
                count = int(num[-2:])
            else:
                count = int(num[-1])

            for i in range(1, count+1):
                url = link + '/' + str(i)
                http = urllib3.PoolManager()
                response = http.request('GET', url)
                soup2 = BeautifulSoup(response.data)

                img = soup2.find('picture', {'class', 'img_con'}).find('img')['src']
                image.append(img)

                inline = soup2.find('div', {'class': 'read__photo__big__caption'}).find('p')
                inline_texts.append(inline.text)
            
            text_div = soup.find('div', {'class': 'read__content full mt20'}).find('p')

            return render_template('article.html', title=title, image=image, text_div=text_div, inline_texts=inline_texts)

if __name__ == '__main__':
    app.run(debug=True)
