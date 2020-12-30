from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_wtf.csrf import CSRFProtect
from InfiniteCampus import IC_grades
from data import Data, weighted_GPA
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)
csrf = CSRFProtect(app)

userdata = {}


@app.route("/", methods=["GET", "POST"])
def function():
    global userdata
    Invalid_Number = False
    Invalid_User = False

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            # semester_grade_wanted = int(request.form.get("semester_grade_wanted"))
            # q2_grade_wanted = int(request.form.get("q2_grade_wanted"))
            # assignment_pts = int(request.form.get("assignment_pts"))
            grades = IC_grades(username, password)
        except ValueError:
            Invalid_Number = True
        except KeyError:
            Invalid_User = True
        else:
            
            li = []
            for i in range(len(grades[0]["courses"])):
                if (
                    "PHYSICS"
                    not in grades[0]["courses"][i]["gradingTasks"][0]["courseName"] 
                ):
                    if grades[1]["courses"][i]["dropped"] == False:
                        li.append(
                            Data(
                                i,
                                grades,
                            )
                        )
            # for i in range(0, len(li)):
            #     ret.append([])
            #     ret[i].append(li[i].course_name)
            #     try:
            #         ret[i].append(round(li[i].exam_percent_needed(), 3))
            #     except:
            #         ret[i].append(li[i].exam_percent_needed())
            #     ret[i].append(round(li[i].q2_bonus_needed(), 3))
            #     ret[i].append(
            #         round(li[i].q2_assignment_percent_needed(assignment_pts), 3)
            #     )
            #     ret[i].append(li[i].letter_to_gpa())
            # semester_GPA = weighted_GPA(ret)
            # ret.append(round(weighted_GPA(ret), 3))
            User_ID = str(os.urandom(24).hex())
            while userdata.get(User_ID, False):
                User_ID = str(os.urandom(24).hex())
            userdata[User_ID] = li
            resp = make_response(redirect("/results"))
            resp.set_cookie("UserID", User_ID)
            return resp
    return render_template(
        "index.html", Invalid_User=Invalid_User, Invalid_Number=Invalid_Number
    )


@app.route("/results", methods=["GET", "POST"])
def functionn():
    ret = {}
    Invalid_Number = False
    get_form = False
    icourse_name = ''
    try:
        User_ID = request.cookies.get("UserID")
        li = userdata[User_ID]
        for i in range(len(li)):
            ret[li[i].course_name] = []
            ret[li[i].course_name].append(li[i].course_name)
            ret[li[i].course_name].append(li[i])
        gpa = round(weighted_GPA(li),3)
            
    except:
        return redirect(url_for("function", Invalid_User=False, Invalid_Number=False))
    if request.method == "POST":
        try:
            icourse_name = request.form.get("course")
            semester_grade_wanted = int(request.form.get("semester_grade_wanted"))
            q2_grade_wanted = int(request.form.get("q2_grade_wanted"))
            assignment_pts = int(request.form.get("assignment_pts"))
        except ValueError:
            Invalid_Number = True
        else:
            try:
                ret[icourse_name].append(round(ret[icourse_name][1].exam_percent_needed(semester_grade_wanted), 3))
            except:
                ret[icourse_name].append(ret[icourse_name][1].exam_percent_needed(semester_grade_wanted))
            ret[icourse_name].append(round(ret[icourse_name][1].q2_bonus_needed(q2_grade_wanted), 3))
            ret[icourse_name].append(
                round(ret[icourse_name][1].q2_assignment_percent_needed(assignment_pts,q2_grade_wanted), 3)
            )
            ret[icourse_name].append(ret[icourse_name][1].letter_to_gpa())
        get_form = True
    

    return render_template("results.html", len=len(ret) - 1, ret=ret, Invalid_Number=Invalid_Number, get_form = get_form, gpa = gpa, icourse_name=icourse_name)

app.run(debug = True,use_reloader=True, port=5002)
