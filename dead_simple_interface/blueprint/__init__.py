import logging
import requests
from json import dumps, loads

from flask import Blueprint, abort, render_template


BLUEPRINT = Blueprint('dead_simple_interface', __name__,
                      template_folder='templates')


BLUEPRINT.config = {
}

log = logging.getLogger(__name__)


@BLUEPRINT.route("/", methods=['GET'])
def root(cursor="0"):
    resp = requests.get(BLUEPRINT.config['ACC_IDNEST_URL']+"?cursor={}".format(cursor))
    resp.raise_for_status()
    resp_json = resp.json()
    acc_list = [x['identifier'] for x in resp_json['Containers']]
    next_link = None
    next_cursor = resp_json['pagination']['next_cursor']
    if next_cursor:
        next_link = BLUEPRINT.config['ACC_IDNEST_URL']+"?cursor={}".format(next_cursor)
    return render_template("root.html", acc_list=acc_list, next_link=next_link)


@BLUEPRINT.route("/<string:acc_id>")
def acc_listing(acc_id, cursor="0"):
    resp = requests.get(BLUEPRINT.config['ACC_IDNEST_URL']+"/{}".format(acc_id))
    resp.raise_for_status()
    resp_json = resp.json()
    obj_list = [x['identifier'] for x in resp_json['Members']]
    next_link = None
    next_cursor = resp_json['pagination']['next_cursor']
    if next_cursor:
        next_link = BLUEPRINT.config['ACC_IDNEST_URL']+"/{}".format(acc_id)+"?cursor={}".format(next_cursor)
    return render_template("acc_listing.html", acc_id=acc_id, obj_list=obj_list, next_link=next_link)


@BLUEPRINT.record
def handle_configs(setup_state):
    app = setup_state.app
    BLUEPRINT.config.update(app.config)

    if BLUEPRINT.config.get("VERBOSITY"):
        logging.basicConfig(level=BLUEPRINT.config['VERBOSITY'])
    else:
        logging.basicConfig(level="WARN")
