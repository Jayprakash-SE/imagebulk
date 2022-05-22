from flask import Flask, render_template, make_response, request, jsonify, \
    redirect, url_for, Response
from tasks import createZip
import os
from celeryWorker import app as celeryApp
from flask_jsonlocale import Locales

app = Flask( __name__ )
app.config["API_URL"] = "https://commons.wikimedia.org/w/api.php"
app.config["MESSAGES_DIR"] = "messages"
app.config["SECRET_KEY"] = os.urandom(24)
locales = Locales(app)
_ = locales.get_message

@app.route('/', methods=[ "GET", "POST"])
def index():
    if request.method == "POST":
        imageList = request.form.get("imageNameList")
        zipFile = createZip.delay( imageList )
        return redirect( url_for("task", id=zipFile.id ) )

    return render_template("index.html")


@app.route('/sendFile/<string:id>')
def sendFile(id):
    # Open and read zip file
    with open(os.path.join('temp', id), 'rb') as f:
        data = f.readlines()
    
    # Returning response with zip file
    return Response(data, headers={
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; filename=data.zip;'
    })


@app.route('/task/<string:id>')
def task(id):
    return render_template("result.html", id=id)

@app.route('/task/status/<string:id>')
def taskStatus(id):
    res = celeryApp.AsyncResult( id )
    if res.state == "SUCCESS":
        return jsonify({
            "status": res.state,
            "result": res.get()
        })

    return jsonify( { "status": res.state } )


@app.route('/changelang', methods=['GET', 'POST'])
def changelang():
    if request.method == "POST":
        locales.set_locale(request.form['locale'])
        return redirect(url_for('index'))

    lcs = locales.get_locales()
    per_lce = locales.get_permanent_locale()
    return render_template('changelanguage.html', locales=lcs, permanent_locale=per_lce)


if '__main__' == __name__:
	app.run()
