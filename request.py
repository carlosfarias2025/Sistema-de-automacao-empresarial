"""
Esse código é responsável por testar a API REST de forma simples e rápida.
Fiz isso pq eu simplesmente não gostava de usar o /docs do FastAPI ou outra ferramente e
também para estudar como funciona o envio de JWT pela rede
"""

import requests
import base64
import json

URL = "http://127.0.0.1:8000"


print("=" * 60)
print("Iniciando sistema de comunição com a API REST")
print("=" * 60)

dados_test = {
    "username":"joao",
    "password":"senha123"
}

def logintest():
    try:
        resposta = requests.post(f"{URL}/login", data=dados_test,timeout=5)
        resposta.raise_for_status()
        print(f"status:{resposta.status_code}")
        print(f"Mensagem:{resposta.text}")

        corpo = resposta.json()
        return corpo["access_token"]
    except requests.exceptions.ConnectionError:
        print("Não foi possível se comunicar com o sevidor")
        exit(1)
    except requests.exceptions.Timeout:
        print("O servidor demorou demais para responder")
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        print(f"Saída do servvidor: {resposta.text}")

def perfiltest():
    print("ola gay")

token = None

def main():
    while True:
        try:
            entrada = int(input("Qual rota você quer acessar?\nNúmero:"))
            if entrada > len(rotas)-1 or entrada < 0:
                print("Error")
                continue
            else:
                name = list(rotas.keys())[entrada]
                token = rotas[name]()
                header, payload, assinatura = token.split(".")
            break
        except ValueError:
            print("por favor digite um número")


rotas = {
        "login": logintest,
        "perfil": perfiltest
}

if __name__ == "__main__":
    for i in range(len(rotas)):
        listofdict = list(rotas.keys())[i]
        print(f"{i} - {listofdict}")
    main()