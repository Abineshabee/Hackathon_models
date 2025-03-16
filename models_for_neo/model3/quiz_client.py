import requests

server_url = "http://127.0.0.1:8000"

# Step 1: Get quiz category from the user
category = input("Enter quiz category (Tech, Math, Physics, Science, Space): ").strip()

# Step 2: Request AI-generated quiz
quiz_response = requests.post(f"{server_url}/generate_quiz", json={"category": category})
quiz_data = quiz_response.json()

if "error" in quiz_data:
    print("Error:", quiz_data["error"])
    exit()

questions = quiz_data["quiz"]
correct_answers = quiz_data["correct_answers"]
student_answers = []

print("\n--- Quiz Start ---\n")

# Step 3: Ask questions to the student
for i, q_data in enumerate(questions):
    print(f"Q{i+1}: {q_data['question']}")
    for option in q_data["options"]:
        print(option)
    
    answer = input("Your Answer (A, B, C, D, E): ").strip().upper()
    student_answers.append(answer)

# Step 4: Send answers for evaluation
print("\nSending answers for evaluation...")

eval_response = requests.post(f"{server_url}/evaluate_quiz", json={"correct_answers": correct_answers, "student_answers": student_answers})
eval_data = eval_response.json()

if "error" in eval_data:
    print("Error:", eval_data["error"])
    exit()

# Step 5: Show Results
print("\n--- Quiz Results ---")
print(f"Score: {eval_data['score']} / {len(questions)}")

for result in eval_data["details"]:
    print(f"Q{result['question']}: Your Answer: {result['student']} | Correct: {result['correct']} | {'✅' if result['score'] == 1 else '❌'}")

# Step 6: Get suggestions based on score
suggestions_response = requests.post(f"{server_url}/suggestions", json={
    "user_score": eval_data['score'], 
    "user_category": category, 
    "questions_len": len(questions)
})

suggestions_data = suggestions_response.json()

print("\n--- Learning Suggestions ---")
print(suggestions_data["links"])

