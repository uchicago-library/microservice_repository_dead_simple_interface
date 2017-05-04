import logging
import requests
import pathlib

from flask import Blueprint, render_template, request


BLUEPRINT = Blueprint('dead_simple_interface', __name__,
                      template_folder='templates')


BLUEPRINT.config = {}

log = logging.getLogger(__name__)


@BLUEPRINT.route("/", methods=['GET'])
def root():
    return render_template("root.html")


@BLUEPRINT.route("/collectionrecs/", methods=['GET'])
def list_collectionrecs():
    pass


@BLUEPRINT.route("/collectionrecs/mint_collectionrec", methods=['GET', 'POST'])
def mint_collectionrec():
    pass


@BLUEPRINT.route("/collectionrecs/<string:c_id>/", methods=['GET'])
def view_collectionrec():
    pass


@BLUEPRINT.route("/collectionrecs/<string:c_id>/mint_accessionrec", methods=['GET', 'POST'])
def mint_accessionrec():
    pass


@BLUEPRINT.route("/collectionrecs/<string:c_id>/<string:a_id>", methods=['GET'])
def view_accessionrec():
    pass


@BLUEPRINT.route("/accessions/", methods=['GET'])
def accs_listing():
    cursor = request.values.get('cursor', "0")
    resp = requests.get(BLUEPRINT.config['INTERNAL_ACC_IDNEST_URL'],
                        params={'limit': 200, 'cursor': cursor})
    resp.raise_for_status()
    resp_json = resp.json()
    acc_list = [x['identifier'] for x in resp_json['Containers']]
    next_link = None
    next_cursor = resp_json['pagination']['next_cursor']
    if next_cursor:
        next_link = ".?cursor={}".format(next_cursor)
    return render_template("accs_listing.html", acc_list=acc_list, next_link=next_link)


@BLUEPRINT.route("/accessions/<string:acc_id>")
def acc_listing(acc_id, cursor="0"):
    def get_originalName(id):
        try:
            r = requests.get(BLUEPRINT.config['INTERNAL_QREMIS_API_URL']+"object_list/"+id)
            r.raise_for_status()
            rj = r.json()
            hex_originalName = rj['originalName']
            bytes_originalName = bytearray.fromhex(hex_originalName)
            return str(bytes_originalName.decode("utf-8"))
        except Exception as e:
            return str(e)

    def get_downloadName(origName):
        if origName is None:
            return None
        n = pathlib.Path(origName).name
        if n == '':
            return None
        return n

    cursor = request.values.get('cursor', "0")
    resp = requests.get(BLUEPRINT.config['INTERNAL_ACC_IDNEST_URL']+"/{}".format(acc_id),
                        params={'limit': 200, 'cursor': cursor})
    resp.raise_for_status()
    resp_json = resp.json()
    obj_list = [{'identifier': x['identifier'], 'originalName': get_originalName(x['identifier']),
                 'download_name': get_downloadName(get_originalName(x['identifier']))}
                for x in resp_json['Members']]
    next_link = None
    next_cursor = resp_json['pagination']['next_cursor']
    if next_cursor:
        next_link = "./{}".format(acc_id)+"?cursor={}".format(next_cursor)
    return render_template("acc_listing.html", acc_id=acc_id, obj_list=obj_list, next_link=next_link,
                           archstor_url=BLUEPRINT.config['EXTERNAL_ARCHSTOR_URL'],
                           qremis_api_url=BLUEPRINT.config['EXTERNAL_QREMIS_API_URL'])


@BLUEPRINT.record
def handle_configs(setup_state):
    app = setup_state.app
    BLUEPRINT.config.update(app.config)

    if BLUEPRINT.config.get("VERBOSITY"):
        logging.basicConfig(level=BLUEPRINT.config['VERBOSITY'])
    else:
        logging.basicConfig(level="WARN")
