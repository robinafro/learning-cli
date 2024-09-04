import argparse, colorama, random, json
from models import Course, Question
from difflib import SequenceMatcher
import db
from settings import SIMILARITY_MESSAGES

def collect_all_ids():
    courses = db.read('courses', default=[])
    ids = []
    for course in courses:
        ids.append(course["id"])
        for question in course["questions"]:
            ids.append(question["id"])
    return ids

def autocomplete_id(input_id):
    ids = collect_all_ids()
    similarities = []
    for id in ids:
        match = SequenceMatcher(None, input_id, id).find_longest_match(0, len(input_id), 0, len(id))
        similarities.append((match.size, id))
    similarities.sort(key=lambda x: x[0], reverse=True)
    if len(similarities) == 0 or similarities[0][0] < 3:
        print(f'{colorama.Fore.RED}Couldn\'t find anything that matches "{input_id}"{colorama.Style.RESET_ALL}')
        exit(1)

    return similarities[0][1]

def list_courses(args):
    courses = db.read('courses', default=[])
    for course in courses:
        print(f'{colorama.Fore.GREEN}{course["id"]}{colorama.Style.RESET_ALL} - {colorama.Fore.WHITE}{course["name"]}{colorama.Style.RESET_ALL} {colorama.Fore.YELLOW}({len(course["questions"])}){colorama.Style.RESET_ALL}')
    if len(courses) == 0:
        print(f'{colorama.Fore.LIGHTBLACK_EX}... nothing here yet!{colorama.Style.RESET_ALL}')

def show_course(args):
    courses = db.read('courses', default=[])
    course = next((c for c in courses if c["id"] == args.id), None)
    if not course:
        print(f'{colorama.Fore.RED}Course not found!{colorama.Style.RESET_ALL}')
        return
    course = Course(**course)
    print(f'{colorama.Fore.GREEN}"{course.name}"{colorama.Style.RESET_ALL}')
    for question in course.questions:
        print(f'{colorama.Fore.LIGHTBLACK_EX}{"-"*50}{colorama.Style.RESET_ALL}')
        print(f'{colorama.Fore.YELLOW}Question: {colorama.Style.RESET_ALL}{question.question} {colorama.Fore.LIGHTBLACK_EX}({question.id}){colorama.Style.RESET_ALL}')
        print(f'{colorama.Fore.CYAN}Answer: {colorama.Style.RESET_ALL}{question.answer}')
    if len(course.questions) == 0:
        print(f'{colorama.Fore.LIGHTBLACK_EX}... no questions here yet!{colorama.Style.RESET_ALL}')

def get_questions_from_input():
    questions = []
    while True:
        question = input(f'{colorama.Fore.YELLOW}Question {colorama.Fore.LIGHTBLACK_EX}(type "done" to finish):{colorama.Style.RESET_ALL} ')
        if question == 'done':
            break
        answer = input(f'{colorama.Fore.YELLOW}Answer{colorama.Style.RESET_ALL}: ')
        questions.append({'question': question.strip(), 'answer': answer.strip().lower()})
    return questions

def add_questions(args):
    courses = db.read('courses', default=[])
    course_raw = next((c for c in courses if c["id"] == args.id), None)
    if not course_raw:
        print(f'{colorama.Fore.RED}Course not found!{colorama.Style.RESET_ALL}')
        return
    course = Course(**course_raw)
    questions = get_questions_from_input()
    for q in questions:
        question = Question(**q)
        course.questions.append(question)
        print(f'{colorama.Fore.BLUE}Added question {question.id}{colorama.Style.RESET_ALL}')
    
    for i, c in enumerate(courses):
        if c["id"] == course.id:
            courses[i] = course.serialize()

    db.save('courses', courses)
    print(f'{colorama.Fore.GREEN}{len(questions)} questions added to course {course.id}{colorama.Style.RESET_ALL}')

def new_course_base(args, questions):
    current_courses = db.read('courses', default=[])
    course = Course(name=args.name.strip(), questions=questions)
    current_courses.append(course.serialize())
    db.save('courses', current_courses)
    print(f'{colorama.Fore.GREEN}Course {course.name} created. ID: {colorama.Fore.BLUE} {course.id}{colorama.Style.RESET_ALL}')

def new_course(args):
    questions = get_questions_from_input()
    new_course_base(args, questions)
    
