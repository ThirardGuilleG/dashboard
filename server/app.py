from flask import request, jsonify, render_template, abort, redirect, url_for
from createApp import app
from utils import get_or_create_img, get_number_update
from loguru import logger
from waitress import serve
# import modéle
from database.models import Server, UpdateAssociation


@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('dashboard'))


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    updates = UpdateAssociation.query.filter(UpdateAssociation.done==False).all()
    done_updates = UpdateAssociation.query.filter(UpdateAssociation.done==True).all()
    return render_template('dashboard.html', number_update=len(updates), done_updates=len(done_updates))


@app.post('/servers')
def servers():
    args= request.form
    token = args.get('token')
    logger.info(f"Demande de la liste des serveurs de : {request.remote_addr}")
    goodToken = "5i3#&N4.r`ftp~s/CG:?t7tCq}zE#5g4Xf58m7.t"
    if token == goodToken:
        servers = [(server.name,server.ip) for server in Server.query.all()]
        logger.debug(servers)
        return jsonify(servers)
    abort(403)


@app.get('/server')
def server_view():
    all_servers = Server.query.all()
    servers = [ {'id': server.id, 'name': server.name, 'ip': server.ip, 'version': server.version, 'need_restart': server.rebootrequired,
                'img': get_or_create_img(server.id), 'update':get_number_update(server.id) } for server in all_servers
                ]
    def sort_by_number_update(element):
        if element.get('need_restart') is True:
            return 9999
        if element.get('update') == 'O':
            return 0
        return element.get('update')
    servers.sort(key=sort_by_number_update, reverse=True)
    return render_template('card.html', servers=servers)


@app.get('/test')
def test():
    import subprocess
    completed = subprocess.run(["powershell", "-Command", "mstsc /v:10.33.1.111:3389"], capture_output=True)
    print(completed)
    return "sss"


if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
    # serve(app, host='0.0.0.0', port=5000, threads=8) #WAITRESS!