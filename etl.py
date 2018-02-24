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
        dictionary = json.loads('datasets/puntos_limpios_fijos.json')
        print(dictionary)

        # Create a document using the Database API.
        newDocument = myDatabase.create_document(dictionary)

        # Check that the document exists in the database.
        if newDocument.exists():
            print ("Document '{0}' successfully created.".format(number))

    except IOError:
        print("The file does not exist.")
