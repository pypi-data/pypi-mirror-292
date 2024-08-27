from opticalflowleo.polar_RAFT_runner import run_multi, run_single
from opticalflowleo.polar_RAFT_runner import cris_product_str, atms_mirs_product_str, metop_avhrr_product_str

mode = 'multi'  # 'multi' or 'single'

if mode == 'multi':

    """
    Computes winds from a set of overlapping pairs of granules through multiple pressure levels.
    (See global parameters at top of this module)
    :param path_to_first: directory containing files of first orbit platform to cross equator.
    :param path_to_second: directory containing files for the second platform
    :param product_str: name of product to work on.
    :param do_plots: output to animated gif.
    :param do_write: output to CF-compliant NetCDF4 file.
    :param press_low: low pressure (hPa). Default value is 800mb
    :param press_high: high pressure (hPa). Default value is 100mb
    :param press_skip: number of pressure levels to skip. Default value is 4
    :param wind_plot_skip: skip factor for wind vectors in plot. Default value is 6
    """

    path_to_first = '/home/rink/data/nh_descnd/N20*/'
    path_to_second = '/home/rink/data/nh_descnd/N21*/'
    product_str = cris_product_str

    run_multi(path_to_first,
              path_to_second,
              product_str)

elif mode == 'single':

    """
    Computes winds for a single overlapping pair of granules through multiple pressure levels.
    (See global parameters at top of this module).
    :param filepath_t0: path for the first granule
    :param filepath_t1: path for the second (later in time) granule
    :param product_str: product identifier
    :param do_plots: output to animated gif.
    :param do_write: output to CF-compliant NetCDF4.
    :param press_low: low pressure (hPa). Default value is 800mb
    :param press_high: high pressure (hPa). Default value is 100mb
    :param press_skip: number of pressure levels to skip. Default value is 4
    :param wind_plot_skip: skip factor for wind vector plots. Default value is 6
    """

    filepath_t0 = None
    filepath_t1 = None
    product_str = None

    run_single(filepath_t0,
               filepath_t1,
               product_str)

