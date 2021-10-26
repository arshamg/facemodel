import os
import uuid
import boto3
import glob
import json
import requests

from flask import Flask, request, Response
from PIL import Image, ExifTags

import zipfile


UPLOAD_FOLDER = '/tmp'
USDZ_OUT_BUCKET = 'usdz-output'
IMAGE_UPLOAD_BUCKET = '3dheads-upload'

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():

    zipfile_flask = request.files['file']
    zip_filename = zipfile_flask.filename
    obj_uuid = os.path.splitext(zip_filename)[0]
    zip_filepath = os.path.join(UPLOAD_FOLDER, zip_filename)
    
    # save the zip file
    zipfile_flask.save(zip_filepath)

    unzip_path = os.path.join(UPLOAD_FOLDER, obj_uuid)

    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)

    # unzip
    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(unzip_path)

    # convert to obj+mtl+png to glb
    #TODO add check for if obj file exists
    # obj_filepath = glob.glob(os.path.join(unzip_path, '*.obj'))[0]
    os.system('ls '+unzip_path+'/')
    print(glob.glob(unzip_path+'/*.obj'))
    obj_filepath = glob.glob(unzip_path+'/*.obj')[0]

    glb_filepath = os.path.join(unzip_path, obj_uuid+'.glb')
    os.system('obj2gltf -i ' + obj_filepath + ' -o ' + glb_filepath)

    os.system('ls '+unzip_path+'/')

    usdz_filepath = os.path.join(unzip_path, obj_uuid+'.usdz')
    os.system('usdzconvert -metersPerUnit 10 ' + glb_filepath + ' ' + usdz_filepath)

    # Upload glb to S3 and get s3 pre-signed url
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(glb_filepath, USDZ_OUT_BUCKET, os.path.basename(glb_filepath))

    s3_client = boto3.client('s3', region_name='us-east-2')
    psu_response_glb = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': USDZ_OUT_BUCKET,
                                                        'Key': os.path.basename(glb_filepath)},
                                                ExpiresIn=60*60)

    # Upload usdz to S3 and get usdz pre-signed URL
    s3.meta.client.upload_file(usdz_filepath, USDZ_OUT_BUCKET, os.path.basename(usdz_filepath))

    psu_response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': USDZ_OUT_BUCKET,
                                                        'Key': os.path.basename(usdz_filepath)},
                                                ExpiresIn=60*60)

    
    result = {
        'message': 'conversion was completed',
        'psu': psu_response,
        'psu_glb': psu_response_glb
    }

    return Response(
        response=json.dumps(result),
        status=200,
        mimetype="application/json",
    )

@app.route("/upload", methods=['POST'])
def upload():

    object_key_uuid = str(uuid.uuid4().hex)

    print('The files are: ', request.files)

    image_file = request.files['file']

    original_image_path = os.path.join('/tmp', image_file.filename)
    image_file.save(original_image_path)

    resized_image_path = os.path.join('/tmp', object_key_uuid+'.jpg')

    with Image.open(original_image_path) as image:
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            
            exif = image._getexif()

            if exif[orientation] == 3:
                image=image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image=image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image=image.rotate(90, expand=True)
        except Exception:
            # cases: image don't have getexif
            pass

        image.thumbnail((500,500), Image.ANTIALIAS)
        image.save(resized_image_path, 'JPEG')

    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(resized_image_path, IMAGE_UPLOAD_BUCKET, object_key_uuid+'.jpg')

    s3_client = boto3.client('s3', region_name='us-east-2')
    psu_response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': IMAGE_UPLOAD_BUCKET,
                                                        'Key': object_key_uuid+'.jpg'},
                                                ExpiresIn=60*60)

    inference_json_payload = {
        "images": [psu_response]
    }

    print(inference_json_payload)

    inference_request = requests.post('http://inference:8080/invocations', 
        json=inference_json_payload, 
        headers = {'Content-type': 'application/json'})

    return {
        'statusCode': 200,
        'body': 'success',
        'result': inference_request.json()
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')