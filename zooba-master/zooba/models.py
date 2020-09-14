from zooba import db, login_manager
from flask_login import UserMixin

#helper method to more easily get a user object based of the user id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#user object
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    site_user = db.Column(db.String(255), unique=True, nullable=False)
    site_pass = db.Column(db.String(255), nullable=False)
    hac_email = db.Column(db.String(255), nullable=False)
    hac_pass = db.Column(db.String(255), nullable=False)
    current_gpa = db.Column(db.String(255))
    current_courses = db.Column(db.JSON, nullable=False, default={})
    past_courses = db.Column(db.JSON, nullable=False, default={})
    course_assignments = db.Column(db.JSON, nullable=False, default={})
    course_grades = db.Column(db.JSON, nullable=False, default={}) 
    all_courses = db.Column(db.JSON, nullable=False, default={})
    about_me = db.Column(db.String(255))
    profile_photo = db.Column(db.String(20), nullable=False, default='default-profile.jpg')
    profile_background = db.Column(db.String(20), nullable=False, default='default-background.jpg')
    instagram = db.Column(db.String(255))
    snapchat = db.Column(db.String(255))
    email = db.Column(db.String(255))
    friends = db.Column(db.JSON, nullable=False, default={})
    incoming_friend_requests = db.Column(db.JSON, nullable=False, default={})

    def __init__(self, name, site_user, site_pass, hac_email, hac_pass):
        self.name = name
        self.site_user = site_user
        self.site_pass = site_pass
        self.hac_email = hac_email
        self.hac_pass = hac_pass

    #method to add friends
    def addFriends(self,friend_id):
        new_friends = dict(self.friends)
        new_friends[len(new_friends)] = friend_id
        self.friends = new_friends

    #creates a bidirectional friendship relation    
    def updateFriends(self,friend_id):
        self.addFriends(friend_id)
        friend = load_user(friend_id)
        friend.addFriends(self.id)
        
    def __repr__(self):
        return f"User('{self.name}')"

#course object
class Course(db.Model):
    name = db.Column(db.String,  primary_key=True, unique=True, nullable=False)
    about_course = db.Column(db.String(255), nullable=False)
    preReqs = db.Column(db.JSON, nullable=False)
    relatedCourses = db.Column(db.JSON, nullable=False)
    students_taking = db.Column(db.JSON, nullable=False)

    def __repr__(self):
        return f"Course('{self.name}')"

    def __init__(self, name, preReqs, relatedCourses, about_course, students_taking):
        self.name = name
        self.preReqs = preReqs
        self.relatedCourses = relatedCourses
        self.about_course = about_course
        self.students_taking = students_taking
    
    def setRelated(self, relatedCourses):
        self.relatedCourses = relatedCourses

    def setPreReqs(self, preReqs):
        self.preReqs = preReqs

    def addRelated(self, course, relatedNess):
        new_related = dict(self.relatedCourses)
        new_related[course] = relatedNess
        self.relatedCourses = new_related

    #method to convert the prerequsite classes into a string
    def getPreReqs(self):
        preReqsString = ''
        if len(self.preReqs) == 0:
            return 'None'
        for i in self.preReqs.values():
            preReqsString += i + ', '
        return preReqsString[:-2]

    def getRelated(self):
        return self.relatedCourses
        
    def __str__(self):
        return str(self.name)


