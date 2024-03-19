from conversion_model import SteererConversionModel, LinearScaling, SteerersConversions
import json
import jsons
import numpy as np


def calculate_offset_slope(limits):
    '''

    Returns:
        offset , slope
    '''
    # The negative current limit corresponds to the maximum negative kick
    # on the beam hence it does not need to be the lower part
    neg_limit = limits['neg_limit_dI']
    pos_limit = limits['pos_limit_dI']
    limits = np.array([pos_limit, neg_limit])
    dI = pos_limit - neg_limit
    # current steps are expected to expand from -1 to 1
    # which is a length of 2.

    dIs = float(dI / 2)
    offset = float(limits.mean())
    # force it to 0 for twin
    offset = 0
    return LinearScaling(slope=dIs, intercept=offset)

def main():

    with open("steerer_current_limits.json") as fp:
        conversions = SteerersConversions(steerers=[SteererConversionModel(name=key.upper(), conversion=calculate_offset_slope(item)) for key, item in json.load(fp).items()])

    tmp = jsons.dump(conversions)

    with open("steerer_conversions.json", "wt") as fp:
        json.dump(tmp, fp, indent="    ")

    print("done")

if __name__ == "__main__":
    main()