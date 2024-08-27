import argparse, colorama
from models import Course, Question
import db

def list_courses(args):
    courses = db.read('courses', default=[])
    for course in courses:
        print(f'{colorama.Fore.GREEN}{course["id"]}{colorama.Style.RESET_ALL} - {colorama.Fore.WHITE}{course["name"]}{colorama.Style.RESET_ALL} {colorama.Fore.YELLOW}({len(course["questions"])}){colorama.Style.RESET_ALL}')

def get_questions_from_input():
    questions = []
    while True:
        question = input('Question: ')
        if question == 'done':
            break
        answer = input('Answer: ')
        questions.append({'question': question, 'answer': answer})
    return questions

def add_questions(args):
    courses = db.read('courses', default=[])
    course_raw = next((c for c in courses if c["id"] == args.id), None)
    if not course_raw:
        print(f'Course with ID {args.id} not found')
        return
    course = Course(**course_raw)
    questions = get_questions_from_input()
    for q in questions:
        question = Question(**q)
        course.questions.append(question)
        print(f'Question {question.question} added to course {course.name}')
    
    for i, c in enumerate(courses):
        if c["id"] == course.id:
            courses[i] = course.serialize()

    db.save('courses', courses)

def new_course(args):
    current_courses = db.read('courses', default=[])
    questions = get_questions_from_input()
    course = Course(name=args.name, questions=[Question(**q) for q in questions])
    current_courses.append(course.serialize())
    db.save('courses', current_courses)

def main():
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(description='CLI for managing courses and questions')
    subparsers = parser.add_subparsers(dest='command', help='commands')

    list_parser = subparsers.add_parser('list', help='List all courses') # Lists all courses and N of questions they have
    list_parser.set_defaults(func=list_courses)

    new_parser = subparsers.add_parser('new', help='Create a new course')
    new_parser.add_argument('name', type=str, help='Course name')
    new_parser.set_defaults(func=new_course)

    add_parser = subparsers.add_parser('add', help='Add a question to a course')
    add_parser.add_argument('id', type=str, help='Course ID')
    add_parser.set_defaults(func=add_questions)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return
    
    args.func(args)

if __name__ == '__main__':
    main()