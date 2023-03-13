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
        
