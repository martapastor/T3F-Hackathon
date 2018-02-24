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

    results = {}
    for each in query1.result:
        results['name'] = each['DISTRITO']
        results['clean_dogs'] = each['Ud Reposicin Bolsas Caninas']

    for each in query2.result:
        if (results['name'] == each['DISTRITO']):
            # results['eco_score'] =
            results['habs'] = each['POBLACION']

    # for each in query3.result:
    #     if (results['name'] == each['DISTRITO']):
    #         results['parks'] = None

    return template ('templates/index.html', districts=results)

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
