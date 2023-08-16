import json
from dataclasses import dataclass, asdict

import jsons
from pymongo import MongoClient

# Import MongoClient and establish a connection to MongoDB
client = MongoClient()
db = client['bessyii']
collection = db['calib.factor']

@dataclass
class CalibrationFactor:
    Family: dict
    t_f: dict
    I_s: dict
    alpha: dict
    beta: dict
    delta: dict
    l_mech: dict
    l_eff: dict

def read_calib_factor_from_json_insert_into_db(file_path):
    # Read the data from the JSON file
    with open(file_path, 'r') as json_file:
        calib_data = json.load(json_file)

    # Create an instance of CalibrationFactor
    calib_factor = CalibrationFactor(
        Family=calib_data['Family'],
        t_f=calib_data['t_f'],
        I_s=calib_data['I_s'],
        alpha=calib_data['alpha'],
        beta=calib_data['beta'],
        delta=calib_data['delta'],
        l_mech=calib_data['l_mech'],
        l_eff=calib_data['l_eff']
    )

    # Insert the data into the MongoDB collection
    collection.insert_one(asdict(calib_factor))

def read_calib_factor_from_database():
    # Retrieve the document from the MongoDB collection
    document = collection.find_one()

    # Reconstruct the CalibrationFactor object using the document
    calib_factor_dict = dict(document)
    calib_factor = CalibrationFactor(
        Family=calib_factor_dict['Family'],
        t_f=calib_factor_dict['t_f'],
        I_s=calib_factor_dict['I_s'],
        alpha=calib_factor_dict['alpha'],
        beta=calib_factor_dict['beta'],
        delta=calib_factor_dict['delta'],
        l_mech=calib_factor_dict['l_mech'],
        l_eff=calib_factor_dict['l_eff']
    )

    return calib_factor

# Close the MongoDB connection
# client.close()

if __name__ == '__main__':
    # # Read from database
    # retrieved_bpm_list = get_bpm_configuration()
    #
    # # Print the retrieved BpmConfigList object
    # print(retrieved_bpm_list)
    # Read from file and insert into database
    read_calib_factor_from_json_insert_into_db('calibration_data.json')
