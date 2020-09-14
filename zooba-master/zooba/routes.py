from flask import render_template, url_for, redirect, request
from zooba.models import Course, User, load_user
from zooba import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from flask import abort
from zooba.admin_routes import *
from zooba.route_functions import *

#account page
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    try:
        return render_template("account.html", current_user=current_user, Course=Course)
    except:
        abort(404)

#page where users can send friend requests to people
@app.route("/add-friends",methods=['GET', 'POST'])
@login_required
def addFriends():
    try:
        matrix = getSimilarityMatrix(User.query.all()) 
        friends = getNFriends(matrix,current_user,5)
        #do special variations for user with atul and dinesh, creators of the site
        atul, dinesh = load_user(2), load_user(1)
        creatorSim = [0, 0]
        creatorFriend = [True, True]
        current_friends = current_user.friends.values()    
        if current_user != atul and current_user != dinesh:
            creatorSim = [matrix[current_user][atul], matrix[current_user][dinesh]]
            creatorFriend[0] = not 2 in current_friends
            creatorFriend[1] = not 1 in current_friends

        #if they send a friend request
        if request.method == "POST":
            username = request.form.get("username")
            if username == "":
                return redirect(url_for("addFriends"))
            #update search results if they search for someone in the search bar
            if username != None:
                username = username.lower()
                friend_list = [i for i in User.query.all() if i.site_user.lower().startswith(username) or i.name.lower().startswith(username)]
                if list(friend_list) == list(User.query.all()):
                    friend_list = []
                friends = {}
                for friend in friend_list:
                    if not current_user == friend and friend.id not in current_user.friends.values(): #only show people who they are not already friends with
                        friends[friend] = matrix[current_user][friend]
            else:
                #send a friend request
                friend_user = request.form.get("add")[4:]
                friend = User.query.filter_by(site_user=friend_user).first()
                friend_requests = dict(friend.incoming_friend_requests)
                if current_user.id not in friend_requests.values() and not current_user.id == friend.id:
                    friend_requests[len(friend_requests)] = current_user.id
                    friend.incoming_friend_requests = friend_requests
                    db.session.commit()

                return redirect(url_for("addFriends"))
            return render_template("add-friends.html", friends=friends, creatorSim = creatorSim, creatorFriend=creatorFriend, dinesh=dinesh, atul=atul, search=True, current_user=current_user)
        return render_template("add-friends.html", friends=friends, creatorSim=creatorSim, creatorFriend=creatorFriend, dinesh=dinesh, atul=atul, search=False, current_user=current_user)
    except:
        abort(404)

#page to show assignments
@app.route("/assignments")
@login_required
def assignments():
    try:
        course_assignments = current_user.course_assignments
        getTime(course_assignments)
        return render_template("assignments.html", title="Assignment", course_assignments=course_assignments, current_user=current_user)
    except:
        abort(404)

#course page for select course passed in the method
@app.route("/course/<course>", methods=['GET', 'POST'])
@login_required
def course(course):
    try:
        #show all the students currently taking the course 
        course = Course.query.filter_by(name=course).first()
        matrix = getSimilarityMatrix(User.query.all())
        friends = {}
        for student_id in course.students_taking.values():
            student = load_user(student_id)
            if student != current_user:
                friends[student] = matrix[current_user][student]
        
        #if you send a friend request from the list of students currently taking a class
        if request.method == "POST":
            friend_user = request.form.get("add")[4:]
            friend = User.query.filter_by(site_user=friend_user).first()
            friend_requests = dict(friend.incoming_friend_requests)
            if current_user.id not in friend_requests.values() and not current_user.id == friend.id:
                friend_requests[len(friend_requests)] = current_user.id
                friend.incoming_friend_requests = friend_requests
                db.session.commit()
        return render_template('course.html', current_user=current_user, course=course, friends=friends)
    except:
        abort(404)

#default page to get course reccomendations
@app.route("/course-recommendation", methods=['GET', 'POST'])
@login_required
def courseRecommendation():
    try:
        graph = getGraph()
        start = list(graph.keys())[0]
        #redirect to the course reccomendation page for the course user selected
        if request.method == 'POST':
            start = request.form.get('start')
            return redirect(url_for("courseRecommendationPage", favorite=start))
        recommendations = dijkstra(graph, start)
        return redirect(url_for("courseRecommendationPage", favorite=start)) 
    except:
        abort(404)

