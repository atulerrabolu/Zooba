import bs4 as bs
import re

#scrapes the html off of home access to get assignment data information such as duedates, grades, etc.
def get_assignments(assignments):
    class_assignments_containers = assignments.find_all(attrs={'class': 'AssignmentClass'})
    class_assignments = {}
    class_grades = {}
    for assignment in class_assignments_containers:
        class_string = clean_string(assignment.find_all(attrs={'class': 'sg-header-heading'})[0].text)
        class_grade = assignment.find_all(attrs={'class': 'sg-header-heading sg-right'})[0].text
        class_grade = class_grade[class_grade.rfind(" ")+1:-1].strip()
        assigns = assignment.find_all(attrs={'class': 'sg-asp-table-data-row'})
        assignment_data = []
        for assign in assigns:
            list = assign.find_all('a')
            for a in list:
                nums = re.findall('[0-9.]+', str(assign.find_all('td')[4]))
                total = re.findall('[0-9.]+', str(assign.find_all('td')[5]))
                assignment_data.append(Assignment(a.attrs['title'], nums, total).assignment_to_dictionary())
        class_grades[class_string] = class_grade
        class_assignments[class_string] = assignment_data
    return class_assignments, class_grades

#clean up the strings scraped because html formatting is messy
def clean_string(class_string):
    class_string = class_string.strip()
    number_chars = re.findall('[0-9]+', class_string)
    last_num = number_chars[len(number_chars)-1]
    class_string = class_string[class_string.rfind(last_num)+2:].strip()
    return class_string

#a clean way to store assignments for each course
class Assignment:
    classwork = ''
    category = ''
    due_date = ''
    grade = ''
    total_points = ''

    #relevant assignment information like assignment name, due data, grade, and the total points of the grade.
    def __init__(self, title_vals, grade, total_points):
        self.classwork, self.category, self.due_date = self.parse_elements(title_vals)
        self.due_date = self.due_date[6:]
        self.grade = None if len(grade) == 0 else "{:.2f}".format(float(grade[0]))
        self.total_points = None if self.grade == None else "{:.2f}".format(float(total_points[0]))

    #scrape the html to get the required data
    def parse_elements(self, title_vals):
        assignment_details = []

        for i in range(3):
            title_vals = title_vals[title_vals.index('\n')+1:]
            assignment_details.append(title_vals[title_vals.index(' ')+1: title_vals.index('\n')])

        return assignment_details[0], assignment_details[1], assignment_details[2]

    #converts the course object into a dictionary representation to more easily store as json in the database
    def assignment_to_dictionary(self):
        assignment = {}
        assignment["classwork"] = self.classwork
        assignment["category"] = self.category
        assignment["due_date"] = self.due_date
        assignment["grade"] = self.grade
        assignment["total_points"] = self.total_points
        return assignment
