import argparse, colorama
from models import Course, Question
import db

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
        questions.append({'question': question, 'answer': answer})
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

def new_course(args):
    current_courses = db.read('courses', default=[])
    questions = get_questions_from_input()
    course = Course(name=args.name, questions=questions)
    current_courses.append(course.serialize())
    db.save('courses', current_courses)
    print(f'{colorama.Fore.GREEN}Course {course.name} created. ID: {colorama.Fore.BLUE} {course.id}{colorama.Style.RESET_ALL}')

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