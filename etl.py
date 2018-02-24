import csv
import json

from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

#import csvmapper
#from csvmapper import FieldMapper, CSVParser

if __name__ == "__main__":
    client = Cloudant("cf5f9c78-492f-427c-bf8c-b267e321ce1d-bluemix", "2ff4ef832b70e14f6bee3f527aa758a3826441adce95394f95389425592ee2c8", url="https://cf5f9c78-492f-427c-bf8c-b267e321ce1d-bluemix:2ff4ef832b70e14f6bee3f527aa758a3826441adce95394f95389425592ee2c8@cf5f9c78-492f-427c-bf8c-b267e321ce1d-bluemix.cloudant.com")
    client.connect()

    databaseName = "act-limp-urb-db"
    client.delete_database(databaseName)
    myDatabase = client.create_database(databaseName)
    if myDatabase.exists():
        print ("'{0}' successfully created.\n".format(databaseName))

    try:
        # Create documents using the sample data.
        #csvfile = open('datasets/Actuaciones_limpieza_urbana.csv', 'r')
        #jsonfile = open('datasets/Actuaciones_limpieza_urbana.json', 'w')
        #dictionary = json.loads('datasets/convertcsv.json')
        #print(dictionary)

        # Create a document using the Database API.
        #for each in dictionary:
        #        newDocument = myDatabase.create_document(dictionary.keys()[each])

        jsonDocument =  {
            "MES": "DICIEMBRE 2017",
            "LOTE": 6,
            "DISTRITO": "VILLAVERDE",
            "Kg Recogida de muebles": "3427",
            "Kg Recogida Residuos Viarios": "421434",
            "N Servicios Barrido Manual": 946,
            "N Servicios Barrido Mecnico": 5,
            "N Servicios Barrido Mixto": 80,
            "N Servicios Baldeo Mixto": 26,
            "N Servicios Baldeo Mecnico": 45,
            "N Servicios Eliminacin Grafitis": 50,
            "M2 Eliminacin Grafitis": 908,
            "Ud Reposicin Bolsas Caninas": 277589
        }

        # Create a document using the Database API.
        newDocument = myDatabase.create_document(jsonDocument)

        # Check that the document exists in the database.
        if newDocument.exists():
            print ("Document '{0}' successfully created.")

    except IOError:
        print("The file does not exist.")
