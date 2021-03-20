import requests
import zipfile
import datetime
import shutil
import os
import time

from celeryWorker import app


@app.task()
def createZip(imageList):
    time.sleep( 15 )
    param = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "titles": '|'.join( imageList.splitlines() ),
        "iiprop": "url"
    }

    # API request to get Commons file's URL
    resp = requests.get(url="https://commons.wikimedia.org/w/api.php", params=param)

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
        return -1


def getUniqueName():
    # Create a unique file name based on time
    currentTime = str(datetime.datetime.now())
    return currentTime.replace(':', '_').replace(' ', '_').replace('-', '_')