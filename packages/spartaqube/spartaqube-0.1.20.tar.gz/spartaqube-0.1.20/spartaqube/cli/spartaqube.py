import typer,utils as utils_cli
from pprint import pprint
from cryptography.fernet import Fernet
import spartaqube_cli as spartaqube_cli
app=typer.Typer()
@app.command()
def sparta_350c6be82e(port=None):spartaqube_cli.runserver(port)
@app.command()
def list():spartaqube_cli.list()
@app.command()
def sparta_a1672ff818():spartaqube_cli.sparta_a1672ff818()
@app.command()
def sparta_02bdd5f1f3(ip_addr,http_domain):A=spartaqube_cli.token(ip_addr,http_domain);print(A)
@app.command()
def sparta_d5513887c6():print('Hello world!')
if __name__=='__main__':app()