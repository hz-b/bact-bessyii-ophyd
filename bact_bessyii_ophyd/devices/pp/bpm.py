"""BPM preprocessed data
"""
import numpy as np
from .bpm_parameters import create_bpm_config

from bact_bessyii_mls_ophyd.devices.process.bpm_packed_data import packed_data_to_named_array
import functools
from ophyd import Component as Cpt, Signal, Kind
from bact_device_models.devices.bpm_elem import BpmElementList, BpmElemPlane, BpmElem
from ..raw.bpm import BPM as BPMR



@functools.lru_cache(maxsize=1)
def bpm_config_data():
    """

    Todo:
         Remove it from here please

    flake8 complains about it too
    """
    import pandas as pd

    tmp = create_bpm_config()
    df = pd.DataFrame(tmp)
    return df

class BPM(BPMR):
    """
    This is the model for a BPM class which specifies a BPM inside a machine.
    A BPM is
    TODO: write a description of the model class in details.
    """

    # List of member attributes for a BPM

    n_elements = 256
    """
        TODO: Provide such a comment to each member attribute of all classes.
        default value of the n_element
        @Member n_elements: this is the number of bpms inside a machine
        todo: rewrite this comment after discussing with Pierre
    """

    #  a constructor for BPM
    #  **kwargs / **args...  passed an unspecified number of arguments to to the constructor.
    #  We should know what are we passing to a constructor, todo don't we?

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self):
        data = super().describe()
        # pack this data into this part
        del data[self.name + "_x_pos"]
        del data[self.name + "_y_pos"]
        del data[self.name + "_x_rms"]
        del data[self.name + "_y_rms"]
        bpm_data = {self.name + "_elem_data": BpmElementList().describe_dict()}
        data.update(bpm_data)
        return data

    def read(self):
        data = super().read()
        bpm_element_list = BpmElementList()
        n_channels = 8

        xp = data[self.name + '_x_pos']['value']
        yp = data[self.name + '_y_pos']['value']
        xr = data[self.name + '_x_rms']['value']
        yr = data[self.name + '_y_rms']['value']
        names = self.cfg.names.get()
        
        for name, xpi, ypi, xri, zri in zip(names, xp, yp, xr, yr):
            if not name:
                continue
            bpm_elem_plane_x = BpmElemPlane(xpi, xri)
            bpm_elem_plane_y = BpmElemPlane(ypi, zri)
            bpm_elem = BpmElem(x=bpm_elem_plane_x, y=bpm_elem_plane_y,
                               intensity_z=7, intensity_s=5,
                               stat=3, gain_raw=1, name=name)
            bpm_element_list.add_bpm_elem(bpm_elem)
        bpm_data = {self.name + "_elem_data": bpm_element_list.to_dict(data['bpm_count']['timestamp'])}
        data.update(BpmElementList().to_json(bpm_data))

        # This data is now in bpm_data
        del data[self.name + "_x_pos"]
        del data[self.name + "_y_pos"]
        del data[self.name + "_x_rms"]
        del data[self.name + "_y_rms"]
        return data


if __name__ == "__main__":
    from bluesky import RunEngine
    from databroker import catalog
    from bluesky.plans import count

    # print("#--------")
    # print(bpm_config_data().dtypes)

    # print(mlsinit.bpm[0])
    # mlsinit.bpm
    # how to combine it with the BPM test of the raw type
    prefix = "Pierre:DT:"
    # bpm = BPM("BPMZ1X003GP", name="bpm")
    bpm = BPM(prefix + "bpm", name="bpm")
    

    if not bpm.connected:
        bpm.wait_for_connection()

    print(bpm.describe_configuration())

    def put_config():
        rec = bpm_config_data()
        # should also go to database
        indices = rec.idx.values
        # that should go away ...
        print(rec.loc[:, ["name", "idx", "s"]])
        print(rec.columns)
        names = np.zeros(128, 'U20')
        names[rec.idx.values] = rec.loc[:, "name"].values
        s_pos = np.zeros(128, float) -1 # np.nan
        s_pos[rec.idx.values] = rec.s.values
        bpm.cfg.configure(dict(names=names, s=s_pos))

    put_config()
    stat = bpm.trigger()
    stat.wait(3)
    data = bpm.read()
    print("# ---- data")
    print(data['bpm_elem_data']['value'])
    print("# ---- end data ")

    # md = dict(
    #     machine="MLS",
    #     nickname="bpm_test",
    #     measurement_target="read bpm data",
    #     target="see if bpm data can be read by RunEngine",
    #     comment="currently only testing if data taking works",
    # )
    # lt = LiveTable(
    #     [
    #         bpm.count.name
    #     ]
    # )
    #initialize RE  and insert into DB using count plan (
    RE = RunEngine({})
    # db = catalog["heavy_local"]
    # RE.subscribe(db.v1.insert)
    RE(count([bpm],3))

    # read back from database
    run =db[-1]
    print(run.metadata['stop'])
    data = run.primary.read()
