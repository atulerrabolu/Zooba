from flask import render_template, url_for, redirect, request
from flask_login import current_user, login_required
from zooba.models import Course
from zooba import app, db
from zooba.route_functions import arrayToDict, get_key

#page on the site to add new classes to the courses database
@app.route("/adder", methods=['GET', 'POST'])
@login_required
def adder():
    #making sure only admins can access this page
    if current_user.id > 2:
        abort(404)

    courses = Course.query.all()

    #checks to see if new course was added    
    if request.method == 'POST': 
        relatedCourses = {}
        for c in courses:
            num = request.form.get(str(c) + "--num")
            if num != None:
                relatedCourses[str(c)] = int(num) #creates a relation for any related classes

        #add prerequiste course information
        preReqs = {}
        count = 0
        for i in range(len(courses)):
            check = request.form.get(str(courses[i]) + "--check")
            if check == "on":
                preReqs[count] = str(courses[i])
                count += 1
        
        newClass = Course(name=request.form.get("course"), preReqs=preReqs, relatedCourses=relatedCourses, about_course = request.form.get("about"), students_taking={})

        #creates a bidrectional relationship with related classes
        courseNames = [str(c) for c in courses]
        if not str(newClass) in courseNames:
            for c in courses:
                c.addRelated(str(newClass), relatedCourses[str(c)])
            
            db.session.add(newClass)
            db.session.commit()
            

    courses = Course.query.all()
    return render_template('adder.html',title="Course Adder", courses=courses)
    
#page on the site to delete any courses
@app.route("/deleter", methods=['GET', 'POST'])
@login_required
def deleter():
    #make sure only admins can access this page
    if current_user.id > 2:
        abort(404)

    courses = Course.query.all()
    
    if request.method == 'POST':
        #gets the course that will be deleted
        courseName = None
        for c in courses:
            if request.form.get(str(c) + "--radio") == "on":
                courseName = str(c)
                Course.query.filter_by(name=courseName).delete()
                db.session.commit()
                break
                
        #remove any relations from other courses to the course that was just deleted        
        courses = Course.query.all()
        for c in courses:
            preReqs = dict(c.preReqs)
            relatedCourses = dict(c.relatedCourses)
            if courseName in preReqs.values():
                preReqs.pop(get_key(preReqs,courseName))
            if courseName in relatedCourses:
                relatedCourses.pop(courseName)

            course = Course.query.filter_by(name=str(c)).first() 
            course.preReqs = arrayToDict(preReqs.values())
            course.relatedCourses = relatedCourses
            db.session.commit()   
        
    courses = Course.query.all()
    return render_template('deleter.html',title="Course Deleter", courses=courses)

#page on the site to allow us to a course to update
@app.route("/editor", methods=['GET', 'POST'])
@login_required
def editor():
    #make sure only admins can access this page
    if current_user.id > 2:
        abort(404)
        
    courses = Course.query.all()
    
    #gets the course to be edited
    if request.method == 'POST':
        for course in courses:
            if str(course) == request.form.get("courses"):
                return redirect(url_for("editing", courseN=course))
        
    return render_template('editor.html',title="Course Editor", courses=courses)

#edit page for to update a course in the database
@app.route("/editor/<courseN>", methods=['GET', 'POST'])
@login_required
def editing(courseN):
    #making sure only admins can access this page
    if current_user.id > 2:
        abort(404)

    #checks to see if new course was updated        
    courses = Course.query.all()
    course = Course.query.filter_by(name=courseN).first()
    if request.method == 'POST':
        relatedCourses = {}
        for c in courses:
            courseName = str(c)
            num = request.form.get(courseName + "--num")
            if num != None and num != "0":
                relatedCourses[courseName] = int(num)  #creates a relation for any related classes
        
        #add prerequiste course information
        preReqs = {}
        for i in range(len(courses)):
            courseName = str(courses[i]) 
            check = request.form.get(courseName + "--check")
            if check == "on":
                preReqs[len(preReqs)] = courseName

        course.preReqs = preReqs
        course.relatedCourses = relatedCourses
        course.about_course = request.form.get("about")
        courseNames = [str(c) for c in courses]
        courseNames.remove(courseN)
        for cN in courseNames:
            Course.query.filter_by(name=cN).first().addRelated(courseN, relatedCourses[cN]) #creates a bidrectional relationship with related classes
        db.session.commit()
        return redirect(url_for("adder"))
        
    courses = Course.query.all()
    return render_template("editing.html", title="Course Editing", courses=Course.query.all(), course=course)