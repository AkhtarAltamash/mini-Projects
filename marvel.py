from flask import Flask, request, jsonify, render_template
import json
import random

app = Flask(__name__)

# Load the character data from the JSON file
with open('marvel_characters.json', 'r') as file:
    characters = json.load(file)

# Initialize the global state for tracking questions and remaining characters
questions_asked = {}
remaining_characters = characters.copy()

def ask_question(remaining_characters, attribute_key, attribute_value, answer):
    if answer == 'yes':
        remaining_characters = [char for char in remaining_characters if attribute_value in char[attribute_key]]
    elif answer == 'no':
        remaining_characters = [char for char in remaining_characters if attribute_value not in char[attribute_key]]
    elif answer in ["probably yes", "i don't know", "probably no"]:
        pass  # Do not filter characters, just move to the next question

    return remaining_characters

def get_next_question(remaining_characters, questions_asked):
    if not remaining_characters:
        return None, None

    character = random.choice(remaining_characters)
    possible_questions = []
    for key in character:
        if key in ["Character Name", "Actor Name", "Image"]:
            continue
        values = character[key].split(", ")
        for value in values:
            question = (key, value)
            if question not in questions_asked:
                possible_questions.append(question)
    
    if not possible_questions:
        return None, None
    
    return random.choice(possible_questions)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_question', methods=['GET'])
def get_question():
    global remaining_characters, questions_asked
    if not remaining_characters:
        return jsonify({"result": "done"})

    question_key, attribute_value = get_next_question(remaining_characters, questions_asked)
    if question_key is None:
        return jsonify({"result": "done"})
    
    question = f"Does your character's {question_key.lower()} include {attribute_value}?"
    questions_asked[(question_key, attribute_value)] = True
    
    return jsonify({"question": question, "question_key": question_key, "attribute_value": attribute_value})

@app.route('/answer', methods=['POST'])
def answer():
    global remaining_characters, questions_asked
    data = request.json
    answer = data.get('answer')
    question_key = data.get('question_key')
    attribute_value = data.get('attribute_value')

    remaining_characters = ask_question(remaining_characters, question_key, attribute_value, answer)

    if len(remaining_characters) == 1:
        predicted_character = remaining_characters[0]
        return jsonify({"result": "predicted", "character": predicted_character})
    elif len(remaining_characters) > 1:
        return jsonify({"result": "multiple", "characters": remaining_characters})
    else:
        return jsonify({"result": "none"})

@app.route('/reset', methods=['POST'])
def reset():
    global remaining_characters, questions_asked
    remaining_characters = characters.copy()  # Reset to the original list
    questions_asked = {}  # Reset the questions asked
    return jsonify({'result': 'reset'})

if __name__ == '__main__':
    app.run(debug=True)
