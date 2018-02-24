from flask import Flask, render_template, request, jsonify
import atexit
import cf_deployment_tracker
import os
import json

from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey
from cloudant.query import Query


from bottle import get, run, request, template

# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/')
def home():
    # Top 3 distritos
    myDatabase1 = client.get("act-limp-urb-db", remote=True)
    myDatabase2 = client.get("padron-db", remote=True)
    myDatabase3 = client.get("zonas-verdes-db", remote=True)

    # Tengo que ordenar descendentemente la lista
    query1 = Query(myDatabase1, selector={'_id': {'$gt': 0}}, fields=['DISTRITO','Kg Recogida de muebles','Kg Recogida Residuos Viarios','Ud Reposicin Bolsas Caninas'])
    query2 = Query(myDatabase2, selector={'_id': {'$gt': 0}}, fields=['DISTRITO','POBLACION'])
    query3 = Query(myDatabase3, selector={'_id': {'$gt': 0}}, fields=['DISTRITO','SUPERFICIE/m2'])

    results1 = []
    results2 = []
    results3 = []

    # Iterate over query1
    for each in query1.result:
        result = {}
        result['name'] = each['DISTRITO']
        result['clean_dogs'] = each['Ud Reposicin Bolsas Caninas']
        result['basura_muebles'] = each['Kg Recogida de muebles']
        result['basura_varios'] = each['Kg Recogida Residuos Viarios']
        results1.append(result)

    # Iterate over query2
    for each in query2.result:
        result = {}
        result['name'] = each['DISTRITO']
        result['habs'] = each['POBLACION']
        results2.append(result)

    # Iterate over query3
    for each in query3.result:
        result = {}
        result['name'] = each['DISTRITO']
        result['parks'] = each['SUPERFICIE/m2']
        results3.append(result)

    # Merge lists of dicts which share a common key
    # Credits to https://stackoverflow.com/a/3422287 and https://mmxgroup.net/2012/04/12/merging-python-list-of-dictionaries-based-on-specific-key/
    results = []

    def merge_lists(l1, l2, l3, key):
      merged = {}
      for item in l1+l2+l3:
        if item[key] in merged:
          merged[item[key]].update(item)
        else:
          merged[item[key]] = item
      return [val for (_, val) in merged.items()]

    results = merge_lists(results1, results2, results3, 'name')

    # Compute eco_score
    for each in results:
        each['eco_score'] = 0.5


    # # Compute eco_score
    # result['eco_score'] = 0.5 #(each['Kg Recogida de muebles'] + each['Kg Recogida Residuos Viarios'])/result['habs']

    return template ('templates/index.html', districts=results)

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