def import_course(args):
    print(f'{colorama.Fore.LIGHTBLACK_EX}{"-"*50}{colorama.Style.RESET_ALL}')
    print(f'{colorama.Fore.CYAN}Please paste a valid JSON of questions for a new course "{args.name}"{colorama.Style.RESET_ALL}')
    print()
    print(f'{colorama.Fore.LIGHTBLACK_EX}The JSON should look as follows:')
    print(f"{colorama.Fore.LIGHTBLACK_EX}[\n\t{{\n\t\t\"question\": \"What is the capital of France?\",\n\t\t\"answer\": \"Paris\"\n\t}},\n\t{{\n\t\t\"question\": \"What is the capital of Germany?\",\n\t\t\"answer\": \"Berlin\"\n\t}}\n]")
    print(f'{colorama.Fore.LIGHTBLACK_EX}{"-" * 50}{colorama.Style.RESET_ALL}')
    questions = input(f'{colorama.Fore.YELLOW}Questions JSON:{colorama.Style.RESET_ALL} ')
    try:
        questions_list = json.loads(questions)
        new_course_base(args, questions_list)
    except Exception as e:
        print(f'{colorama.Fore.RED}Error: {e}{colorama.Style.RESET_ALL}')

def delete(args):
    courses = db.read('courses', default=[])
    for i, course in enumerate(courses):
        if course["id"] == args.id:
            del courses[i]
            db.save('courses', courses)
            print(f'{colorama.Fore.GREEN}{args.id} {colorama.Fore.RED}deleted{colorama.Fore.GREEN} successfully{colorama.Style.RESET_ALL}')
            return

        for j, question in enumerate(course["questions"]):
            if question["id"] == args.id:
                del courses[i]["questions"][j]
                db.save('courses', courses)
                print(f'{colorama.Fore.GREEN}{args.id} {colorama.RED}deleted{colorama.GREEN} successfully{colorama.Style.RESET_ALL}')
                return
    
    print(f'{colorama.Fore.RED}Didn\'t find anything that matches the ID!{colorama.Style.RESET_ALL}')

def log_answer_result(question, property, value):
    # incremental update
    log = db.read('log', default={})
    question_data_all = log.get("question_data", {})
    question_data = question_data_all.get(question.id, {})

    if property not in question_data:
        question_data[property] = 0

    question_data[property] += value

    question_data_all[question.id] = question_data
    log["question_data"] = question_data_all
    db.save('log', log)

def calculate_priority(question_data, penalty_factor=0.2, epsilon=0.01):
    """
    Calculate the priority score for a question based on its score data.

    Parameters:
    question_data (dict): A dictionary containing 'score', 'attempts', and 'skips'.
    penalty_factor (float): The factor by which skips affect the score.
    epsilon (float): A small constant to prevent division by zero.

    Returns:
    float: The priority score of the question.
    """
    score = question_data.get('score', 0)
    attempts = question_data.get('attempts', 0)
    skips = question_data.get('skips', 0)
    
    if attempts == 0:
        # If there are no attempts, give it the highest priority.
        return 1.0

    # Calculate the average score
    avg_score = score / attempts
    
    # Adjust for skips
    adjusted_score = max(avg_score - (skips / attempts * penalty_factor), 0)
    
    # Compute the priority (higher means more priority)
    priority = 1 / (adjusted_score + epsilon)
    return priority

def select_questions_with_priority(question_data, question_count):
    """
    Select questions to ask, repeating them based on their priority.

    Parameters:
    question_data (dict): A dict containing question data. (question id = {score, attempts, skips})
    question_count (int): The total number of questions to ask.

    Returns:
    list: A list of selected question indices.
    """
    # Calculate priorities for each question
    priorities = [(i, calculate_priority(data)) for i, data in question_data.items()]

    # Normalize priorities so they sum to 1
    total_priority = sum(p[1] for p in priorities)
    normalized_priorities = [(i, p / total_priority) for i, p in priorities]

    # Create a weighted list of question indices based on their normalized priorities
    question_pool = []
    for index, normalized_priority in normalized_priorities:
        # Determine how many times this question should appear in the pool
        count = int(round(normalized_priority * question_count))
        question_pool.extend([index] * count)

    # Shuffle the pool to ensure randomness
    random.shuffle(question_pool)

    # Select `question_count` questions, allowing for repeats based on priority
    selected_questions = question_pool[:question_count]

    # If the number of selected questions is less than required (due to rounding), fill in the rest randomly
    while len(selected_questions) < question_count:
        selected_questions.append(random.choice([i for i, _ in priorities]))
        
    return selected_questions

