import typer,utils as utils_cli
from pprint import pprint
from cryptography.fernet import Fernet
import spartaqube_cli as spartaqube_cli
app=typer.Typer()
@app.command()
def sparta_8056318f37(port=None):spartaqube_cli.runserver(port)
@app.command()
def list():spartaqube_cli.list()
@app.command()
def sparta_9eda191ef0():spartaqube_cli.sparta_9eda191ef0()
@app.command()
def sparta_dc0ffa82f6(ip_addr,http_domain):A=spartaqube_cli.token(ip_addr,http_domain);print(A)
@app.command()
def sparta_832baf3aa9():print('Hello world!')
if __name__=='__main__':app()