#shows course reccomendations for the course selected
@app.route("/course-recommendation/<favorite>", methods=['GET', 'POST'])
@login_required
def courseRecommendationPage(favorite):
    try:
        #create a course graph relationship
        #runs dijkstra's shortest path algorithm to determine similar courses - shorter the path, the more similar they are
        graph = getGraph()
        if request.method == 'POST':
            favorite = request.form.get('start')
            return redirect(url_for("courseRecommendationPage", favorite=favorite))
        recommendations = dijkstra(graph, favorite)
        calculateSimilarity(recommendations)
        return render_template("course-recommendation.html", current_user=current_user, start=favorite, courses=Course.query.all(), recommendations=recommendations, Course=Course)
    except:
        abort(404)

#create a demo user for the demo showcasing feature (still need to implement this feature)
@app.route('/demo')
@login_required
def demo():
    user = User.query.all(site_user='demo')
    user.name = 'demo'
    site_pass = 'demo'
    hac_email = ''
    hac_pass = ''
    user.current_courses = {"0": "English IV AP Lit & Lang", "1": "Calculus BC AP", "2": "Biology AP", "3": "Physics C: Mechanics AP", "4": "Environmental Science AP", "5": "Ind Study: Tech Apps I"}
    user.current_gpa = 5.55
    user.past_courses = {"0": "Symphonic Band IV"}
    user.course_assignments = {"English IV AP Lit & Lang": [], "Calculus BC AP": [{"classwork": "FLIP: Limits-Graph, Numer, and Analytically", "category": "Homework", "due_date": "08/24/2030", "grade": null, "total_points": null}, {"classwork": "PC VIDEOS: Limits Intro", "category": "Effort/Participation", "due_date": "08/20/2020", "grade": "5.00", "total_points": "5.00"}], "Biology AP": [], "Physics C: Mechanics AP": [], "Environmental Science AP": [{"classwork": "1.1 Notes Completion (MAX 20 Pts)", "category": "Notes-Homework-Classwork", "due_date": "08/19/2020", "grade": null, "total_points": null}, {"classwork": "1.1 Notes Check (MAX 4 Pts)", "category": "Assessments", "due_date": "08/19/2020", "grade": null, "total_points": null}], "Ind Study: Tech Apps I": []}
    user.course_grades = {"English IV AP Lit & Lang": 97, "Calculus BC AP": 100, "Biology AP": 96, "Physics C: Mechanics AP": 100, "Environmental Science AP": 92, "Ind Study: Tech Apps I": 98}
    all_course_list = list(user.current_courses.values()) + list(user.past_courses.values())
    user.all_courses = arrayToDict(all_course_list)
    user.about_me = 'Hello I am a demo account, use me however you see fit. But please make an actual account if you like the product!'
    user.profile_photo = 'default-profile.jpg'
    user.profile_background = 'default-background.jpg'
    user.instagram = 'mrbeast'
    user.snapchat = 'DemoSnap'
    user.email = 'demo@gmail.com'
    user.friends = {}
    user.incoming_friend_requests = {}
    db.session.commit()
    login_user(user)

    return redirect(url_for('account'))

#page to edit user profile
@app.route("/edit-profile", methods=['GET', 'POST'])
@login_required
def editProfile():
    try:
        pastCourses = Course.query.all()
        for courseName in current_user.current_courses.values():
            course = Course.query.filter_by(name=courseName).first()
            if course:
                pastCourses.remove(course)
        
        #if they update their profile
        if request.method == 'POST':
            #adding any classes to their past classes they have taken
            student_past_courses = []
            for course in pastCourses:
                check = request.form.get(course.name + "--check")
                if check == "on":
                    student_past_courses.append(course.name)
            current_user.past_courses = arrayToDict(student_past_courses)
            all_course_list = list(current_user.current_courses.values()) + list(current_user.past_courses.values())
            current_user.all_courses = arrayToDict(all_course_list)

            #update basic information
            profile = request.files["profile_pic"]
            back = request.files["profile_bac"]

            insta = None if request.form.get("instagram") == "" else request.form.get("instagram")
            snap = None if request.form.get("snapchat") == "" else request.form.get("snapchat")
            email = None if request.form.get("email") == "" else request.form.get("email")
            about = None if request.form.get("about_me") == "" else request.form.get("about_me")
            hac_email = request.form.get("hac_email")
            hac_pass = request.form.get("hac_pass")

            current_user.instagram = insta
            current_user.snapchat = snap
            current_user.email = email
            current_user.about_me = about
            current_user.hac_email = hac_email
            current_user.hac_pass = hac_pass
            
            #change their profile and background images
            if profile.filename != '':
                current_user.profile_photo = save_picture(profile, 198, 198)
            if back.filename != '':
                current_user.profile_background = save_picture(back, 934*4, 350*4)

            db.session.commit()
            return redirect(url_for("account"))
        return render_template("edit-profile.html", current_user=current_user, pastCourses=pastCourses)
    except:
        abort(404)

