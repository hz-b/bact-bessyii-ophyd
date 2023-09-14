import logging
from typing import Sequence, Hashable
from collections import OrderedDict

import numpy as np
import xarray as xr

# from bact_analysis_bessyii.bba.analysis_model import MeasuredValues, MeasuredItem
from bact_bessyii_ophyd.devices.pp.bpmElem import BpmElem

logger = logging.getLogger("bact-analysis-bessyii")


# def bpm_data_extract_measurement(item):
#        try:
#             x_pos_raw = item["x"]["pos_raw"]
#             x_rms_raw = item["x"]["rms_raw"]
#             y_pos_raw = item["y"]["pos_raw"]
#             y_rms_raw = item["y"]["rms_raw"]
#        except KeyError as ex:
#             logger.error(f"Failed to treat item {item}: {ex}")
#             raise ex
#        return  MeasuredItem(value=x_pos_raw, rms=x_rms_raw), MeasuredItem(value=y_pos_raw, rms=y_rms_raw)


# def extract_bpm_data_to_flat_structure(data_for_one_magnet: Sequence[Sequence[BpmElem]]) -> Sequence[MeasuredValues]:
#     """
#     Todo:
#         return it as numpy array with named columns ... quite close to an xarray then
#     """
#
#     def one_measurement_to_data_model(one_measurement):
#         x = []
#         y = []
#         for one_bpm_data in one_measurement:
#             name = one_bpm_data['name']
#             xtmp, ytmp = extract_data(one_bpm_data)
#             x.append((name, xtmp))
#             y.append((name, ytmp))
#
#         return MeasuredValues(data=OrderedDict(x)), MeasuredValues(data=OrderedDict(y))

    # tmp = [
    #
    #     for one_measurement in data_for_one_magnet.bpm_elem_data.values
    # ]
    # r = [bpm_elem_util.extract_data(one_bpm) for one_bpm in data_for_one_magnet.bpm_elem_data[0]]

    # extract names of the bpm ... take first one as reference
    # todo: make it a separate function
    # get the bpm names from first line
    # bpm_names = np.array(tmp[0].keys())
    # # check that they are the same in each: too paranoic?
    # for c in tmp[1:]:
    #     check = np.array(c.keys())
    #     assert ((bpm_names == check).all())
    #
    # # all good ... make a flat structure
    # return [[items for _, items in one_measurement.items()] for one_measurement in tmp]


def extract_data(item):
    try:
        x_pos_raw = item["x"]["pos_raw"]
        x_rms_raw = item["x"]["rms_raw"]
        y_pos_raw = item["y"]["pos_raw"]
        y_rms_raw = item["y"]["rms_raw"]
    except KeyError as ex:
        logger.error(f"Failed to treat item {item}: {ex}")
        raise ex
    return ([x_pos_raw, x_rms_raw], [y_pos_raw, y_rms_raw])

def bpm_to_dataset(read_data: Sequence[Hashable]) -> xr.DataArray:
    """
    Convert BPM data to an xarray DataArray.

    Parameters:
        read_data (Sequence[Hashable]): List of BPM data dictionaries.

    Returns:
        xr.DataArray: Converted xarray DataArray.

    Raises:
        KeyError: If any required keys are missing in the data dictionaries.
        Exception: If there is an error converting the data to an xarray DataArray.
    """

    d = {item['name']: extract_data(item) for item in read_data}
    data = [item for _, item in d.items()]
    bpm_names = list(d.keys())
    try:
        da = xr.DataArray(data=data, dims=["bpm", "plane", "quality"],
                          coords=[bpm_names, ["x", "y"], ["pos", "rms"]])
    except Exception as ex:
        logger.error(f"Failed to convert dict to xarray: {ex}")
        logger.error(f"Dict was: {d}")
        raise ex
    return da


def rearrange_bpm_data(bpm_elem_data) -> xr.DataArray:
    """extract values from the dictonaries and put time into consistent arrays
    """
    data = bpm_elem_data
    r = [[bpm_to_dataset(data.isel(name=name_idx, step=step_idx).values)
          for step_idx in range(len(data.coords["step"]))]
         for name_idx in range(len(data.coords["name"]))]
    ref_item = r[0][0]
    bpm_names_as_in_model = data.coords["bpm"].values
    dims = ["name", "step"] + list(ref_item.dims)
    shape = (len(data.coords["name"]), len(data.coords["step"])) + ref_item.shape
    da = xr.DataArray(np.empty(shape, dtype=object), dims=dims)
    for name_idx in range(len(data.coords["name"])):
        for step_idx in range(len(data.coords["step"])):
            da[name_idx, step_idx] = r[name_idx][step_idx]
    da = da.assign_coords(dict(
        name=data.coords["name"],
        step=data.coords["step"],
        bpm=ref_item.coords["bpm"],
        plane=ref_item.coords["plane"],
        quality=ref_item.coords["quality"]
    ))
    return da


