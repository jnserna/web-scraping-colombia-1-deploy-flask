import flask
from flask import Flask, render_template, request, jsonify

from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup as soup
import requests
import numpy as np
import re

app=Flask(__name__)

@app.route('/')
def index():
	""" 
	Acceder a la portada inicial de la app.
	Ejecución: http://host:port
	""" 
	return flask.render_template('index.html')


def buscar(producto):
	"""
	Buscar el producto en Homecenter
	"""

	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	headers={'User-Agent':user_agent,} 

	lista_productos = []
	lista_productos.append(['Descripción','Marca','Precio Final','Precio Normal','Precio Final CMR','Precio Normal CMR','Precio Final Internet','Precio Normal Internet','Unidad Precio','Enlace Web'])

	my_url = 'https://www.homecenter.com.co/homecenter-co/search/?Ntt=' + producto
	my_url=requests.get(my_url).url
	request=Request(my_url,None,headers) 
	response = urlopen(request)
	page_html = response.read().decode(encoding="iso-8859-1")
	response.close()
	page_soup = soup(page_html, "html.parser")
	p = page_soup.findAll("ul",{"class":"jsx-4278284191 page-indicies"})
	if p != [] :
		lenp=len(p[0])
		pages = np.arange(1, lenp+1, 1)
	else: 
		pages = np.arange(1, 2, 1)
		
	for page in pages:
		
		my_url = 'https://www.homecenter.com.co/homecenter-co/search/?Ntt=' + producto
		my_url=requests.get(my_url).url + "&currentpage=" + str(page)

		request=Request(my_url,None,headers) 
		response = urlopen(request)
		page_html = response.read().decode(encoding="iso-8859-1")
		response.close()

		# html parsing
		page_soup = soup(page_html, "html.parser")

		# grabs each product
		containers = page_soup.findAll("div",{"class":"jsx-411745769 product ie11-product-container"})

		for container in containers: 

			descripcion = container.findAll("h2",{"class":"jsx-411745769 product-title"})
			descripcion = descripcion[0].text.replace(",","")

			marca = container.findAll("div",{"class":"jsx-411745769 product-brand"})
			if len(marca) !=0:
				marca = marca[0].text
			else:
				marca=""

			precio_fin = container.findAll("div",{"class":"jsx-585964327 main gridView"})
			if len(precio_fin) != 0:
				precio_fin = precio_fin[0].text
			else:
				precio_fin = ""

			precio_full = container.findAll("div",{"class":"jsx-585964327 sub gridView"})
			if len(precio_full) !=0:
				precio_full = precio_full[0].text.replace("Normal:","")
			else:
				precio_full = ""

			precio_fin_CMR = container.findAll("div",{"class":"jsx-585964327 main gridView CMR"})
			if len(precio_fin_CMR) != 0:
				precio_fin_CMR = precio_fin_CMR[0].text
			else:
				precio_fin_CMR = ""

			precio_full_CMR = container.findAll("div",{"class":"jsx-585964327 sub gridView CMR"})
			if len(precio_full_CMR) !=0:
				precio_full_CMR = precio_full_CMR[0].text.replace("Normal:","")
			else:
				precio_full_CMR = ""
				
			precio_fin_int = container.findAll("div",{"class":"jsx-585964327 main gridView INTERNET"})
			if len(precio_fin_int) != 0:
				precio_fin_int = precio_fin_int[0].text
			else:
				precio_fin_int = ""

			precio_full_int = container.findAll("div",{"class":"jsx-585964327 sub gridView INTERNET"})
			if len(precio_full_int) !=0:
				precio_full_int = precio_full_int[0].text.replace("Normal:","")
			else:
				precio_full_int = ""


			unidad = container.findAll("span",{"class":"jsx-4135487716 price-unit"})
			if len(unidad) != 0:
				unidad = unidad[0].text
			else: unidad=""

			enlace = "https://www.homecenter.com.co"+container.a["href"]

			precio_fin=re.sub(r'([a-z]|ã)', '',precio_fin.lower())
			precio_full=re.sub(r'([a-z]|ã)', '',precio_full.lower())
			precio_fin_CMR=re.sub(r'([a-z]|ã)', '',precio_fin_CMR.lower())
			precio_full_CMR=re.sub(r'([a-z]|ã)', '',precio_full_CMR.lower())
			precio_fin_int=re.sub(r'([a-z]|ã)', '',precio_fin_int.lower())
			precio_full_int=re.sub(r'([a-z]|ã)', '',precio_full_int.lower())


			lista_productos.append([descripcion,marca,precio_fin,precio_full,precio_fin_CMR,precio_full_CMR,precio_fin_int,precio_full_int,unidad,enlace])

	return lista_productos


@app.route('/consultar', methods = ['POST'])
def result():
	"""
	Buscar el producto en Homecenter
	"""
	if request.method == 'POST':
		result = buscar(request.form["producto"])
		
		return render_template('index.html', items=result)

if __name__ == '__main__':
	app.run(debug=True)
