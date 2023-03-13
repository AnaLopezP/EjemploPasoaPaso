#Importamos todas las librerías necesarias
from urllib.parse import *
from contextlib import closing
from http.client import *
from sys import *
from bs4 import *
from os import sep
from timeit import *
import asyncio
from aiohttp import *
from functools import partial
import html.parser

async def wget(session, uri): #Devuelve el contenido indicado por la URI
    async with session.get(uri) as response: #Conectamos con el servidor y analizamos su respuesta
        if response.status != 200:
            return None #Ha dado error así que pasamos
        if response.content_type.startswith("text/"):
            return await response.text() #que devuelva esto si es un texto
        else:
            return await response.read()
        
async def descargar(session, uri):
    #Para descargar el contenido de la URI
    contenido = await wget(session, uri) #Llamamos a la funcion que nos da la URI
    if contenido is None: #Entramos aquí si la función anterior devuelve None
        return None
    with open(uri.split(sep)[-1], 'wb') as f: #Si no es None, escribimos el contenido en un archivo
        f.write(contenido)
        return uri

async def get_images_src_from_html(doc_html): #cogemos el src de las imágenes 
    soup = BeautifulSoup(doc_html, "html.parser")
    for img in soup.find_all("img"): #buscamos en cada imagen de soup
        yield img.get("src") #cogemos el src
        await asyncio.sleep(0.001) #esperamos 

async def get_uri_from_images_src(base_uri, images_src):
    #Miramos en caso de que la uri sea absoluta o relativa
    #Devuelve cada URI de las imágenes
    #Parseamos el archivo
    mparsed = urlparse(base_uri)
    async for src in images_src:
        parsed = urlparse(src)
        if parsed.netloc == "":
            path = parsed.path
            if parsed.query:
                path += "¿?" + parsed.query
            if path[0] != "/":
                if mparsed.path == "/":
                    path = "/" + path
                else:
                    path = "/" + "/".join(mparsed.path.split("/")[:1]) + "/" + path
            yield mparsed.scheme + "://" + mparsed.netloc + path
            yield parsed.geturl()
        await asyncio.sleep(0.001)


async def get_images(session, page_uri): #Recupera las uri de todas las imagenes de ua pagina
    html = await wget(session, page_uri) #Volvemos a llamar a la funcion wget
    if not html: #Entramos aquí si la web no es html
        print("No se encuentra imagen", stderr)
        return None
    images_src_gen = get_images_src_from_html(html)
    images_uri_gen = get_uri_from_images_src(page_uri, images_src_gen)
    #Ahora recuperamos las imagenes
    async for img in images_uri_gen:
        print("Porcentaje de descarga" %img)
        await descargar(session, img) #Llamamos a la funcion descargar con la imagen 
