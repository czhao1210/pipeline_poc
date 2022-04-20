import os,sys
import threading,time
from multiprocessing import Process
from flask import Flask, request, abort, jsonify, send_from_directory

if(sys.platform == "win32"):
    UPLOAD_DIRECTORY =r"C:\DPG_Automation\\"
else:
    UPLOAD_DIRECTORY = "/opt/APP/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api = Flask(__name__)

@api.route("/list",methods=['GET'])
def list_folders():
    """Endpoint to list files on the server."""
    folders = []
    ff=os.listdir(UPLOAD_DIRECTORY)
    return str(ff)

@api.route("/download/<path:path>")
def get_file(path):
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

@api.route("/shutdown", methods=['GET'])
def shutdown():
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func is None:
        raise RuntimeError('Not running werkzeug')
    shutdown_func()
    return "Stoping Flask Service"

@api.route("/help", methods=['GET'])
def help():
    return "/list  -- To list the files and folders \n/upload/filename -- curl -T C:\git\dtaf_core\src\dtaf_core\drivers\internal\pi_driver.py -X POST 10.215.137.xx/files/ \n/shutdown -- To stop the service \n/download/filename -- To download a file to respective location or streaming it"

@api.route("/upload/<filename>", methods=["POST"])
def post_file(filename):
    """Upload a file."""
    if "/" in filename:
        # Return 400 BAD REQUES
        abort(400, "no subdirectories directories allowed")
    with open(os.path.join(UPLOAD_DIRECTORY, filename), "wb") as fp:
        fp.write(request.data)
    # Return 201 CREATED
    return "", 201

if __name__ == "__main__":
    server = Process(target=api.run(host="0.0.0.0",threaded=True,port=80,debug=True))
    server.terminate()
    server.join()
#curl -T C:\git\dtaf_core\src\dtaf_core\drivers\internal\pi_driver.py -X POST 10.215.137.xx/files/
#