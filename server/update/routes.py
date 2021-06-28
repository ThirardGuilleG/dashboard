from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import json, re

from update.models import Server

updateB = Blueprint("update",__name__, url_prefix="/update")

@updateB.route("/data", methods=["GET","POST"])
def data():
    if request.method == "POST":
        answer = request.get_data(as_text=True).encode('utf-8')
        resp = json.loads(answer.decode())
        if resp:
            for update in resp:
                nameUpdate = update.get('Title')
                server = update.get('PSComputerName')
                maxSize = update.get('MaxDownloadSize')
                url = update.get('SupportUrl')
                reboot = update.get('RebootRequired')
                installed = update.get('IsInstalled')
                date = update.get('LastDeploymentChangeTime')
                print(date[0:15])
                timestamp = int(re.search(r'\d+', date[0:16]).group())
                print(timestamp)
                t = datetime.fromtimestamp(timestamp)
                print(t)
                # Server
                idServer = Server.query.filter_by(name=server).first().id
                print(idServer)
                # Update
            return jsonify("ok", 200)
    return 'None'



@updateB.route("/tables", methods=['GET', 'POST'])
def tables():
    names = ['Serveur', 'Titre', "Taille Max(Mo)", "Reboot", "Description"]
    rows = [["SRVT2WP","Une MAJ intéressante", 125, True,"Un texte beaucoup trop long à lire qui ne sert à rien et qui prend de la place"], 
    ["SRVT2SMTP","Une MAJ intéressante V2", 125, True,"Un texte beaucoup trop long à lire qui ne sert à rien et qui prend de la place V2"],
    ["SRVT2WP","Une MAJ intéressante V3", 130, True,"Un texte beaucoup trop long à lire qui ne sert à rien et qui prend de la place V3"]]
    return render_template('tables.html', title= "Serveur", names=names, rows=rows)


@updateB.route('/<int:idServeur>')
def update(idServeur):
    names = ['Titre', "Taille Max(Mo)", "Reboot", "Description"]
    rows = [["SRVT2WP","Une MAJ intéressante", 125, True,"Un texte beaucoup trop long à lire qui ne sert à rien et qui prend de la place"], 
    ["SRVT2WP","Une MAJ intéressante V2", 125, True,"Un texte beaucoup trop long à lire qui ne sert à rien et qui prend de la place V2"],
    ["SRVT2WP","Une MAJ intéressante V3", 130, True,"Un texte beaucoup trop long à lire qui ne sert à rien et qui prend de la place V3"]]
    return render_template('tables.html', title= "SRVT2WP", names=names, rows=rows)