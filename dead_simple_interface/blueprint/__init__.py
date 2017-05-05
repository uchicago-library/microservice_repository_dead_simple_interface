import logging
import requests
import pathlib
from uuid import uuid4

from flask import Blueprint, render_template, request, make_response, \
    redirect


BLUEPRINT = Blueprint('dead_simple_interface', __name__,
                      template_folder='templates')


BLUEPRINT.config = {}

log = logging.getLogger(__name__)


@BLUEPRINT.route("/", methods=['GET'])
def root():
    return render_template("root.html")


@BLUEPRINT.route("/records/", methods=['GET'])
def list_collectionrecs():
    r = requests.get(BLUEPRINT.config['INTERNAL_RECS_API_URL']+'collections')
    r.raise_for_status()
    rj = r.json()
    coll_list = rj['Collection_Records']
    return render_template("collrec_listing.html", coll_list=coll_list)


@BLUEPRINT.route("/records/mint_collectionrec", methods=['GET', 'POST'])
def mint_collectionrec():
    if request.method == 'POST':
        cid = uuid4().hex
        r = requests.put(BLUEPRINT.config['INTERNAL_RECS_API_URL']+'collections/{}'.format(cid),
                         data={'name': request.values['name'],
                                 'note': request.values['note']})
        r.raise_for_status()
        return redirect("/records/{}".format(cid))

    if request.method == 'GET':
        return render_template("mint_collrec.html")


@BLUEPRINT.route("/records/<string:c_id>/", methods=['GET'])
def view_collectionrec(c_id):
    identifier = c_id
    r = requests.get(BLUEPRINT.config['INTERNAL_RECS_API_URL']+'collections/{}'.format(c_id))
    r.raise_for_status()
    rj = r.json()
    name = rj['name']
    accrec_list = rj['accs']
    coll_note = rj['note']
    return render_template("collrec_view.html", coll_name=name, coll_identifier=identifier,
                           accrec_list=accrec_list, coll_note=coll_note)


@BLUEPRINT.route("/records/<string:c_id>/editNote", methods=['GET', 'POST'])
def edit_collectionrecNote(c_id):
    if request.method == 'POST':
        r = requests.put(BLUEPRINT.config['INTERNAL_RECS_API_URL']+'collections/{}/editNote'.format(c_id),
                         data={'note': request.values['field']})
        r.raise_for_status()
        return redirect("/records/{}/".format(c_id))

    if request.method == 'GET':
        r = requests.get(BLUEPRINT.config['INTERNAL_RECS_API_URL']+'collections/{}'.format(c_id))
        r.raise_for_status()
        rj = r.json()
        curr_value = rj['note']
        return render_template("edit_textarea.html", field_name="Collection Record Note",
                               curr_value=curr_value)


@BLUEPRINT.route("/records/<string:c_id>/editName", methods=['GET', 'POST'])
def edit_collectionrecName(c_id):
    if request.method == 'POST':
        r = requests.put(BLUEPRINT.config['INTERNAL_RECS_API_URL']+'collections/{}/editName'.format(c_id),
                         data={'name': request.values['field']})
        r.raise_for_status()
        return redirect("/records/{}/".format(c_id))

    if request.method == 'GET':
        r = requests.get(BLUEPRINT.config['INTERNAL_RECS_API_URL']+'collections/{}'.format(c_id))
        r.raise_for_status()
        rj = r.json()
        curr_value = rj['name']
        return render_template("edit_text.html", field_name="Collection Name",
                               curr_value=curr_value)


@BLUEPRINT.route("/records/<string:c_id>/mint_accessionrec", methods=['GET', 'POST'])
def mint_accessionrec(c_id):
    if request.method == 'POST':
        return make_response(str(request.values))

    if request.method == 'GET':
        return render_template("mint_accrec.html", c_id=c_id)


@BLUEPRINT.route("/records/<string:c_id>/<string:a_id>/", methods=['GET'])
def view_accessionrec(c_id, a_id):
    note = "This is an accession note"
    linked_acc = "linkedAccessionIdentifier"
    return render_template("accrec_view.html", accrec_id=a_id, accrec_note=note, linked_acc=linked_acc)


@BLUEPRINT.route("/records/<string:c_id>/<string:a_id>/editNote", methods=['GET', 'POST'])
def edit_accessionrecNote(c_id, a_id):
    if request.method == 'POST':
        return make_response(str(request.values))

    if request.method == 'GET':
        return render_template("edit_textarea.html", field_name="Accession Record Note",
                               curr_value="test_curr_value")


@BLUEPRINT.route("/records/<string:c_id>/<string:a_id>/editLinkedAcc", methods=['GET', 'POST'])
def edit_accessionrecLinkedAcc(c_id, a_id):
    if request.method == 'POST':
        return make_response(str(request.values))

    if request.method == 'GET':
        return render_template("edit_text.html", field_name="Linked Accession Identifier",
                               curr_value="test_curr_value")


@BLUEPRINT.route("/records/<string:c_id>/<string:a_id>/editAssociatedIdentifiers", methods=['GET', 'POST'])
def edit_accessionrecAssociatedIds(c_id, a_id):
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
