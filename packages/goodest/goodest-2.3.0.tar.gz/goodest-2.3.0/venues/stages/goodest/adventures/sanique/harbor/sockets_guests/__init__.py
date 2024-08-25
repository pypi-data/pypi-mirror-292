

#\
#
from goodest._essence import retrieve_essence
#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi
import sanic.response as sanic_response
from sanic_limiter import Limiter, get_remote_address
#
#
import json
from os.path import exists, dirname, normpath, join
from urllib.parse import unquote
#
#/

def sockets_guests (packet):
	essence = retrieve_essence ()

	the_sockets = sanic.Blueprint ("sockets", url_prefix = "/sockets")
	
	@the_sockets.websocket ('/')
	async def address_ws_handler(request, ws):
		while True:
			# Receive data from the client
			data = await ws.recv ()  
			
			# Send the received data back to the client
			await ws.send (f"Echo: {data}")  