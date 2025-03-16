from flask import Flask, request, jsonify
import subprocess as sp
import difflib
import re

app = Flask(__name__)

# Function to parse AI-generated questions & answers
def parse_quiz(ai_response):
    lines = ai_response.split("\n")
    questions = []
    correct_answers = []
    current_question = None
    options = []

    for line in lines:
        line = line.strip()
        if re.match(r"^\d+\.", line):  # Detects question numbers like "1. What is..."
            if current_question:
                questions.append({"question": current_question, "options": options})
            current_question = line
            options = []
        elif line.startswith("Answer:"):
            correct_answers.append(line.replace("Answer:", "").strip())  # Store full answer
        elif re.match(r"^[A-E]\)", line):  # Detects options like "A) Option1"
            options.append(line)

    if current_question:  # Add last question
        questions.append({"question": current_question, "options": options})

    return questions, correct_answers

# Function to extract the letter (A, B, C, etc.) from the correct answer
def extract_answer_letter(answer):
    match = re.match(r"([A-E])\)", answer)  # Looks for "A)", "B)", etc.
    return match.group(1) if match else answer  # Extract the letter or return full text

# Function to generate quiz using AI
def generate_quiz(category):
    prompt = f"Generate 10 multiple-choice quiz questions on category : ' { category } '. Provide questions with 5 options each. Mention the correct answer as 'Answer:'. Note: WITHOUT WEB SEARCH. With random order "
    
    result = sp.run(['tgpt', '-q', prompt], capture_output=True, text=True)

    if result.returncode != 0:
        return None, None, result.stderr.strip()

    quiz_text = result.stdout.strip()
    questions, correct_answers = parse_quiz(quiz_text)
    return questions, correct_answers, None

# Function to evaluate student answers
def evaluate_answers(correct_answers, student_answers):
    score = 0
    results = []

    for i, (correct, student) in enumerate(zip(correct_answers, student_answers)):
        correct_letter = extract_answer_letter(correct)  # Get letter only
        similarity = difflib.SequenceMatcher(None, correct_letter.lower(), student.lower()).ratio()
        correct_flag = similarity > 0.8  # 80% similarity threshold

        results.append({
            "question": i + 1,
            "correct": correct_letter,
            "student": student,
            "score": 1 if correct_flag else 0
        })
        
        if correct_flag:
            score += 1

    return score, results

@app.route('/generate_quiz', methods=['POST'])
def quiz():
    data = request.json
    category = data.get("category", "").strip()

    if not category:
        return jsonify({"error": "No category provided"}), 400

    questions, correct_answers, error = generate_quiz(category)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"quiz": questions, "correct_answers": correct_answers})

@app.route('/evaluate_quiz', methods=['POST'])
def evaluate():
    data = request.json

    correct_answers = data.get("correct_answers", [])
    student_answers = data.get("student_answers", [])

    if not correct_answers or not student_answers or len(correct_answers) != len(student_answers):
        return jsonify({"error": "Invalid answers provided"}), 400

    score, results = evaluate_answers(correct_answers, student_answers)
    return jsonify({"score": score, "details": results})
    
@app.route('/suggestions', methods=['POST'])
def suggestions():
    user_result = request.json
    user_score = user_result.get("user_score")
    user_category = user_result.get("user_category", "")
    questions_len = user_result.get("questions_len")

    if user_score < questions_len:
        prompt = f"Suggest YouTube video links and website links for the topic: '{user_category}'"
        result = sp.run(['tgpt', '-q', prompt], capture_output=True, text=True)

        if result.returncode == 0:
            suggested_links = result.stdout.strip()
        else:
            suggested_links = "No links found."

        return jsonify({"links": f"Don't worry! Keep practicing and try again!\n{suggested_links}"})
    else:
        return jsonify({"links": "Amazing job! You got a perfect score! Keep it up and keep learning!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

