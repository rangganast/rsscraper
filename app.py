from flask import Flask, render_template, request, url_for, redirect, make_response, session
from bs4 import BeautifulSoup
import urllib
import urllib3

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
    datetimes = []
    paragraph = []
    
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

        # Get Time
        time = soup2.findAll('div', {'class': 'date'})
        for d in time:
            datetimes.append(d.text)

        # Get paragraph
        par = soup2.find('p').text
        paragraph.append(par)

    # Get Image
    photo_div = soup.find_all('div', {'class': 'list__news__photo pull-left'})

    session['links'] = links
    session['titles'] = titles
    session['photo_links'] = photo_links
    session['datetimes'] = datetimes
    session['paragraph'] = paragraph

    for i in photo_div:
        soup2 = BeautifulSoup(str(i), 'lxml')
        photo = soup2.find('img')['src']
        photo_links.append(photo)

    if "link" in request.form:
        if request.method == 'POST':
            link = request.form.get('link')
            return redirect(url_for('articledetik', link=link))

    if "rss" in request.form:
        if request.method == 'POST':
            return redirect(url_for('detikfeed'))

    # Send Variables to html template
    return render_template('detik.html', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes, paragraph=paragraph)

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
        for i in article.findAll('h1', {'class': 'title'}):
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

@app.route('/kompas', methods=['GET', 'POST'])
def kompas():
    # Get URL
    url = 'https://indeks.kompas.com/?site=travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')

    titles = []
    links = []
    photo_links = []
    datetimes = []

    # Find content div
    news_contents = soup.findAll('div', {'class': 'article__asset'})
    
    for article in news_contents:

        # Get Links
        link_div = article.findAll('a')
        for i in link_div:
            link = i['href']
            links.append(link)
            
            # Get image and title
            img_div = i.findAll('img')
            for img in img_div:
                photo_links.append(img['src'])
                titles.append(img['alt'])

    time_div = soup.findAll('div', {'class': 'article__date'})
    for i in time_div:
        datetimes.append('Kompas Travel | ' + i.text)
            
    if "link" in request.form:
        if request.method == 'POST':
            link = request.form.get('link')
            return redirect(url_for('articledetik', link=link))

    if "rss" in request.form:
        if request.method == 'POST':
            return redirect(url_for('detikfeed'))

    # Send Variables to html template
    return render_template('kompas.html', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes)

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

