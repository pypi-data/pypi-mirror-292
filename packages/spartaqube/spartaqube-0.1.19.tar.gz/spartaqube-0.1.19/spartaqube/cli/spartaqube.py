import typer,utils as utils_cli
from pprint import pprint
from cryptography.fernet import Fernet
import spartaqube_cli as spartaqube_cli
app=typer.Typer()
@app.command()
def sparta_9333c1dcf4(port=None):spartaqube_cli.runserver(port)
@app.command()
def list():spartaqube_cli.list()
@app.command()
def sparta_117f8101e3():spartaqube_cli.sparta_117f8101e3()
@app.command()
def sparta_13a4e9a3b1(ip_addr,http_domain):A=spartaqube_cli.token(ip_addr,http_domain);print(A)
@app.command()
def sparta_35d25e7e83():print('Hello world!')
if __name__=='__main__':app()