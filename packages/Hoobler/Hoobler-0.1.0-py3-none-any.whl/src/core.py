from difflib import get_close_matches
import src.functions
import json
import random

# Carrega o arquivo JSON com a base da IA
def load_knowledge_base(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Verifica a estrutura do JSON
            if not isinstance(data, dict) or "questions" not in data:
                raise ValueError("Invalid JSON structure")
            return data
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        print(f"Error loading knowledge base: {e}")
        return {"questions": []}

# Salva o que a IA aprende no arquivo JSON
def save_knowledge_base(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except IOError as e:
        print(f"Error saving knowledge base: {e}")

# Encontra a melhor resposta para o que o usuario escreve
def find_best_match(user_question, questions):
    # Encontra strings que são "parecidas" com uma string alvo, a partir de uma lista 
    # de possibilidades e transforma a lista de perguntas em uma única lista de strings para comparação""" 
    flattened_questions = [q for sublist in questions for q in sublist]
    matches = get_close_matches(user_question.lower(), [q.lower() for q in flattened_questions], n=1, cutoff=0.6)
    return matches[0] if matches else None

# Responde com a melhor resposta encontrada
def get_answer(user_question, knowledge_base):
    for q in knowledge_base["questions"]:
        # Verifica se user_questions coincide com alguma pergunta na lista
        if any(question.lower() in user_question.lower() for question in q["question"]):
            if "function" in q:
                func_name = q["function"]
                func = getattr(src.functions, func_name, None)
                if func:
                    return func()
            return random.choice(q["answer"])
    return "I didn't understand..."

# Adiciona uma nova resposta a uma pergunta existente ou cria uma nova entrada
def add_or_update_question(knowledge_base, user_question, new_answer):
    for q in knowledge_base["questions"]:
        if any(question.lower() == user_question.lower() for question in q["question"]):
        # Verifica se a resposta já existe na lista
            if new_answer not in q["answer"]:
                q["answer"].append(new_answer)
            return
    # Se a pergunta não existir, adiciona uma nova entrada
    knowledge_base["questions"].append({"question": [user_question], "answer": [new_answer]})

# Remove entrada do banco de dados
def remove_question_from_knowledge_base(question: str, knowledge_base: dict):
    for i, q in enumerate(knowledge_base['questions']):
        if q['question'] == question:
            del knowledge_base['questions'][i]
            save_knowledge_base('knowledge_base.json', knowledge_base)
            print("Hoobler: The question-answer pair has been successfully removed.")
            return
    print("Hoobler: Question not found in the knowledge base.")