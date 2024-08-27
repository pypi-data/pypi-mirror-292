import numpy as np
from .ssec_rink_util.util import value_to_index


def simple_cld_mask(rtrvl_temp_3d, model_temp_3d, press_levels, temp_thresh=10.0, top_press=10.0):
    """
    Poor man's cloud clearing algo (Stettner, Santek)
    :param rtrvl_temp_3d:  Retrieval temperature
    :param model_temp_3d:  Model temperature
    :param press_levels:  Pressure levels (vertical coordinate locations)
    :param temp_thresh:  Temperature threshold for cloud mask
    :param top_press:  Pressure level to start working down the atmospheric column
                       (this algo doesn't work well above this level).
    :return: cloud clearing mask, approximate cloud top pressure, cloud top height index
    """

    if rtrvl_temp_3d.shape != model_temp_3d.shape:
        raise ValueError('rtrvl_temp_3d and model_temp_3d must have same shape')

    if rtrvl_temp_3d.shape[0] != press_levels.shape[0]:
        raise ValueError('slowest varying dimension must the the vertical coordinate with length == press_levels.size')

    num_plevs = press_levels.size
    press_diff = np.diff(press_levels)
    _, ylen, xlen = model_temp_3d.shape

    # Find the closest index of top_press
    p_start_idx = value_to_index(press_levels, top_press)
    ascending = True
    if np.all(press_diff > 0):  # ascending
        bot_idx = num_plevs - 1
    elif np.all(press_diff < 0):  # descending
        ascending = False
        bot_idx = 0
    else:
        raise ValueError("press_levels is neither strictly ascending nor descending")

    diff_3d = model_temp_3d - rtrvl_temp_3d
    cldy = np.where(diff_3d >= temp_thresh, 1, 0)

    if ascending:
        cld_mask_2d = np.any(cldy[p_start_idx::, :, :] == 1, axis=0)
        high_cld_pidx = p_start_idx + np.argmax(cldy[p_start_idx::, :, :], axis=0)
    else:
        cld_mask_2d = np.any(cldy[p_start_idx:-1, :, :] == 1, axis=0)
        high_cld_pidx = (num_plevs-1) - (p_start_idx + np.argmax(cldy[(num_plevs-p_start_idx)::-1, :, :], axis=0))

    cld_press = press_levels[high_cld_pidx.flatten()].reshape(ylen, xlen)
    cld_press = np.where(np.invert(cld_mask_2d), press_levels[bot_idx], cld_press)

    return cld_mask_2d, cld_press, high_cld_pidx



