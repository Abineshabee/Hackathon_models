import subprocess as sp
import difflib
import re

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

# Function to get suggestions
def get_suggestions(user_score, user_category, questions_len):
    if user_score < questions_len:
        prompt = f"Suggest YouTube video links and website links for the topic: '{user_category}'"
        result = sp.run(['tgpt', '-q', prompt], capture_output=True, text=True)

        if result.returncode == 0:
            return f"Don't worry! Keep practicing and try again!\n{result.stdout.strip()}"
        else:
            return "No links found. Keep practicing!"
    else:
        return "Amazing job! You got a perfect score! Keep it up and keep learning!"

# Main Program
if __name__ == "__main__":
    # Step 1: Get quiz category from the user
    category = input("Enter quiz category (Tech, Math, Physics, Science, Space): ").strip()

    # Step 2: Generate quiz
    questions, correct_answers, error = generate_quiz(category)
    if error:
        print("Error:", error)
        exit()

    student_answers = []

    print("\n--- Quiz Start ---\n")

    # Step 3: Ask questions to the student
    for i, q_data in enumerate(questions):
        print(f"Q{i+1}: {q_data['question']}")
        for option in q_data["options"]:
            print(option)
        
        answer = input("Your Answer (A, B, C, D, E): ").strip().upper()
        student_answers.append(answer)

    # Step 4: Evaluate answers
    print("\nEvaluating answers...\n")
    score, results = evaluate_answers(correct_answers, student_answers)

    print("\n--- Quiz Results ---")
    print(f"Score: {score} / {len(questions)}")

    for result in results:
        print(f"Q{result['question']}: Your Answer: {result['student']} | Correct: {result['correct']} | {'✅' if result['score'] == 1 else '❌'}")

    # Step 5: Get suggestions based on score
    suggestions = get_suggestions(score, category, len(questions))

    print("\n--- Learning Suggestions ---")
    print(suggestions)

