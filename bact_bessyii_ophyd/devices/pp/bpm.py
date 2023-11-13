"""BPM preprocessed data
"""
import numpy as np
import pandas as pd
from bact2.ophyd.devices.process import bpm_parameters

from bact_bessyii_mls_ophyd.devices.process.bpm_packed_data import packed_data_to_named_array
import functools
from ophyd import Component as Cpt, Signal, Kind
from . import bpm_configuration
from .bpmElem import BpmElementList, BpmElemPlane, BpmElem
from ..raw.bpm import BPM as BPMR


def read_orbit_data():
    """
    todo:
        need to retrieve data from a database
        refactor name ... it is rather reading configuration / calibration data for
        the raw orbit data

    Returns:

    How nice if one uses MML. Doing in f77 style is a good excuse for building up technical debt.
    """
    # from pyml import mls_data
    # return mls_data.bpm_offsets()
    # TODO:
    tmp =bpm_parameters.create_bpm_config()
    # TODO: uncommit below two lines once discussed with Pierre
    # retrieved_bpm_list = bpm_configuration.get_bpm_configuration()
    # bpm_config_data_as_data_frame = pd.DataFrame(retrieved_bpm_list.bpmConfigList)
    df = pd.DataFrame(tmp)
    return df
    # return bpm_config_data_as_data_frame


@functools.lru_cache(maxsize=1)
def bpm_config_data():
    """

    Todo:
         Remove it from here please

    flake8 complains about it too
    """
    # BESSY II style
    # bpm_data = mml_bpm_data.reindex(columns=columns + ["offset_x", "offset_y"])
    # ref_orbit = read_orbit_data()
    # ref_orbit = pd.DataFrame()

    import pandas as pd

    return pd.DataFrame(read_orbit_data()).rename(columns={"ds": "s"})

    raise ValueError("remove me please")
    import numpy as np
    from pyml import mlsinit

    columns = [
        "name",
        # x plane
        "read_x",
        "x_active",
        # y plane
        "read_y",
        "y_active",
        # infos
        "family",
        "num",
        "s",
        # index into the vector
        "idx",
        #
        "unknown_a",
        #
        "unknown_b",
        #
    ]


    if False:
        # MLS data
        mml_bpm_data = pd.DataFrame(
            index=columns, data=mlsinit.bpm, dtype=object
        ).T.set_index("name")

        # dead code: flake8 will complain
        # bpm_data = mml_bpm_data.merge(ref_orbit, left_index=True, right_index=True)
        # bpm_data = bpm_data.infer_objects()
        # return bpm_data


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

    #  @Member n_valid_bpms out of n_elements these are only active....
    #  todo: why set this on the model level?
    n_valid_bpms = Cpt(Signal, name="n_valid_bpms", value=-1, kind=Kind.config)
    # n_valid_bpms = Cpt(Signal, name="n_valid_bpms", value=255, kind=Kind.config)

    #  @Member ds: position of the beam position monitor at the longitudinal coordinate
    #  A component is a descriptor representing a device component (or signal)
    ds = Cpt(Signal, name="ds", value=np.nan )  # kind=Kind.config
    #  @Member indices a signal which determines the index .... what is inside indices
    indices = Cpt(Signal, name="indices", value=np.nan, kind=Kind.config)
    names = Cpt(Signal, name="names", value=np.nan, kind=Kind.config)

    #  a constructor for BPM
    #  **kwargs / **args...  passed an unspecified number of arguments to to the constructor.
    #  We should know what are we passing to a constructor, todo don't we?

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.standardConfiguration()

    def stage(self):
        assert(self.n_valid_bpms.get() > 0)
        super().stage()

    # member function standardConfiguration
    #  todo: explain what we should be doing in this function
    def standardConfiguration(self):
        """

        Todo:
            make this hack a transparent access
        """
        #  todo: rec = recievable... or?
        rec = bpm_config_data()
        self.ds.put(rec.s.values)
        indices = rec.idx.values
        #: todo fix number of bpms  for machine and twin
        self.configure(dict(names=rec.loc[:, "name"].values, indices=indices, n_valid_bpms=123))#len(123)))#rec.idx.values)))
        return

    #
    def splitPackedData(self, data_dic):
        """
        @Params: data_dict: data dictionary in a ... format
        this method will split the packed data into ...
        """
        pd = data_dic[self.name + '_packed_data']
        timestamp = pd["timestamp"]
        r = packed_data_to_named_array(pd["value"], n_elements=self.n_elements, indices=self.indices.get())
        d2 = {self.name + "_" + key: dict(value=r[key], timestamp=timestamp) for key, val in r.dtype.descr}
        return d2

    @functools.lru_cache(maxsize=1)
    def dataForDescribe(self):
        return self.splitPackedData(self.read())

    def describe(self):
        data = super().describe()
        signal_name = self.name + "_packed_data"
        bpm_data = {self.name + "_elem_data": BpmElementList().describe_dict()}
        data.update(bpm_data)
        del data[signal_name]
        return data

    def read(self):
        data = super().read()
        bpm_element_list = BpmElementList()
        n_channels = 8
        signal_name = self.name + "_packed_data"
        # get rid of the empty data first before reshaping
        # todo: that's the bessy ii world, perhaps to dispose them already when reading them?
        # todo: ask colleagues to adjust the .NORD parameter?
        # todo: check that only zeros are discarded?
        data_buffer = data[signal_name]['value'][:1024]
        bpm_packed_data_chunks = np.transpose(np.reshape(data_buffer, (n_channels, -1)))
        # only take the bpm's which are valid
        # minus one is significant: indices are still starting from one
        # need to be shifted here
        bpm_packed_data_chunks = bpm_packed_data_chunks[self.indices.get() -1 ]

        # todo: get names and index correct in reading bpm data
        names_to_use = list(self.names.get()) #+ [f'bpmz_added:{cnt}' for cnt in range(14)]
        # ensure that zip does not finish premature
        assert len(names_to_use) == len(bpm_packed_data_chunks)
        # todo: check the order of chunks in packed data. already acheived by sorting the data chunks?
        for chunk, name in zip(bpm_packed_data_chunks, names_to_use):
            # todo: is that the correct order at the machine
            # bpm_elem_plane_x = BpmElemPlane(chunk[0], chunk[1])
            # bpm_elem_plane_y = BpmElemPlane(chunk[2], chunk[3])
            # todo: thats how the twin puts into the packed data
            #       needs to follow the machine
            bpm_elem_plane_x = BpmElemPlane(chunk[0], chunk[6])
            bpm_elem_plane_y = BpmElemPlane(chunk[1], chunk[7])
            bpm_elem = BpmElem(x=bpm_elem_plane_x, y=bpm_elem_plane_y, intensity_z=chunk[2], intensity_s=chunk[3],
                               stat=chunk[4], gain_raw=chunk[5], name=name)
            bpm_element_list.add_bpm_elem(bpm_elem)
        bpm_data = {self.name + "_elem_data": bpm_element_list.to_dict(data['bpm_packed_data']['timestamp'])}
        data.update(BpmElementList().to_json(bpm_data))
        del data[signal_name]
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
    bpm = BPM(prefix + "MDIZ2T5G", name="bpm")
    if not bpm.connected:
        bpm.wait_for_connection()
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
    db = catalog["heavy_local"]
    RE.subscribe(db.v1.insert)
    RE(count([bpm],3))

    # read back from database
    run =db[-1]
    print(run.metadata['stop'])
    data = run.primary.read()
