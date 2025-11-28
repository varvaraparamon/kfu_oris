from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

data = [
    {"title" : "anya", "desc": "очень умная студентка"},
    {"title" : "bulat", "desc": "любит backend"},
    {"title" : "varya", "desc": "это я"}
]

@app.get("/") # творческое задание - главная страница
def index():
    return render_template("index.html")

@app.get("/items")
def items():
    global data
    return render_template("items.html", items=data)

@app.get("/user/<name>")
def users(name):
    global data
    return render_template("user.html", name=name, users=list(item["title"] for item in data))

@app.get("/search")
def search():
    username = request.args.get("username")
    if username:
        return redirect(url_for("users", name=username))
    return render_template("search.html")


if __name__ == '__main__':
    app.run(debug=True)