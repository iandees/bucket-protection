import boto3
import botocore
from flask import (
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    request,
    Response,
    url_for,
)
from flask_login import current_user
from . import passthrough_bp


@passthrough_bp.route('/<path:path>')
def passthrough(path):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next=request.path))
    else:
        s3 = boto3.resource('s3')
        bucket = current_app.config.get('S3_BUCKET')
        if path.endswith("/") and current_app.config.get('S3_INDEX_DOCUMENT'):
            path += current_app.config.get('S3_INDEX_DOCUMENT')
        obj = s3.Object(bucket, path)

        try:
            obj_resp = obj.get()

            def generate(result):
                for chunk in iter(lambda: result['Body'].read(8192), b''):
                    yield chunk

            response = Response(generate(obj_resp))
            response.headers['Content-Type'] = obj_resp['ContentType']
            response.headers['Content-Encoding'] = obj_resp['ContentEncoding']
            return response
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                abort(404)
            elif e.response['Error']['Code'] == 'NoSuchKey':
                abort(404)
            else:
                raise
