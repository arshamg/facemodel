import base64
import io
import json
import logging
import logging.config
import os
import requests
import shutil
import uuid
import boto3
from zipfile import ZipFile

from flask import Flask, request, Response, jsonify
from functools import lru_cache
from PIL import Image
from urllib.parse import urlparse

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# gunicorn_error_logger = logging.getLogger('gunicorn.error')
# app.logger.handlers.extend(gunicorn_error_logger.handlers)
# app.logger.setLevel(logging.DEBUG)

PREFIX_PATH = "/opt/ml/"
IMAGES_FOLDER = os.path.join(PREFIX_PATH, "images")
INFERENCE_OUT_BUCKET = 'face3d-inference-out'
CONVERSION_URL = 'http://conversion:5000/convert'

def download_image(request_id, image):
    def download_file_from_url(folder, url):
        filebase,extension = os.path.splitext(urlparse(url).path)
        filebase = filebase.split('/')[1]

        filename = os.path.join(folder, os.path.basename(urlparse(url).path))

        print('extension: ', extension)
        if extension == 'jpeg':
            filename += '.jpg'

        try:
            response = requests.get(url)
            with open(filename, "wb") as f:
                f.write(response.content)

            return filebase, filename
        except Exception:
            return None, None

    logging.info(f'Downloading image "{image}"...')

    folder = os.path.join(IMAGES_FOLDER, request_id)
    os.makedirs(folder, exist_ok=True)
    os.makedirs(IMAGES_FOLDER, exist_ok=True)

    fragments = urlparse(image, allow_fragments=False)
    if fragments.scheme in ("http", "https"):
        filebase, filename = download_file_from_url(folder, image)
    else:
        filename = image

    if filename is None:
        raise Exception(f"There was an error downloading image {image}")

    os.system('ls -R /opt/ml/images/' )

    # return filebase, Image.open(filename).convert("RGB")
    return filebase, None


def delete_images(request_id):
    directory = os.path.join(IMAGES_FOLDER, request_id)

    try:
        shutil.rmtree(directory)
    except OSError as e:
        logging.error(f"Error deleting image directory {directory}.")



@app.route("/ping", methods=["GET"])
def ping():
    """This endpoint determines whether the container is working and healthy."""
    logging.info("Ping received...")

    health = Predictor.load() is not None

    status = 200 if health else 404
    return Response(response="\n", status=status, mimetype="application/json")


@app.route("/invocations", methods=["POST"])
def invoke():
    if request.content_type != "application/json":
        return Response(
            response='{"reason" : "Request should be application/json"}',
            status=400,
            mimetype="application/json",
        )

    # Predictor.load()

    request_id = uuid.uuid4().hex

    data = request.get_json()

    images = []
    for im in data["images"]:
        fragments = urlparse(im, allow_fragments=False)
        if fragments.scheme in ("http", "https", "file"):
            filebase, image = download_image(request_id, im)
        else:
            image = Image.open(io.BytesIO(base64.b64decode(im)))

        images.append(image)

    image_request_folder = os.path.join(IMAGES_FOLDER, request_id)
    
    print('^'*20)
    os.system('ls -R '+image_request_folder)
    results_path = os.path.join('/opt/ml/results', request_id)
    os.system('python3 DECA/demos/demo_reconstruct.py -i ' + image_request_folder + ' --savefolder ' + results_path + ' --saveDepth True --saveObj True --useTex False')

    zip_filename = request_id+'.zip'
    zipObj = ZipFile(zip_filename, 'w')

    obj_path = os.path.join(results_path, filebase, filebase+'.obj')
    zipObj.write( obj_path, filebase+'.obj' )

    mtl_path = os.path.join(results_path, filebase, filebase+'.mtl')
    zipObj.write( mtl_path, filebase+'.mtl' )

    png_path = os.path.join(results_path, filebase, filebase+'.png')
    zipObj.write( png_path, filebase+'.png' )
    zipObj.close()

    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(zip_filename, INFERENCE_OUT_BUCKET, zip_filename)

    #TODO clean up the files / delete them

    s3_client = boto3.client('s3')
    psu_response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': INFERENCE_OUT_BUCKET,
                                                        'Key': zip_filename},
                                                ExpiresIn=60*60)
    print('PSU response: ', psu_response)

    files = {'file': open(zip_filename,'rb')}
    conversion_response = requests.post(CONVERSION_URL, files=files)

    print(conversion_response)
    print(conversion_response.json())

    result = {
        'message': 'it was done',
        'artifact': zip_filename,
        'psu': conversion_response.json()
        # 'conv_response': conversion_response
    }

    return Response(
        response=json.dumps(result),
        status=200,
        mimetype="application/json",
    )
