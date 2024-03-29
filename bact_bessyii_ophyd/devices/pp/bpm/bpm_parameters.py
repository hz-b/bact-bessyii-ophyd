import numpy as np
from . import bpm_config

#: scale raw bpm bits to mm
#: 10 mm equals 2**15
bit_scale = 10/2**15


def create_bpm_config():
    '''Beam position monitor as an array of records

    The calculation from BPM readings to physical data is handled by
    :class:`ophyd.devices.utils.derived_signal.DerivedSignalLinearBPM`

    Returns:
         a structured numpy array

    The returned array contains the following entries:
        * `name`: name of the beam position monitor
        * `x_state`: scale in x axis
        * `y_state`: scale in y axis
        * `ds`:      s position in the ring
        * `x_scale`: scale in x axis
        * `y_scale`: scale in y axis
        * `x_offset`: offset in x axis
        * `y_offset`: offset in y axis

    Todo:
       Discuss how x_scale and y_scale should be handled.

       Rationale: bluesky/ophyd considers the transformation from raw data to
                  physics data as an inverse operation. Thus standard operation
                  would be for the forward operation:

                  ..math::

                       raw_value = scale $\cdot$ physics_value + offset

                  BESSY II standard approach is to use the equation above as
                  a mapping from raw_value to physics_value.
    '''

    t_names = ['name', 'x_state', 'y_state',  's',      'idx']
    formats = ['U20',   np.bool_,  np.bool_,   np.float_, np.int_]
    t_names += ['x_scale', 'y_scale', 'x_offset', 'y_offset']
    formats += [np.float_, np.float_,  np.float_,  np.float_]
    dtypes = np.dtype({'names':  t_names, 'formats': formats})

    n_bpms = len(bpm_config.bpm_conf)
    data = np.zeros((n_bpms,), dtype=dtypes)
    for i in range(n_bpms):
        entry = bpm_config.bpm_conf[i]
        no_offset = (0, 0)
        data[i] = entry + no_offset

    del entry, i, n_bpms

    # The scale factors are stored as multipliers ...
    # The BPM class expects them as deviders
    data['x_scale'] = 1 / data['x_scale']
    data['y_scale'] = 1 / data['y_scale']

    for name in bpm_config.bpm_offset.keys():
        x_offset, y_offset = bpm_config.bpm_offset[name]

        idx = data['name'] == name
        line = data[idx]
        assert(name == line['name'])

        line['x_offset'] = x_offset
        line['y_offset'] = y_offset
        data[idx] = line

    del idx, x_offset, y_offset, line, name
    # deselect deactivated bpms
    valid_bpms = data['x_state'] & data['y_state']
    reduced_bpms = data[valid_bpms]
    del data

    # only valid bpms beyond this point
    assert(sum(reduced_bpms['x_state']) == reduced_bpms.shape[0])
    assert(sum(reduced_bpms['x_state']) == reduced_bpms.shape[0])

    s_sort = np.argsort(reduced_bpms['s'])
    sorted_bpms = np.take(reduced_bpms, s_sort)
    del s_sort
    del reduced_bpms

    # data start counting at one ... need to use count at zero
    # compatible with python
    sorted_bpms['idx'] -= 1
    return sorted_bpms


if __name__ == '__main__':
    n_bpms = 10
    dtypes = np.dtype({
        'names'   : ['name', 'state_x', 'state_y', 'ds',     'idx',    'x_scale',   'y_scale'],
        'formats' : ['U20',   np.bool_,  np.bool_,  np.float_, np.int_,  np.float_,  np.float_]
        }
    )
    data = np.array(n_bpms, dtype=dtypes)

    s_bpm = create_bpm_config()
    idx = s_bpm['idx']
    print('{:d} # names'.format(len(s_bpm['name'])))
    print('{:d} # indices {:d} unique ones'.format(len(idx), len(set(idx))))
    print('{:d} # scale_x'.format(len(s_bpm['x_scale'])))
