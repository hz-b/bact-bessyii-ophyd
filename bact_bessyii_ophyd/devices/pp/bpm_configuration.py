from dataclasses import dataclass, asdict
from pymongo import MongoClient
import pandas as pd

# Import MongoClient and establish a connection to MongoDB
client = MongoClient()
db = client['bessyii']
collection = db['bpm.config']

@dataclass
class BpmConfigList:
    bpmConfigList: list

@dataclass
class BpmConfig:
    name: str
    x_state: bool
    y_state: bool
    ds: float
    idx: int
    x_scale: float
    y_scale: float
    x_offset: float
    y_offset: float


def get_offset_values(name):
    # Read the second file containing offset values
    offset_data = pd.read_csv('offset_data.txt', delimiter=',', header=None,
                              names=['name', 'x_offset', 'y_offset'], skipinitialspace=True, index_col=False, dtype=str)

    # Find the offset values for the given bpm_name
    offset_row = offset_data[offset_data['name'] == name]
    if not offset_row.empty:
        x_offset = float(offset_row['x_offset'].values[0])
        y_offset = float(offset_row['y_offset'].values[0])
        return x_offset, y_offset

    # Return default offset values if not found
    return 0.0, 0.0
def read_from_file_insert_in_database(file_path):
    # Read the data from the file into a pandas DataFrame
    # Read the data from the file into a pandas DataFrame
    data = pd.read_csv(file_path, delimiter=',', header=None,
                       names=['name', 'x_state', 'y_state', 'ds', 'idx', 'x_scale', 'y_scale'], skipinitialspace=True,
                       index_col=False, dtype=str)

    # Create an instance of BpmConfigList
    bpm_list = BpmConfigList([])

    # Convert DataFrame rows to BpmConfig dictionaries and add them to the list
    for row in data.itertuples(index=False):
        bpm_dict = dict(row._asdict())

        # Convert x_state and y_state to boolean
        bpm_dict['x_state'] = bool(int(bpm_dict['x_state']))
        bpm_dict['y_state'] = bool(int(bpm_dict['y_state']))
        # Convert ds, idx, x_scale, and y_scale to appropriate data types
        bpm_dict['ds'] = float(bpm_dict['ds'])
        bpm_dict['idx'] = int(bpm_dict['idx'])
        bpm_dict['x_scale'] = float(bpm_dict['x_scale'])
        bpm_dict['y_scale'] = float(bpm_dict['y_scale'])
        # Add BPMZ offset values from second file
        bpm_dict['x_offset'], bpm_dict['y_offset'] = get_offset_values(bpm_dict['name'])

        bpm_config = BpmConfig(**bpm_dict)
        bpm_list.bpmConfigList.append(asdict(bpm_config))

    #INFO: if offset is not going to be joined than below code until ----------------------
    # data = pd.read_csv(file_path, delimiter=',', header=None, names=['name', 'x_state', 'y_state', 'ds', 'idx', 'x_scale', 'y_scale'], skipinitialspace=True, index_col=False, dtype=str)
    #
    # # Create an instance of BpmConfigList
    # bpm_list = BpmConfigList([])
    #
    # # Convert DataFrame rows to BpmConfig dictionaries and add them to the list
    # for row in data.itertuples(index=False):
    #     bpm_dict = dict(row._asdict())
    #     bpm_config = BpmConfig(**bpm_dict)
    #     bpm_list.bpmConfigList.append(asdict(bpm_config))
    # ------------------------------------------------
    # Insert the data into the MongoDB collection
    collection.insert_one(asdict(bpm_list))


def get_bpm_configuration():
    # Retrieve the document from the MongoDB collection
    document = collection.find_one()

    # Reconstruct the BpmConfigList object using the document
    bpm_list_dict = dict(document)
    bpm_list = BpmConfigList(bpmConfigList=bpm_list_dict['bpmConfigList'])

    # Reconstruct the BpmConfig objects inside the list
    bpm_list.bpmConfigList = [BpmConfig(**bpm_dict) for bpm_dict in bpm_list.bpmConfigList]

    return bpm_list

# Close the MongoDB connection
# client.close()


if __name__ == '__main__':
    # # Read from database
    # retrieved_bpm_list = get_bpm_configuration()
    #
    # # Print the retrieved BpmConfigList object
    # print(retrieved_bpm_list)
    # Read from file and insert into database
    read_from_file_insert_in_database('configuration_data.txt')
