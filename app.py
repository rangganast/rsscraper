from flask import Flask, render_template, request, url_for, redirect, make_response, session
from bs4 import BeautifulSoup
import urllib
import urllib3
import re
import datetime
import pickle
import string

app = Flask(__name__)
app.config["SECRET_KEY"] = 'super secret key'

@app.route('/', methods=['GET', 'POST'])
def home():
    pass

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
        if len(links) < 10:
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
            paragraph.append(i.findAll('p')[1].text)

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

        if d[5:7].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

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
        if d[:2].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

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
        for before, after in month_dict.items():
            d = d.replace(before, after)

        if d[:2].isdigit() == False:
            d = '0' + d
        
        d = d.replace(u'\xa0', u'')
        d = d + ':00 +0700'

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:15], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d
        d_final = d_final.replace('  ', ' ')

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

        for before, after in month_dict.items():
            d = d.replace(before, after)

        if d[:2].isdigit() == False:
            d = '0' + d      

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
        if d[:2].isdigit() == False:
            d = '0' + d

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
    
    template = render_template('feedmytrip123.xml', links=links, titles=titles, photo_links=photo_links, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/hipwee')
def feedhipwee():
    url = 'https://www.hipwee.com/events/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('article', {'class', 'archive-base top top-event'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')
        
        image_div = soup2.findAll('div', {'class': 'image-post'})
        for div in image_div:
            a_div = div.findAll('a')
            links.append(a_div[0]['href'])

            for a in a_div:
                img_div = a.findAll('img')
                for img in img_div:
                    photo_links.append(img['src'])  

        title_div = soup2.findAll('h2', {'class': 'post-title'})
        for div in title_div:
            a_div = div.findAll('a')
            for a in a_div:
                titles.append(a.text)

        par_div = soup2.findAll('div', {'class': 'post-excerpt'})
        for div in par_div:
            p_div = div.findAll('p')
            paragraph.append(p_div[0].text)

    template = render_template('feedhipwee.xml', links=links, titles=titles, photo_links=photo_links, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response      

@app.route('/feed/tirto')
def feedtirto():
    url = 'https://tirto.id'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('div', {'class': 'container mt-28 container900'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        content_div = soup2.findAll('div')[10]

        row_div = content_div.findAll('div', {'class': 'row'})
        for row in row_div:
            a_div = row.findAll('a')
            for a in a_div:
                links.append(a['href'])
        
        img_div = content_div.findAll('div', {'class': 'col-12 p-0 relative hidden-over'})
        for div in img_div:
            title_div = div.findAll('h1', {'class': 'title-overlay'})
            for title in title_div:
                titles.append(title.text)

            img_div = div.findAll('img')
            for img in img_div:
                photo_links.append(img['src'])

    for link in links:
        req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        d_times = soup3.findAll('span', {'class': 'detail-date mt-1 text-left'})
        for d in d_times:
            d = d.text.split("-")[1]
            d = d[1:]
            datetimes.append(d)

        par_div = soup3.findAll('i', {'class': 'italic ringkasan mb-2'})
        for par in par_div:
            par = par.text
            par = par.replace('\t', '')
            par = par.replace('\r', '')
            par = par.replace('\n', '')
            paragraph.append(par)

    datetimes_ = []

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
        'Desember': 'Dec'
    }

    check_dict = {
        'Jan': 'January',
        'Feb': 'February',
        'Mar': 'March',
        'Apr': 'April',
        'Jun': 'June',
        'Jul': 'July',
        'Aug': 'August',
        'Sep': 'September',
        'Oct': 'October',
        'Nov': 'November',
        'Dec': 'December'
    }

    for d in datetimes:
        if d[:2].isdigit() == False:
            d = '0' + d

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d += ' 00:00:00 +0700'

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:-15], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d

        datetimes_.append(d_final) 

    template = render_template('feedtirto.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/sindonews')
def feedsindonews():
    url = 'https://lifestyle.sindonews.com/travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('div', {'class': 'lst-mr'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        li_div = soup2.findAll('li', {'class': 'clearfix'})
        for li in li_div:
            divs = li.findAll('div')

            img_div = divs[0].findAll('img')
            for img in img_div:
                photo_links.append(img['src'])

            par_div = divs[1].findAll('p')

            a_div = par_div[0].findAll('a')

            for a in a_div:
                links.append(a['href'])
                titles.append(a.text)

            time_div = divs[1].findAll('time')
            for time in time_div:
                datetimes.append(time.text)

            paragraph.append(par_div[1].text)

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
        'Desember': 'Dec'
    }

    for d in datetimes:
        for before, after in day_dict.items():
            d = d.replace(before, after)

        if d[5:7].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace('- ', '')
        d = d.replace(' WIB', ':00 +0700')

        datetimes_.append(d)

    template = render_template('feedsindonews.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/bisnistravel')
