from bs4 import BeautifulSoup
import csv
import html5lib
from urllib.request import urlopen
import schedule
import time
import datetime
import redis
import os
import requests

class clase:
    nombre = ''
    edificio=''
    numero=''
    horario=''
    dias=''
    link=''

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"

def scrape():
    listaSalones=[]
    log("solicitando principal")
    page = request("https://registroapps.uniandes.edu.co/scripts/semestre/adm_con_horario_joomla.php")

    soup = BeautifulSoup( page , 'html5lib')

    for unaClase in soup.find_all('a'):
        nuevaClase = clase()
        nuevaClase.nombre=unArticulo.a.string
        nuevaClase.link=unArticulo.a['href']
        nuevaClase.contenido=""

        is_relative_article_link = nuevoArticulo.link.startswith('..')
        if is_relative_article_link:
            nuevaClase.link = "https://registroapps.uniandes.edu.co/scripts" + nuevoArticulo.link.split('..')[1]
        noodles = BeautifulSoup(request(nuevoArticulo.link),'html5lib')
        nuevoArticulo.contenido = (noodles.find('div',class_="item-text"))

        if nuevoArticulo.contenido != None:
            nuevoArticulo.fecha = noodles.find('h3', class_="header-date")
            nuevoArticulo.imagen = noodles.find('a', class_="article-image").get("href")
            log(nuevoArticulo.imagen)
            listaArticulos.append(nuevoArticulo)

    elcsv = serialize_articles(listaArticulos)
    store(elcsv)
    log("termine")
    print(datetime.datetime.now())

def request(url):
    log("requesting " + url)
    custom_headers = {
        'user-agent' : USER_AGENT ,
        'accept': "text/html;charset=UTF-8"
    }
    response = requests.get(url , headers = custom_headers)
    response.encoding="utf-8"
    return response.text

def log(algo):
    prefix = '[' + timestamp() + '] '
    print( prefix + algo)

def timestamp():
    return datetime.datetime.now().strftime("%m/%d/%y %H:%M:%S")

def serialize_articles(lista):
    articulos = map(serialize_article, lista)
    finalCsv =  "titulo,link,contenido,fecha,imagen\n" + '\n'.join(articulos)
    return finalCsv

def serialize_article(article):
    line_elements = [
        article.titulo,
        article.link,
        article.contenido,
        article.fecha,
        article.imagen
    ]
    clean_line_elements = map(applyFormatEscaping , line_elements )
    final_line = ','.join(clean_line_elements)
    return final_line

def applyFormatEscaping(data):
    return  '"' + str(data).replace('"', "'") + '"'

def store(content):
    r = redis.from_url(os.environ.get('REDIS_URL'))
    r.set('news' , content.encode('utf8'))



scrape()
schedule.every(5).minutes.do(scrape)
while True:
    schedule.run_pending()
    time.sleep(1)