from flask import Flask, render_template, request, url_for, redirect, make_response, session
from bs4 import BeautifulSoup
import urllib
import urllib3
import re
import datetime
import pickle

app = Flask(__name__)
app.config["SECRET_KEY"] = 'super secret key'

@app.route('/', methods=['GET', 'POST'])
def home():
    pass

@app.route('/detik', methods=['GET', 'POST'])
def detik():
    # Get URL
    url = 'https://travel.detik.com/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

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

@app.route('/kompas', methods=['GET', 'POST'])
def kompas():
    # Get URL
    url = 'https://indeks.kompas.com/?site=travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

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
            
    for i in links:
        req = urllib.request.Request(i, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup2 = BeautifulSoup(con.read(), 'lxml')

        text_div = soup2.findAll('div', {'class': 'read__content'})
        for i in text_div:
            if i.findAll('p')[0].text == '':
                paragraph.append(i.findAll('p')[1].text)
            elif i.findAll('p')[0] == '<strong></strong>':
                paragraph.append(i.findAll('p')[1].text)
            else:
                paragraph.append(i.findAll('p')[0].text)

    if request.method == 'POST':
        link = request.form.get('link')
        return redirect(url_for('articlekompas', link=link))

    # Send Variables to html template
    return render_template('kompas.html', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes, paragraph=paragraph)

@app.route('/tempo', methods=['GET', 'POST'])
def tempo():
    d = datetime.datetime.today()
    now_date = '{}/{}/{}'.format(d.year, d.month, d.day)

    url = 'https://tempo.co/indeks/' + now_date + '/travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

    news_contents = soup.find_all('ul', {'class': 'wrapper'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        divs = soup2.findAll('div', {'class': 'wrapper clearfix'})
        for div in divs:
            a_div = div.find_all('a')

            links.append(a_div[0]['href'])
            photo_links.append(a_div[0].find('img')['src'])
            titles.append(a_div[1].find('h2').text)
            paragraph.append(a_div[1].find('p').text)
            datetimes.append(a_div[1].find('span').text)

    return render_template('tempo.html', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes, paragraph=paragraph)

@app.route('/articledetik')
def articledetik():
    link = request.args.get('link', None)
    req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    category = soup.find('h4', {'class': 'mt10'})

    # TRAVEL NEWS
    if category == 'TRAVEL NEWS':
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
    if category == 'DOMESTIC DESTINATIONS':
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
    if category == 'INTERNATIONAL DESTINATIONS':
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
    if category == 'TRAVEL-TIPS':
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
    if category == "D'TRAVELERS STORIES":
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
    if category == "D'TRAVELERS PHOTOS":
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
    if category == 'PHOTOS':
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
    if category == 'UGC-BRIDGE':
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
    soup = BeautifulSoup(con.read(), 'lxml')

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

@app.route('/feed/kompas')
def feedkompas():
    # Get URL
    url = 'https://indeks.kompas.com/?site=travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

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
        datetimes.append(i.text)
            
    for i in links:
        req = urllib.request.Request(i, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup2 = BeautifulSoup(con.read(), 'lxml')

        text_div = soup2.findAll('div', {'class': 'read__content'})
        for i in text_div:
            if i.findAll('p')[0].text == '':
                paragraph.append(i.findAll('p')[1].text)
            elif i.findAll('p')[0].text == u'\xa0':
                paragraph.append(i.findAll('p')[1].text)
            else:
                paragraph.append(i.findAll('p')[0].text)

    datetimes_ = []

    day_dict = {
    'Senin': 'Mon',
    'Selasa': 'Tue',
    'Rabu': 'Wed',
    'Kamis': 'Thu',
    "Jum'at": 'Fri',
    'Sabtu': 'Sat',
    'Minggu': 'Sun'
    }

    month_dict = {
        '/01/': ' Jan ',
        '/02/': ' Feb ',
        '/03/': ' Mar ',
        '/04/': ' Apr ',
        '/05/': ' May ',
        '/06/': ' Jun ',
        '/07/': ' Jul ',
        '/08/': ' Aug ',
        '/09/': ' Sep ',
        '/10/': ' Oct ',
        '/11/': ' Nov ',
        '/12/': ' Dec ',
    }

    check_dict = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace(' WIB', ':00 +0700')

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:-16], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d
        d_final = d_final.replace('2019,', '2019')

        datetimes_.append(d_final)

    # Send Variables to html template
    template = render_template('feedkompas.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/detik')
def feeddetik():
    # Get URL
    url = 'https://travel.detik.com/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

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

    for i in photo_div:
        soup2 = BeautifulSoup(str(i), 'lxml')
        photo = soup2.find('img')['src']
        photo_links.append(photo.split("?")[0])

    datetimes_ = []

    day_dict = {
        'Senin': 'Mon',
        'Selasa': 'Tue',
        'Rabu': 'Wed',
        'Kamis': 'Thu',
        "Jumat": 'Fri',
        'Sabtu': 'Sat',
        'Minggu': 'Sun'
    }

    month_dict = {
        'Agu': 'Aug',
        'Okt': 'Oct',
        'Des': 'Dec'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace(' WIB', ':00 +0700')
        d = d.replace('detikTravel | ', '')
        datetimes_.append(d)

    titles_ = []
    for title in titles:
        newchar = ''
        for char in title:
            if char == "'":
                char.replace("'", "\\'")
            newchar += char
        titles_.append(newchar)

    template = render_template('feeddetik.xml', links=links, titles=titles_, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/tempo')
def feedtempo():
    d = datetime.datetime.today()
    now_date = '{}/{}/{}'.format(d.year, d.month, d.day)

    url = 'https://tempo.co/indeks/' + now_date + '/travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

    news_contents = soup.find_all('ul', {'class': 'wrapper'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        divs = soup2.findAll('div', {'class': 'wrapper clearfix'})
        for div in divs:
            a_div = div.find_all('a')

            links.append(a_div[0]['href'])
            photo_links.append(a_div[0].find('img')['src'])
            titles.append(a_div[1].find('h2').text)
            paragraph.append(a_div[1].find('p').text)
            datetimes.append(a_div[1].find('span').text)

    datetimes_ = []

    day_dict = {
        'Senin': 'Mon',
        'Selasa': 'Tue',
        'Rabu': 'Wed',
        'Kamis': 'Thu',
        "Jum'at": 'Fri',
        'Sabtu': 'Sat',
        'Minggu': 'Sun'
    }

    month_dict = {
        'Januari': 'Jan',
        'Februari': 'Feb',
        'Maret': 'Mar',
        'April': 'Apr',
        'Mei': 'May',
        'Juni': 'Jun',
        'Juli': 'Jul',
        'Agustus': 'Aug',
        'September': 'Sep',
        'Oktober': 'Oct',
        'November': 'Nov',
        'Desember': 'Dec',
    }

    check_dict = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace(' WIB', ':00 +0700')

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:-15], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d

        datetimes_.append(d_final)

    template = render_template('feedtempo.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/kumparan')
def feedkumparan():
    url = 'https://kumparan.com/kumparantravel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

    news_contents = soup.find_all('div', {'class': 'Viewweb__StyledView-sc-61094a-0 fPqoSZ'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        divs = soup2.findAll('div', {'class': 'Viewweb__StyledView-sc-61094a-0 fNfbQb'})
        for div in divs:
            title = div.findAll('h2', {'class': 'Textweb__StyledText-sc-2upo8d-0 msdeg'})
            for t in title:
                titles.append(t.text)
                link = t.find('a')['href']
                links.append(link)

        image_div = soup2.findAll('img', {'class': 'no-script'})
        for i in image_div:
            photo_links.append(i['src'])

    links_ = []
    for link in links:
        links_.append('https://kumparan.com' + link)

    for i in links:
        url = 'https://kumparan.com' + i
        req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        d_times = soup3.findAll('div', {'class': 'Viewweb__StyledView-sc-61094a-0 bBekbp'})
        for d in d_times:
            times = d.findAll('div', {'class': 'TextBoxweb__StyledTextBox-n41hy7-0 duIFRd'})
            for t in times:
                spans = t.findAll('span', {'class': 'Textweb__StyledText-sc-2upo8d-0 ceLXoP'})
                for s in spans:
                    datetimes.append(s.text)

        par_div = soup3.findAll('span', {'class': 'Textweb__StyledText-sc-2upo8d-0 dxEmzN'})
        for p in par_div:
            paragraph.append(p.text)

        links_.append(url)

    datetimes_ = []

    day_dict = {
        'Senin': 'Mon',
        'Selasa': 'Tue',
        'Rabu': 'Wed',
        'Kamis': 'Thu',
        "Jum'at": 'Fri',
        'Sabtu': 'Sat',
        'Minggu': 'Sun'
    }

    month_dict = {
        'Agu': 'Aug',
        'Okt': 'Oct',
        'Des': 'Dec'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)
        
        d = d.replace(' WIB', ':00 +0700')
        datetimes_.append(d)

    template = render_template('feedkumparan.xml', links=links_, titles=titles, photo_links=photo_links, datetimes=datetimes, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/kompasiana')
def feedkompasiana():
    url = 'https://www.kompasiana.com/wisata'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

    news_contents = soup.find_all('div', {'class', 'timeline--item timeline--artikel'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        divs = soup2.findAll('div', {'class': 'artikel--img'})
        for div in divs:
            a_divs = div.findAll('a')
            for a in a_divs:
                links.append(a['href'])
                images = a.findAll('img')
                for i in images:
                    titles.append(i['alt'])
                    photo_links.append(i['data-src'].split("?")[0])

    for i in links:
        req = urllib.request.Request(i, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        date_div = soup3.findAll('span', {'class': 'count-item'})
        datetimes.append(date_div[0].text)

        par_div = soup3.findAll('div', {'class': 'read-content col-lg-9 col-md-9 col-sm-9 col-xs-9'})
        for i in par_div:
            par = i.findAll('p')
            paragraph.append(par[0].text)

    datetimes_ = []

    day_dict = {
        'Senin': 'Mon',
        'Selasa': 'Tue',
        'Rabu': 'Wed',
        'Kamis': 'Thu',
        "Jum'at": 'Fri',
        'Sabtu': 'Sat',
        'Minggu': 'Sun'
    }

    month_dict = {
        'Januari': 'Jan',
        'Februari': 'Feb',
        'Maret': 'Mar',
        'April': 'Apr',
        'Mei': 'May',
        'Juni': 'Jun',
        'Juli': 'Jul',
        'Agustus': 'Aug',
        'September': 'Sep',
        'Oktober': 'Oct',
        'November': 'Nov',
        'Desember': 'Dec',
    }

    check_dict = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)
        
        d = d.replace(u'\xa0', u'')
        d = d + ':00 +0700'

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:15], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d

        datetimes_.append(d_final)


    template = render_template('feedkompasiana.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/tripcanvas')
def feedtripcanvas():
    url = 'https://indonesia.tripcanvas.co/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

    news_contents = soup.find_all('div', {'class', 'no-top-margin grid grid-full section not-first-section has-title post-6069 type-section status-publish format-standard hentry'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        image_div = soup2.findAll('div', {'class': 'isobrick-inner'})
        for div in image_div:
            img = div.findAll('img')
            for i in img:
                photo_links.append(i['src'])

        divs = soup2.findAll('h2', {'class': 'title'})
        for div in divs:
            a_div = div.findAll('a')
            links.append(a_div[0]['href'])
            titles.append(a_div[0]['title'])

    datetimes_ = []

    for i in links:
        req = urllib.request.Request(i, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        par_div = soup3.findAll('div', {'class': 'postcontent content'})
        for div in par_div:
            par = div.findAll('h3')
            paragraph.append(par[1].text)

        date_div = soup3.findAll('div', {'class': 'date updated'})
        for div in date_div:
            d_times = div.findAll('p')
            d_span = div.findAll('span')

            d_times[0] = d_span[0]

            dtime = ' '.join(i.text for i in d_times)

            datetimes.append(dtime)

        datetimes_ = []

    day_dict = {
        'Senin': 'Mon',
        'Selasa': 'Tue',
        'Rabu': 'Wed',
        'Kamis': 'Thu',
        "Jum'at": 'Fri',
        'Sabtu': 'Sat',
        'Minggu': 'Sun'
    }

    month_dict = {
        'Agu': 'Aug',
        'Okt': 'Oct',
        'Des': 'Dec'
    }

    check_dict = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d += ' 00:00:00 +0700'

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:-15], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d

        datetimes_.append(d_final)
 
    template = render_template('feedtripcanvas.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/tripcanvasindo')
def feedtripcanvasindo():
    url = 'https://indonesia.tripcanvas.co/id/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    datetimes = []
    paragraph = []

    news_contents = soup.find_all('div', {'class', 'no-top-margin grid grid-full section not-first-section has-title post-6069 type-section status-publish format-standard hentry'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        image_div = soup2.findAll('div', {'class': 'isobrick-inner'})
        for div in image_div:
            img = div.findAll('img')
            for i in img:
                photo_links.append(i['src'])

        divs = soup2.findAll('h2', {'class': 'title'})
        for div in divs:
            a_div = div.findAll('a')
            links.append(a_div[0]['href'])
            titles.append(a_div[0]['title'])

    datetimes_ = []

    for i in links:
        req = urllib.request.Request(i, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        par_div = soup3.findAll('div', {'class': 'postcontent content'})
        for div in par_div:
            par = div.findAll('h3')
            paragraph.append(par[1].text)

        date_div = soup3.findAll('div', {'class': 'date updated'})
        for div in date_div:
            d_times = div.findAll('p')
            d_span = div.findAll('span')

            d_times[0] = d_span[0]

            dtime = ' '.join(i.text for i in d_times)

            datetimes.append(dtime)

        datetimes_ = []

    day_dict = {
        'Senin': 'Mon',
        'Selasa': 'Tue',
        'Rabu': 'Wed',
        'Kamis': 'Thu',
        "Jum'at": 'Fri',
        'Sabtu': 'Sat',
        'Minggu': 'Sun'
    }

    month_dict = {
        'Agu': 'Aug',
        'Okt': 'Oct',
        'Des': 'Dec'
    }

    check_dict = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d += ' 00:00:00 +0700'

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:-15], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d

        datetimes_.append(d_final)
 
    template = render_template('feedtripcanvasindo.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/mytrip')
def feedmytrip123():
    url = 'https://mytrip123.com/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    paragraph = []

    news_contents = soup.find_all('div', {'class', 'td_module_11 td_module_wrap td-animation-stack'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        image_div = soup2.findAll('div', {'class': 'td-module-thumb'})
        for div in image_div:
            a_div = div.findAll('a')
            links.append(a_div[0]['href'])
            titles.append(a_div[0]['title'])

            for a in a_div:
                img = a.findAll('img')
                photo_links.append(img[0]['src'])

        text_div = soup2.findAll('div', {'class': 'td-excerpt'})
        for t in text_div:
            paragraph.append(t.text)
    
    template = render_template('feedmytrip123.xml', news_contents=news_contents, links=links, titles=titles, photo_links=photo_links, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response
    
if __name__ == '__main__':
    app.run(debug=True)
