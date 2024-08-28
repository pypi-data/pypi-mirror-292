from difflib import get_close_matches
import importlib.resources
import src.core
import os
import json
import sys
import random

# Variáveis globais para armazenar configurações
idioma = 'en'  # Valor padrão
interface = 'cli'  # Valor padrão

# Função para criar o arquivo de configuração padrão
def criar_configuracao():
    print("Hoobler: Arquivo de configurações não encontrado.")
    print("Hoobler: Iniciando setup.")
    with open("configs.txt", "w") as f:
        f.write("""# Configurações do HOOBLER
# Defina o idioma: 'pt' para Português, 'en' para Inglês, etc.
idioma=None

# Defina a interface: 'cli' para Linha de Comando, 'gui' para Interface Gráfica
interface=None
""")
    print("Hoobler: Arquivo de configurações criado. Por favor, defina as preferências:\n")
    config()  # Chama a função para atualizar as configurações

# Função para configurar e atualizar o arquivo de configuração
def config():
    configuracoes = {}
    with open('configs.txt', 'r') as f:
        linhas = f.readlines()
        
    alterado = False

    # Solicitar idioma
    idioma_atual = next((linha for linha in linhas if linha.startswith('idioma=')), None)
    if idioma_atual and 'None' in idioma_atual:
        print("Digite 'pt' para definir o idioma em português:")
        print("Type 'en' to set the program in English:")
        idioma = input("> ").strip()
        configuracoes['idioma'] = idioma
        alterado = True
    else:
        configuracoes['idioma'] = idioma_atual.split('=')[1].strip() if idioma_atual else 'None'

    # Solicitar interface
    interface_atual = next((linha for linha in linhas if linha.startswith('interface=')), None)
    if interface_atual and 'None' in interface_atual:
        print("Digite 'cli' para Linha de Comando ou 'gui' para Interface Gráfica:")
        interface = input("> ").strip()
        configuracoes['interface'] = interface
        alterado = True
    else:
        configuracoes['interface'] = interface_atual.split('=')[1].strip() if interface_atual else 'None'
    
    # Atualizar o arquivo com as novas configurações
    if alterado:
        with open('configs.txt', 'w') as f:
            for linha in linhas:
                if linha.startswith('idioma='):
                    f.write(f"idioma={configuracoes['idioma']}\n")
                elif linha.startswith('interface='):
                    f.write(f"interface={configuracoes['interface']}\n")
                else:
                    f.write(linha)
        print("Hoobler: Configurações atualizadas!")

# Função para carregar configurações
def carregar_configuracoes():
    configuracoes = {}
    try:
        with open('configs.txt', 'r') as f:
            linhas = f.readlines()

        for linha in linhas:
            if linha.startswith('idioma='):
                configuracoes['idioma'] = linha.split('=')[1].strip()
            elif linha.startswith('interface='):
                configuracoes['interface'] = linha.split('=')[1].strip()

    except FileNotFoundError:
        print("Hoobler: Arquivo de configurações não encontrado. Usando configurações padrão.")
        configuracoes['idioma'] = 'pt'  # Valor padrão
        configuracoes['interface'] = 'cli'  # Valor padrão

    return configuracoes

# Função para aplicar configurações
def aplicar_configuracoes(configuracoes):
    global idioma
    global interface

    idioma = configuracoes.get('idioma', 'pt')
    interface = configuracoes.get('interface', 'cli')

    if idioma == 'pt':
        print("Idioma definido para Português.")
        # Implemente a lógica para definir o idioma para Português
    elif idioma == 'en':
        print("Language set to English.")
        # Implemente a lógica para definir o idioma para Inglês
    else:
        print("Error.")

    if interface == 'cli':
        print("Interface definida para Linha de Comando.")
        # Implemente a lógica para usar a interface CLI
    elif interface == 'gui':
        print("Interface set to Graphical User Interface.")
        # Implemente a lógica para usar a interface GUI
    else:
        print("Error.")

# Função principal do chat bot
def main():
    # Check if the knowledge base path is valid
    try:
        with importlib.resources.open_text('src', 'knowledge_base.json') as file:
            knowledge_base = json.load(file)
    except FileNotFoundError:
        print("Error loading knowledge base: knowledge_base.json not found.")
        return
    print("\n------- HOOBLER --------\n   by Pedro Ivo, 2024")
    
    # Loop principal
    while True:
        user_input = input('\n> ').strip()

        # Para fechar o programa
        if user_input.lower() in ('quit', 'sair', 'bye', 'tchau', 'adeus', 'goodbye', 'exit'):
            print("Hoobler: See you later!")
            break
        elif user_input.lower() in ('remove question', 'remove entry'):
            question_to_remove = input('Which question would you like to remove? ')
            src.core.remove_question_from_knowledge_base(question_to_remove, knowledge_base)
            continue

        # Procura a melhor resposta
        best_match = src.core.find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

        # Responde
        if best_match:
            answer = src.core.get_answer(user_input, knowledge_base)
            print(f'Hoobler: {answer}')
        else:
            print("Hoobler: I don't know the answer. Can you teach me?")
            new_answer = input("Type the answer or 'skip': ")

            if new_answer.lower() != 'skip':
                src.core.add_or_update_question(knowledge_base, user_input, new_answer)
                src.core.save_knowledge_base('knowledge_base.json', knowledge_base)
                print('Hoobler: Thank you.')

if __name__ == '__main__':
    if not os.path.exists('configs.txt'):
        criar_configuracao()
    else:
        configuracoes = carregar_configuracoes()
        aplicar_configuracoes(configuracoes)
    main()