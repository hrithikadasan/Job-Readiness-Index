from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department TEXT,
    cgpa REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS skills(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    aptitude INTEGER,
    coding INTEGER,
    communication INTEGER,
    projects INTEGER
)
""")

conn.commit()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        department = request.form["department"]
        cgpa = request.form["cgpa"]

        cursor.execute(
            "INSERT INTO students (name, department, cgpa) VALUES (?, ?, ?)",
            (name, department, cgpa)
        )

        conn.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/skills", methods=["GET","POST"])
def skills():

    if request.method == "POST":

        student_id = request.form["student_id"]
        aptitude = int(request.form["aptitude"])
        coding = int(request.form["coding"])
        communication = int(request.form["communication"])
        projects = int(request.form["projects"])

        cursor.execute(
            """INSERT INTO skills
            (student_id, aptitude, coding, communication, projects)
            VALUES (?, ?, ?, ?, ?)""",
            (student_id, aptitude, coding, communication, projects)
        )

        conn.commit()

        return redirect("/result/" + student_id)

    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()

    return render_template("skills.html", students=students)


@app.route("/result/<student_id>")
def result(student_id):

    cursor.execute("""
    SELECT students.name, aptitude, coding, communication, projects
    FROM students
    JOIN skills ON students.id = skills.student_id
    WHERE students.id = ?
    ORDER BY skills.id DESC
    LIMIT 1
    """,(student_id,))

    data = cursor.fetchone()

    name = data[0]
    aptitude = data[1]
    coding = data[2]
    communication = data[3]
    projects = data[4]

    score = (aptitude*0.25) + (coding*0.35) + (communication*0.20) + (projects*0.20)

    if score >= 80:
        status = "Job Ready"
    elif score >= 60:
        status = "Almost Ready"
    else:
        status = "Needs Improvement"

    return render_template(
        "result.html",
        name=name,
        score=round(score,2),
        status=status
    )


@app.route("/dashboard")
def dashboard():

    cursor.execute("""
    SELECT students.id, students.name, aptitude, coding, communication, projects
    FROM students
    JOIN skills ON students.id = skills.student_id
    GROUP BY students.id
    """)

    data = cursor.fetchall()

    results = []

    for row in data:

        student_id = row[0]
        name = row[1]
        aptitude = row[2]
        coding = row[3]
        communication = row[4]
        projects = row[5]

        score = (aptitude*0.25) + (coding*0.35) + (communication*0.20) + (projects*0.20)

        if score >= 80:
            status = "Job Ready"
        elif score >= 60:
            status = "Almost Ready"
        else:
            status = "Needs Improvement"

        results.append((student_id, name, round(score,2), status))

    return render_template("dashboard.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)