from datetime import datetime
from src.calc import Calculator
import src.core
import os
import sys
import random
import requests
import pyjokes

# Get the parent directory of the current file (src folder)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to the sys.path
sys.path.append(parent_dir)

# Now you can import main
import main

# Receber informações do clima.
def get_weather():
    city_name = input("\nHoobler: Enter the name of the city or press ENTER to use current location: ")

    # Usa o sistema WTTR para ver o clima - ?T - Remove cor e faz arte ASCII funcionar e o 0 para mostrar apenas
    # o clima atual
    url = 'https://wttr.in/{}?T&0'.format(city_name)
    try:
        data = requests.get(url)
        T = data.text
    except Exception as e:
        T = f"Error occurred: {e}"
    # Printa o clima e a arte ASCII
    return T

# Conta piadas - TODO: OPÇÃO DE IDIOMAS E PIADAS SEM SER DE T.I.
def tell_joke(): 
    # Usa a biblioteca Pyjokes para gerar piadas de T.I.
    jokes = pyjokes.get_jokes(language="en", category="all") 
    
    # Retorna uma piada aleatoria da lista de piadas criadas acima
    return random.choice(jokes)
    
# Fala a hora
def tell_time():
    # Recebe a data e hora atual
    now = datetime.now()

    # Formata a data de um jeito mais elegante
    date = now.strftime("%A - %B %d, %Y")  # e.g., "Wednesday, August 21, 2024"

    return f"It's {date}."

# Calculadora simples
def calc():
    calcular = Calculator()
    line = input("Hoobler: Digite a conta: ")
    
    try:
        print("Hoobler:", calcular.parse(line))
    except SyntaxError as e:
        print(f'Hoobler: {e.msg}')

    ch = input("Hoobler: Quer usar a calculadora novamente? s/n\n> ")
    if ch.lower() in ('s', 'y'):
        conta = 0
        return calc()
    else: 
        return "Ok."

# Ir pro setup novamente:
def config():
    ch = input("Hoobler: Deseja usar o setup novamente? s/n\n")
    if ch.lower() in ('s', 'y'):
        cfg.values['setup'] = 1
        return main.setup()
    else: 
        return "Ok."
        
# Manual
def help():
    # Printa um textao explicando o app ou abre um arquivo .txt?
    return "Here is what you can do with me:"