from flask import Flask, render_template, make_response, request, jsonify, \
    redirect, url_for, Response
import os
import zipfile
import datetime
import requests
import shutil

app = Flask( __name__ )
app.config["API_URL"] = "https://commons.wikimedia.org/w/api.php"


@app.route('/', methods=[ "GET", "POST"])
def index():
    if request.method == "POST":
        imageList = request.form.get("imageNameList")
        zipFile = createZip( imageList )
        return redirect( url_for("sendFile", id=zipFile) )
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


def createZip(imageList):
    param = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": '|'.join( imageList.splitlines() ),
        "iiprop": "url"
    }

    # API request to get Commons file's URL
    resp = requests.get(url=app.config["API_URL"], params=param)

    if resp.status_code == 200:
        d = resp.json()["query"]["pages"]

        # Creating temporary directory
        tempDir = 'temp/' + getUniqueName()
        os.mkdir( tempDir )

        # Download the files
        for i in d.values():
            imageUrl = i["imageinfo"][0]["url"]
            r = requests.get(imageUrl, allow_redirects=True)
            fileName = i["title"].replace("File:", "")
            open( tempDir + "/" + fileName, 'wb').write(r.content)

        # Creating zip file of downloaded files
        zipf = zipfile.ZipFile( tempDir + '.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in os.listdir(tempDir):
            fileZipPath = os.path.join(tempDir, file)
            zipf.write(filename=fileZipPath, arcname=file)
        zipf.close()

        # Remove temporary directory
        shutil.rmtree( tempDir )

        return (tempDir + '.zip').replace("temp/", "")
    else:
        print("Failed request!")


def getUniqueName():
    # Create a unique file name based on time
    currentTime = str(datetime.datetime.now())
    return currentTime.replace(':', '_').replace(' ', '_').replace('-', '_')


if '__main__' == __name__:
	app.run()