#page that shows them their gpa and current grades
@app.route("/gpa")
@login_required
def GPA():
    try:
        print(current_user.course_grades)
        return render_template("gpa.html", current_user=current_user, Course=Course)
    except:
        print(current_user.course_grades)
        abort(404)

#home page
@app.route("/",methods=['GET', 'POST'])
def home():
    try:
        return render_template("index.html")
    except:
        abort(404)

#page that shows them their incoming friend requests
@app.route('/incoming', methods=['GET', 'POST'])
@login_required
def incoming():
    try:
        #shows the user the income request's user similarities
        matrix = getSimilarityMatrix(User.query.all())
        incoming = {}
        for friend_id in current_user.incoming_friend_requests.values():
            friend = load_user(friend_id)
            if current_user != friend:
                incoming[friend] = matrix[current_user][friend]

        #if they accept the incoming friend requests, they are added as a friend
        if request.method == 'POST':
            friend_user = request.form.get("add")[4:]
            friend = User.query.filter_by(site_user=friend_user).first()
            user_requests = dict(current_user.incoming_friend_requests)
            user_requests.pop(str(get_key(user_requests, friend.id)))
            current_user.incoming_friend_requests = user_requests
            friend_requests = dict(friend.incoming_friend_requests)
            key = get_key(friend_requests, current_user.id)
            if key != "DNE":
                friend_requests.pop(str(key))
            friend.incoming_friend_requests = friend_requests
            current_user.updateFriends(friend.id)
            db.session.commit()
            
            return redirect(url_for("incoming"))
        return render_template('incoming-friends.html', incoming=incoming, current_user=current_user)
    except:
        abort(404)

#page to login to the site
@app.route("/login", methods=['GET', 'POST'])
def login():
    try:
        if not current_user.is_anonymous:
            return redirect(url_for("account"))
        user_name = request.form.get("username")
        if user_name:
            user_name = user_name.lower()
            user = User.query.filter_by(site_user=user_name).first() #check to see if the hashed password matches to the once in the database
            if user and bcrypt.check_password_hash(user.site_pass, request.form.get("password")):
                login_user(user)
                update_assignments() #updates all their assignment data
                return redirect(url_for("account"))
        return render_template("login.html")
    except:
        abort(404)

#page to logout the site
@app.route("/logout")
def logout():
    try:
        logout_user()
        return redirect(url_for('home'))
    except:
        abort(404)

#handles 404 errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404page.html', title = '404'), 404

#handles 401 errors
@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for("login"))

#page to signup to the site
@app.route("/signup",methods=['GET', 'POST'])
def signup():
    try:
        if not current_user.is_anonymous:
            return redirect(url_for("account"))
        if request.method == 'POST':
            #add user to the database from the given information
            name = request.form.get("name")
            user_name = request.form.get("user_name")
            password =  bcrypt.generate_password_hash(request.form.get("pass_word")).decode('utf-8') #hash the password
            hac_email = request.form.get("hac_email")
            hac_pass = request.form.get("hac_password")
            if User.query.filter_by(site_user=user_name).first():
                return redirect(url_for("signup"))
            user = User(name, user_name.lower(), password, hac_email, hac_pass) 
            db.session.add(user)
            db.session.commit()
            #login user
            login_user(user)
            #redirect to edit profile
            update_assignments() #updates all their assignment data
            return redirect(url_for("editProfile"))
        return render_template("signup.html",site_users = getUsernameList())
    except:
        abort(404)

#page for the user that is selected
@app.route("/user/<username>")
@login_required
def user(username):
    try:
        username = username.lower()
        friend = User.query.filter_by(site_user=username).first()
        matrix = getSimilarityMatrix(User.query.all())
        similarityScore=100
        if friend and current_user != friend:
            similarityScore = matrix[current_user][friend] #see how similar you are to that user
        return render_template("friend-page.html", Course= Course, current_user=current_user, friend=friend, similarityScore=similarityScore)
    except:
        abort(404)

#page to view all your friends
@app.route("/view-friends")
@login_required
def viewFriends():
    try:
        #shows each friend and your similarity to them
        matrix = getSimilarityMatrix(User.query.all())
        friends = {}
        for friend_id in current_user.friends.values():
            friend = load_user(friend_id)
            friends[friend] = matrix[current_user][friend]
        return render_template("view-friends.html",current_user=current_user, friends=friends)
    except:
        abort(404)