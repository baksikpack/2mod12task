"""
# [x] Добавьте объявления.
# [x] Выполните просмотр объявлений.
# [x] Удалите своё объявление (определять свои объявления необходимо через Cookies).
# [x] Измените свои объявления (определять свои объявления необходимо через Cookies).
# [x] Удалите устаревшие объявления через заданное время (например, 5 минут).
"""

from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, abort
from flask import session
from flask_apscheduler import APScheduler


from ad_store import ad_store

app = Flask(__name__)


# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def check_perms(pk: int):
    username = session.get('username')
    ad = ad_store.read(pk=pk)
    if ad.created_by != username:
        abort(403)


@app.route('/')
def index():
    return render_template("index.html", username=session["username"] if 'username' in session else None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/ad/create', methods=["GET", "POST"])
def ad_create():
    username = session.get("username")
    if not username:
        abort(403)
    if request.method == "GET":
        return render_template("create.html", username=username)
    elif request.method == "POST":
        ad_store.create(author=username, body=request.form['body'])
        return redirect(url_for('ad'))


@app.route('/ad/<int:pk>/edit', methods=["GET", "POST"])
def ad_edit(pk):
    check_perms(pk)
    if request.method == "GET":
        ad = ad_store.read(pk)
        return render_template("edit.html", ad=ad)
    elif request.method == "POST":
        ad_store.update(pk=pk, body=request.form['body'])
        return redirect(url_for('ad'))


@app.route('/ad/<int:pk>/delete')
def ad_delete(pk: int):
    check_perms(pk)
    ad_store.delete(pk)
    return redirect(url_for('ad'))


@app.route('/ad', methods=["GET"])
def ad():
    return render_template("ads.html", ads=ad_store.all())


scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)


@scheduler.task('interval', id='clear_old_ads', seconds=10)
def clear_old_ads():
    clear_task_older_than = 60 * 5  # Старее чем 5-ть минут
    deleted = ad_store.delete_old(clear_task_older_than)
    if deleted:
        print(f"Delete ads: {deleted}")


scheduler.start()

if __name__ == '__main__':
    app.run()