def start_course(args):
    courses = db.read('courses', default=[])
    course_raw = next((c for c in courses if c["id"] == args.id), None)
    if not course_raw:
        print(f'{colorama.Fore.RED}Course not found!{colorama.Style.RESET_ALL}')
        return
    course = Course(**course_raw)

    question_count = args.count if "count" in args and args.count != None else len(course.questions)

    print(f'{colorama.Fore.GREEN}Starting course "{course.name}"{colorama.Style.RESET_ALL}')
    print(f'{colorama.Fore.LIGHTBLACK_EX}{"-"*50}{colorama.Style.RESET_ALL}')

    question_data = db.read('log', default={}).get("question_data", {})
    for q in course.questions:
        if q.id not in question_data:
            question_data[q.id] = {}
    selected_questions_ids = select_questions_with_priority(question_data, question_count)
    selected_questions = []
    for i in selected_questions_ids:
        for q in course.questions:
            if q.id == i:
                selected_questions.append(q)
                break
    
    similarities = []
    for question in selected_questions:
        print(f'{colorama.Fore.YELLOW}{question.question}{"?" if not question.question.endswith("?") else ""}{colorama.Style.RESET_ALL}')
        user_answer = input(f'{colorama.Fore.CYAN}Your answer{colorama.Fore.LIGHTBLACK_EX} (press enter to reveal): {colorama.Style.RESET_ALL}').strip().lower()
        if len(user_answer) == 0:
            print(f'{colorama.Fore.LIGHTBLACK_EX}Answer was: {colorama.Fore.GREEN}{question.answer}{colorama.Style.RESET_ALL}')

            log_answer_result(question, "skips", 1)
        else:
            similarity = SequenceMatcher(None, user_answer, question.answer).ratio()
            for key, message in SIMILARITY_MESSAGES.items():
                if key[0] <= similarity <= key[1]:
                    print(message.replace('$answer', question.answer))
                    break
            similarities.append(similarity)
            log_answer_result(question, "score", similarity)
        log_answer_result(question, "attempts", 1)

        print(f'{colorama.Fore.LIGHTBLACK_EX}{"-"*50}{colorama.Style.RESET_ALL}')

    score = sum(similarities) / len(similarities) if len(similarities) > 0 else 0

    print(f'{colorama.Fore.CYAN}That\'s it! You\'ve finished the course!{colorama.Style.RESET_ALL}')
    print()
    print(f'{colorama.Fore.YELLOW}Your score: {colorama.Fore.GREEN}{score*100:.2f}%{colorama.Style.RESET_ALL}')

def main():
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(description='CLI for managing courses and questions')
    subparsers = parser.add_subparsers(dest='command', help='commands')

    list_parser = subparsers.add_parser('list', help='List all courses')
    list_parser.set_defaults(func=list_courses)

    info_parser = subparsers.add_parser('info', help='Show course info')
    info_parser.add_argument('id', type=str, help='Course ID')
    info_parser.set_defaults(func=show_course)

    delete_parser = subparsers.add_parser('delete', help='Delete a course or question')
    delete_parser.add_argument('id', type=str, help='Course or Question ID')
    delete_parser.set_defaults(func=delete)

    new_parser = subparsers.add_parser('new', help='Create a new course')
    new_parser.add_argument('name', type=str, help='Course name')
    new_parser.set_defaults(func=new_course)

    import_parser = subparsers.add_parser('import', help='Import questions from a JSON into a new course')
    import_parser.add_argument('name', type=str, help='Course name')
    import_parser.set_defaults(func=import_course)

    add_parser = subparsers.add_parser('add', help='Add a question to a course')
    add_parser.add_argument('id', type=str, help='Course ID')
    add_parser.set_defaults(func=add_questions)

    start_parser = subparsers.add_parser('start', help='Start a course')
    start_parser.add_argument('id', type=str, help='Course ID')
    # optional: question count
    start_parser.add_argument('-c', '--count', type=int, help='Number of questions to ask')
    start_parser.set_defaults(func=start_course)

    args = parser.parse_args()

    if 'id' in args:
        args.id = autocomplete_id(args.id)

    if not args.command:
        parser.print_help()
        return
    
    args.func(args)

if __name__ == '__main__':
    main()