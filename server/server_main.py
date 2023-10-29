# save this as app.py
import task
import flask
import common

app = flask.Flask(__name__)

db = common.getDbInstance()

@app.route("/")
def newTask():
    t = task.createNewTask("http://10.9.9.9/dummy/audio.mp3", "dummy audio file / named as audio.mp3")
    db.add(t)
    return f"new task added, id = {t['id']}"

if __name__ == '__main__':
    app.run(port=8820, host="0.0.0.0")