@app.route('/articledetik', methods=['GET', 'POST'])
def articledetik():
    link = request.args.get('link', None)
    req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')

    category = soup.find('h4', {'class': 'mt10'})

    # TRAVEL NEWS
    if category.text == 'TRAVEL NEWS':
        # Delete tags
        for div in soup.find_all('div', {'class': 'detail_tag'}):
            div.decompose()

        for a in soup.find_all('a', {'class': 'embed'}):
            a.decompose()

        for strong in soup.find_all('strong'):
            strong.decompose()

        # Scrape title
        title = soup.find('h1', {'class': 'mt5'}).text

        # Scrape images
        image = []
        img = soup.find('picture').find('img')['src']
        image.append(img)

        # Scrape datetimes
        time = soup.findAll('div', {'class': 'date'})
        for d in time:
            datetimes = d.text

        # Scrape content
        text_div = soup.find('div', {'class': 'itp_bodycontent read__content pull-left'})

        return render_template('articledetik.html', title=title, image=image, text_div=text_div, datetimes=datetimes)

    # DOMESTIC DESTINATIONS
    if category.text == 'DOMESTIC DESTINATIONS':
        # Delete tags
        for div in soup.find_all('div', {'class': 'detail_tag'}):
            div.decompose()

        for a in soup.find_all('a', {'class': 'embed'}):
            a.decompose()

        for strong in soup.find_all('strong'):
            strong.decompose()

        title = soup.find('h1', {'class': 'mt5'}).text

        image = []
        img = soup.find('picture').find('img')['src']
        image.append(img)

        time = soup.findAll('div', {'class': 'date'})
        for d in time:
            datetimes = d.text

        text_div = soup.find('div', {'id' : 'detikdetailtext'})

        return render_template('articledetik.html', title=title, image=image, text_div=text_div, datetimes=datetimes)

    # INTERNATIONAL DESTINATIONS
    if category.text == 'INTERNATIONAL DESTINATIONS':
        # Delete tags
        for div in soup.find_all('div', {'class': 'detail_tag'}):
            div.decompose()

        for a in soup.find_all('a', {'class': 'embed'}):
            a.decompose()

        for strong in soup.find_all('strong'):
            strong.decompose()
            
        title = soup.find('h1', {'class': 'mt5'}).text

        image = []
        img = soup.find('picture').find('img')['src']
        image.append(img)

        time = soup.findAll('div', {'class': 'date'})
        for d in time:
            datetimes = d.text

        text_div = soup.find('div', {'class' : 'itp_bodycontent read__content pull-left'})

        return render_template('articledetik.html', title=title, image=image, text_div=text_div, datetimes=datetimes)

    # TRAVEL-TIPS
    if category.text == 'TRAVEL-TIPS':
        # Delete tags
        for div in soup.find_all('div', {'class': 'detail_tag'}):
            div.decompose()

        for a in soup.find_all('a', {'class': 'embed'}):
            a.decompose()

        for strong in soup.find_all('strong'):
            strong.decompose()
            
        title = soup.find('h1', {'class': 'mt5'}).text

        image = []
        img = soup.find('picture').find('img')['src']
        image.append(img)

        time = soup.findAll('div', {'class': 'date'})
        for d in time:
            datetimes = d.text

        text_div = soup.find('div', {'class' : 'itp_bodycontent read__content pull-left'})

        return render_template('articledetik.html', title=title, image=image, text_div=text_div, datetimes=datetimes)

    # D'TRAVELERS STORIES
    if category.text == "D'TRAVELERS STORIES":
        # Scrape title
        title = soup.find('h1', {'class': 'mt5'}).text

        # Scrape images
        image = []
        inline_texts = []

        div = soup.findAll('span', {'class': 'img_con lqd'})

        for elem in div:
            img = elem.find('img')['src']
            image.append(img.replace("?w=200&q=90", "?w=600&q=90"))

            text = elem.find('img')['alt']
            inline_texts.append(text)

        text_div = ''

        p_header = soup.findAll('div', {'class': 'clearfix detail_wrap'})

        p_div = soup.findAll('p')
        p_div = p_div[1:]

        for p in p_div:
            p_header.append(p)
        
        for text in p_header:
            text_div += str(text)

        time = soup.findAll('div', {'class': 'date'})
        for d in time:
            datetimes = d.text

        return render_template('articledetik.html', title=title, image=image, text_div=text_div, inline_texts=inline_texts, datetimes=datetimes)

    # D'TRAVELERS PHOTOS
    if category.text == "D'TRAVELERS PHOTOS":
        # Scrape title
        title = soup.find('h1', {'class': 'mt5'}).text

        # Scrape images
        image = []
        inline_texts = []

        div = soup.findAll('span', {'class': 'img_con lqd'})

        for elem in div:
            img = elem.find('img')['src']
            image.append(img.replace("?w=200&q=90", "?w=600&q=90"))

            text = elem.find('img')['alt']
            inline_texts.append(text)

        time = soup.findAll('div', {'class': 'date'})
        for d in time:
            datetimes = d.text

        text_div = soup.find('div', {'class': 'read__content full mt20'})

        return render_template('articledetik.html', title=title, image=image, text_div=text_div, inline_texts=inline_texts, datetimes=datetimes)

    # PHOTOS
    if category.text == 'PHOTOS':
        title = soup.find('h1', {'class': 'mt5'}).text

        # Scrape images
        image = []
        inline_texts = []

        caption = soup.find('div', {'class': 'read__photo__count'}).text
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
                img_div = i.findAll('picture', {'class': 'img_con'})
                for i in img_div:
                    img = i.find('img')['src']
                    image.append(img.replace("?w=300&q=", "?w=600&q=90"))

            inline = soup2.findAll('div', {'class': 'read__photo__big__caption'})
            for i in inline:
                inline_text = i.find('p')
                inline_texts.append(inline_text.text)

        time = soup.findAll('div', {'class': 'date'})
        for d in time:
            datetimes = d.text
        
        text_div = soup.find('div', {'class': 'read__content full mt20'}).find('p')

        return render_template('articledetik.html', title=title, image=image, text_div=text_div, inline_texts=inline_texts, datetimes=datetimes)

    # UGC-BRIDGE
    if category.text == 'UGC-BRIDGE':
            # Delete tags
            for div in soup.find_all('div', {'class': 'detail_tag'}):
                div.decompose()

            for a in soup.find_all('a', {'class': 'embed'}):
                a.decompose()

            for strong in soup.find_all('strong'):
                strong.decompose()

            # Scrape title
            title = soup.find('h1', {'class': 'mt5'}).text

            # Scrape images
            image = []
            img = soup.find('picture').find('img')['src']
            image.append(img)

            # Scrape datetimes
            time = soup.findAll('div', {'class': 'date'})
            for d in time:
                datetimes = d.text

            # Scrape content
            text_div = soup.find(
                'div', {'class': 'itp_bodycontent read__content pull-left'})

            return render_template('articledetik.html', title=title, image=image, text_div=text_div, datetimes=datetimes)

@app.route('/articlekompas')
def articlekompas():
    url = request.args.get('link', None)
    link = url + '?page=all'
    req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    inline_texts = []

    # Scrape title
    title = soup.find('h1', {'class': 'read__title'}).text

    # Scrape images
    image = []
    div_photo = soup.findAll('div', {'class': 'col-bs10-7 js-read-article'})
    for i in div_photo:
        div = i.findAll('div', {'class': 'photo'})
        for i in div:
            img = i.findAll('img', {"data-src": True})
            for i in img:
                image.append(i['data-src'])

    # Scrape content
    text_div = soup.find('div', {'class': 'read__content'})

    # Scrape time
    time = soup.findAll('div', {'class': 'read__time'})
    for i in time:
        datetimes.append(i.text)
    
    return render_template('articlekompas.html', title=title, image=image, text_div=text_div, datetimes=datetimes, inline_texts=inline_texts)

@app.route('/feed/detik')
def detikfeed():
    titles = session['titles']
    links = session['links']
    paragraph = session['paragraph']

    photo_links = []
    for link in session['photo_links']:
        photo_links.append(link.split("?")[0])

    datetimes = []
    for res in session['datetimes']:
        res = res.replace(' WIB', ':00 +0700')
        res = res.replace('detikTravel | ', '')
        datetimes.append(res)

    template = render_template('detikfeed.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(host='0.0.0.0', debug=True)
