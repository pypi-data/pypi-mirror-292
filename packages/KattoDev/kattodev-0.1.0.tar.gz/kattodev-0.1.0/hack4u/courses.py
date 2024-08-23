class Course:

    def __init__(self, name, duration, link):
        self.name = name
        self.duration = duration
        self.link = link

    def __repr__(self):
        return f"{self.name} [{self.duration} horas] ({self.link})"

courses = [
    Course("Introducción a Linux", 15, "https://hack4u.io/cursos/introduccion-a-linux/12539"),
    Course("Personalización de entorno en Linux", 3, "https://hack4u.io/cursos/personalizacion-de-entorno-en-linux/19867"),
    Course("Introducción al Hacking", 53, "https://hack4u.io/cursos/introduccion-al-hacking/15268"),
    Course("Python Ofensivo", 35, "https://hack4u.io/cursos/python-ofensivo/18870")
]

def list_courses():
    for course in courses:
        print(course)

def search_course_by_name(name):
    for course in courses:
        if course.name == name:
            return course

    return None

print(courses)