def feedbisnistravel():
    url = 'https://traveling.bisnis.com/'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')

    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('div', {'class': 'sub-highlight'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        a_div = soup2.findAll('a')

        links.append(a_div[0]['href'])

        img_div = a_div[0].findAll('img')
        for img in img_div:
            photo_links.append(img['src'].split("?")[0])

        titles.append(a_div[1].text)

    for link in links:
        req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        d_times = soup3.findAll('div', {'class': 'new-description'})
        for d in d_times:
            span_div = d.findAll('span')
            for span in span_div:
                datetimes.append(span.text)

        par_div = soup3.findAll('div', {'class': 'subtitle'})
        for par in par_div:
            paragraph.append(par.text)

    datetimes_ = []

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
        'Desember': 'Dec'
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

        d = d[1:-1]

        if d[:2].isdigit() == False:
            d = '0' + d

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace(u'\xa0' + '|' + u'\xa0' + ' ', '')
        d = d.replace(' WIB', ':00 +0700')
        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:-15], '%d %B %Y').strftime('%a')

        d = day + ', ' + d

        datetimes_.append(d)

    template = render_template('feedbisnistravel.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/kontan')
def feedkontan():
    url = 'https://lifestyle.kontan.co.id/rubrik/51/Wisata'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')
    
    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.findAll('div', {'class': 'list-berita'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        li_div = soup2.findAll('li')
        for li in li_div:
            a_div = li.findAll('a')
            links.append('https://lifestyle.kontan.co.id' + a_div[0]['href'])

            for a in a_div:
                img_div = a.findAll('img')
                for img in img_div:
                    photo_links.append(img['src'])
                    titles.append(img['title'])

            span_div = li.findAll('span', {'class': 'font-gray'})
            for span in span_div:
                datetimes.append(span.text)

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
        'Desember': 'Dec'
    }

    for d in datetimes:

        d = d[1:]

        for before, after in day_dict.items():
            d = d.replace(before, after)

        if d[5:7].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace('/ ', '')
        d = d.replace(' WIB', ':00 +0700')

        datetimes_.append(d)


    template = render_template('feedkontan.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/okezone')
def feedokezone():
    url = 'https://lifestyle.okezone.com/travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')
    
    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.findAll('div', {'class': 'list-contentx'})
    
    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')
        
        li_div = soup2.findAll('li')
        for li in li_div:
            if len(links) < 10:
                divs = li.findAll('div', {'class': 'wp-thumb-news'})
                for div in divs:
                    a_div = div.findAll('a', {'class': 'gabreaking'})
                    for a in a_div:
                        links.append(a['href'].split("?")[0])
                        titles.append(a['title'])

                    img_div = div.findAll('div', {'class': 'thumb-news img-responsive lazy'})
                    photo_links.append(img_div[0]['data-original'])

                content_div = li.findAll('div', {'class': 'content-hardnews'})
                for div in content_div:
                    par_div = div.findAll('p')
                    for par in par_div:
                        paragraph.append(par.text)

    for link in links:
        req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        d_times = soup3.findAll('div', {'class': 'namerep'})
        for d in d_times:
            datetimes.append(d.find('b').text)

    datetimes_ = []

    day_dict = {
        'Senin': 'Mon,',
        'Selasa': 'Tue,',
        'Rabu': 'Wed,',
        'Kamis': 'Thu,',
        "Jum'at": 'Fri,',
        'Sabtu': 'Sat,',
        'Minggu': 'Sun,'
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
        'Desember': 'Dec'
    }

    for d in datetimes:

        for before, after in day_dict.items():
            d = d.replace(before, after)
        
        if d[5:7].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace(' WIB', ':00 +0700')

        datetimes_.append(d)

    template = render_template('feedokezone.xml', news_contents=news_contents, links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/beritasatuwisata')
def feedberitasatuwisata():
    url = 'https://www.beritasatu.com/newsindex/wisata'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')
    
    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('div', {'class': 'media custom-media-index'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        divs = soup2.findAll('div', {'class': 'media-left pr15 media-top'})
        for div in divs:
            a_div = div.findAll('a')
            links.append(a_div[0]['href'])

            for a in a_div:
                image_div = a.findAll('img')
                for img in image_div:
                    photo_links.append(img['data-src'])
                    titles.append(img['alt'])

        content_div = soup2.findAll('div', {'class': 'media-body'})
        for div in content_div:
            span_div = div.findAll('span', {'class':'hz_date_post'})
            for span in span_div:
                datetimes.append(span.text)

            par_div = div.findAll('p', {'class': 'summary-index'})
            for par in par_div:
                par = par.text
                par = par.replace('\t', '')
                par = par.replace('\n', '')
                paragraph.append(par)

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
        'Desember': 'Dec'
    }

    for d in datetimes:

        for before, after in day_dict.items():
            d = d.replace(before, after)

        if d[5:7].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace('| ', '')

        d = d.replace(' WIB', ':00 +0700')

        datetimes_.append(d)

    template = render_template('feedberitasatuwisata.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/beritasatukuliner')
def feedberitasatukuliner():
    url = 'https://www.beritasatu.com/newsindex/kuliner'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')
    
    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('div', {'class': 'media custom-media-index'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        divs = soup2.findAll('div', {'class': 'media-left pr15 media-top'})
        for div in divs:
            a_div = div.findAll('a')
            links.append(a_div[0]['href'])

            for a in a_div:
                image_div = a.findAll('img')
                for img in image_div:
                    photo_links.append(img['data-src'])
                    titles.append(img['alt'])

        content_div = soup2.findAll('div', {'class': 'media-body'})
        for div in content_div:
            span_div = div.findAll('span', {'class':'hz_date_post'})
            for span in span_div:
                datetimes.append(span.text)

            par_div = div.findAll('p', {'class': 'summary-index'})
            for par in par_div:
                par = par.text
                par = par.replace('\t', '')
                par = par.replace('\n', '')
                paragraph.append(par)

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
        'Desember': 'Dec'
    }

    for d in datetimes:

        for before, after in day_dict.items():
            d = d.replace(before, after)

        if d[5:7].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace('| ', '')

        d = d.replace(' WIB', ':00 +0700')

        datetimes_.append(d)

    template = render_template('feedberitasatukuliner.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/pikiranrakyat')
def feedpikiranrakyat():
    url = 'https://www.pikiran-rakyat.com/hidup-gaya'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')
    
    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('div', {'id': 'articles'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        image_div = soup2.findAll('div', {'class': 'd-flex mr-3 align-self-top'})
        for div in image_div:
            img_div = div.findAll('img')
            for img in img_div:
                photo_links.append(img['src'])
        
        content_div = soup2.findAll('div', {'class': 'media-body'})
        for div in content_div:
            title_div = div.findAll('h4')
            for title in title_div:
                titles.append(title.find('a').text)
                links.append('https://pikiran-rakyat.com' + title.find('a')['href'])

            d_times = div.findAll('small', {'class': 'text-muted'})
            for d in d_times:
                datetimes.append(d.text)

            par_div = div.findAll('p')
            for par in par_div:
                paragraph.append(par.text)

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
        d = d[7:-5]

        for before, after in day_dict.items():
            d = d.replace(before, after)

        if d[5:7].isdigit() == False:
            d = d.replace(d[5], '0' + d[5])

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d = d.replace('- ', '') 
        d += ':00 +0700'

        datetimes_.append(d)    
    
    template = render_template('feedpikiranrakyat.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/kemenpar')
def feedkemenpar():
    url = 'http://www.kemenpar.go.id/categories/berita-utama'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')
    
    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.find_all('div', {'class': 'news-col1 wow fadeInUp'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        image_div = soup2.findAll('div', {'class': 'col-md-4'})
        for div in image_div:
            img = div.findAll('img')
            photo_links.append(img[0]['src'])

        content_div = soup2.findAll('div', {'class': 'col-md-8'})
        for div in content_div:
            a_div = div.findAll('a')
            links.append(a_div[0]['href'])

            for a in a_div:
                h5_div = a.findAll('h5')
                titles.append(h5_div[0].text)

            d_times = div.findAll('p', {'class': 'date1'})
            for d in d_times:
                datetimes.append(d.text)

            par_div = div.findAll('p', {'class': 'news-intro1'})
            for par in par_div:
                paragraph.append(par.text)

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
        'Desember': 'Dec'
    }

    for d in datetimes:

        for before, after in day_dict.items():
            d = d.replace(before, after)

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d += ' 00:00:00 +0700'

        datetimes_.append(d)

    template = render_template('feedkemenpar.xml', links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

@app.route('/feed/idntimes')
def feedidntimes():
    url = 'https://www.idntimes.com/travel'
    req = urllib.request.Request(url, headers={'User-Agent': "Magic Browser"})
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con.read(), 'lxml')
    
    titles = []
    links = []
    photo_links = []
    paragraph = []
    datetimes = []

    news_contents = soup.findAll('div', {'class': 'box-latest box-list'})

    for i in news_contents:
        soup2 = BeautifulSoup(str(i), 'lxml')

        if len(links) < 8:
            a_div = soup2.findAll('a')
            links.append(a_div[0]['href'])

            for div in a_div:
                image_div = div.findAll('div', {'class': 'image-latest box-image'})
                for img in image_div:
                    image = img.findAll('img')
                    photo_links.append(image[0]['data-src'])

            content_div = soup2.findAll('div', {'class': 'description-latest box-description'})
            for div in content_div:
                d_times = div.findAll('time', {'class': 'date'})
                datetimes.append(d_times[0].text)

                title_div = div.findAll('h2', {'class': 'title-text'})
                for title in title_div:
                    titles.append(title.text)

    for link in links:                    
        req = urllib.request.Request(link, headers={'User-Agent': "Magic Browser"})
        con = urllib.request.urlopen(req)
        soup3 = BeautifulSoup(con.read(), 'lxml')

        par_div = soup3.findAll('div', {'class': 'excerpt'})
        for par in par_div:
            paragraph.append(par.text)

    datetimes_ = []

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
        'Desember': 'Dec'
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
        d = d[25:-21]

        if d[:2].isdigit() == False:
            d = '0' + d

        for before, after in month_dict.items():
            d = d.replace(before, after)

        d += '00:00:00 +0700'

        d_ = ' '.join([check_dict.get(i, i) for i in d.split()])
        day = datetime.datetime.strptime(d_[:-15], '%d %B %Y').strftime('%a')
        d_final = day + ", " + d

        datetimes_.append(d_final)

    template = render_template('feedidntimes.xml', news_contents=news_contents, links=links, titles=titles, photo_links=photo_links, datetimes=datetimes_, paragraph=paragraph)
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response

if __name__ == '__main__':
    app.run(debug=True)