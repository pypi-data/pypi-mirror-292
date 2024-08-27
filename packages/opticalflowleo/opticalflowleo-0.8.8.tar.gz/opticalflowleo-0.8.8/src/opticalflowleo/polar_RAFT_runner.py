import h5py
import matplotlib.pyplot as plt
from metpy.units import units

from opticalflowleo.resample import *
from opticalflowleo.raft_inference import RAFT_inference
from opticalflowleo.cld_mask_cth import simple_cld_mask
from opticalflowleo.output import write_to_netcdf4
from opticalflowleo.plot import make_plots
import re
import datetime
from datetime import timezone
import os
from opticalflowleo.ssec_rink_util.util import value_to_index
from opticalflowleo.ssec_rink_util.files import ATMS_MIRS, CrIS_Retrieval
import math
from pathlib import Path

home_dir = str(Path.home())

# list of supported products:
cris_product_str = "CrIS_retrvl"
metop_avhrr_product_str = "METOP_AVHRR"
atms_mirs_product_str = "ATMS_MIRS_retrvl"

# User parameters -----------------------------------------------------------------------------------------------
# set the product to one of the above
product_str = cris_product_str

# locations of the CrIS retrievals, separated by satellite platform
# Note: the directories can contain wildcard characters to indicate that they are recursive.
# The descending orbit:
path_to_jpss20 = os.environ.get("path_to_jpss20", "/Users/tomrink/data/cris/twin_hurricanes/nh_descnd/N20*/")
path_to_jpss21 = os.environ.get("path_to_jpss21", "/Users/tomrink/data/cris/twin_hurricanes/nh_descnd/N21*/")
path_to_npp = os.environ.get("path_to_npp", "/Users/tomrink/data/cris/twin_hurricanes/nh_descnd/NPP*/")

# The ascending orbit:
# path_to_jpss20 = os.environ.get("path_to_jpss20", "/Users/tomrink/data/cris/twin_hurricanes/nh_ascnd/N20*/")
# path_to_jpss21 = os.environ.get("path_to_jpss21", "/Users/tomrink/data/cris/twin_hurricanes/nh_ascnd/N21*/")
# path_to_npp = os.environ.get("path_to_npp", "/Users/tomrink/data/cris/twin_hurricanes/nh_ascnd/NPP*/")

path_to_first = path_to_jpss20
path_to_second = path_to_jpss21
# path_to_first = path_to_jpss21
# path_to_second = path_to_npp

# Set vertical coordinate (pressure) range. Note: these are ignord for AVHRR.
# set these for run_single and run_multi (ignores single_press below)
press_low_default = 100.0  # millibars
press_high_default = 800.0
press_skip_default = 4

# Set this for run_multi_accum (ignores pressure range above)
single_press_default = 200.0

# Done user parameters ----------------------------------------------------------------------------------------

# The fixed CrIS retrieval vertical pressure levels
Plevs = [
    0.005,
    0.0161,
    0.0384,
    0.0769,
    0.137,
    0.2244,
    0.3454,
    0.5064,
    0.714,
    0.9753,
    1.2972,
    1.6872,
    2.1526,
    2.7009,
    3.3398,
    4.077,
    4.9204,
    5.8776,
    6.9567,
    8.1655,
    9.5119,
    11.0038,
    12.6492,
    14.4559,
    16.4318,
    18.5847,
    20.9224,
    23.4526,
    26.1829,
    29.121,
    32.2744,
    35.6505,
    39.2566,
    43.1001,
    47.1882,
    51.5278,
    56.126,
    60.9895,
    66.1253,
    71.5398,
    77.2396,
    83.231,
    89.5204,
    96.1138,
    103.0172,
    110.2366,
    117.7775,
    125.6456,
    133.8462,
    142.3848,
    151.2664,
    160.4959,
    170.0784,
    180.0183,
    190.3203,
    200.9887,
    212.0277,
    223.4415,
    235.2338,
    247.4085,
    259.9691,
    272.9191,
    286.2617,
    300,
    314.1369,
    328.6753,
    343.6176,
    358.9665,
    374.7241,
    390.8926,
    407.4738,
    424.4698,
    441.8819,
    459.7118,
    477.9607,
    496.6298,
    515.72,
    535.2322,
    555.1669,
    575.5248,
    596.3062,
    617.5112,
    639.1398,
    661.192,
    683.6673,
    706.5654,
    729.8857,
    753.6275,
    777.7897,
    802.3714,
    827.3713,
    852.788,
    878.6201,
    904.8659,
    931.5236,
    958.5911,
    986.0666,
    1013.948,
    1042.232,
    1070.917,
    1100,
]
cris_press_levs_nd = np.array(Plevs)

# Re-projection target grid resolution
# CrIS retrieval
grid_spacing = 8000.0  # meters
# AVHRR
avhrr_skip = 2
# grid_spacing = avhrr_skip * 1200.0

# Time delta between overlapping granules (nominal)
# JPSS
time_difference = 1440  # seconds
# METOP
# time_difference = 2880

# CrIS retrieval field of interest
field_name = "H2OMMR"  # Specific Humidity
# AVHRR
# field_name = 'scene_radiances5'
# ATMS MIRS
# field_name = 'PVapor'

# units definition
spd_unit = units("m/s")
press_unit = units("mb")

# Must be equal area map projections for now: we use the constant grid size to unscale the predicted wind components
cartopy_map_name = "LambertAzimuthalEqualArea"
# cartopy_map_name = 'AlbersEqualArea'
# cartopy_map_name = 'Sinusoidal'

# RAFT model dimensions
# CrIS Retrieval ------
RAFT_tile_size = 128
# AVHRR ---------------
# RAFT_tile_size = 512
RAFT_overlap = 0

# Parameter dictionaries:
cris_rtvl_params = {'product_str': cris_product_str,
                    'grid_spacing': 8000.0,
                    'time_difference': 1440.0,
                    'field_name': 'H2OMMR',
                    'cartopy_map_name': 'LambertAzimuthalEqualArea',
                    'remap_method': 'linear'}

atms_mirs_rtvl_params = {'product_str': atms_mirs_product_str,
                         'grid_spacing': 8000.0,
                         'time_difference': 1440.0,
                         'field_name': 'PVapor',
                         'cartopy_map_name': 'LambertAzimuthalEqualArea',
                         'remap_method': 'linear'}

avhrr_params = {'product_str': metop_avhrr_product_str,
                'grid_spacing': avhrr_skip * 1200.0,
                'time_difference': 2880.0,
                'field_name': 'scene_radiances5',
                'cartopy_map_name': 'LambertAzimuthalEqualArea',
                'remap_method': 'linear'}


class OverlapPair:
    """
    This class, Iterable, generates pairs of granule files between two polar orbiting platforms in a train formation
    separated by time. Successive pairs will be time ordered (increasing)
    """

    def __init__(self, fileset_1, fileset_2, t_lo_minutes=22, t_hi_minutes=26):
        """
        :param fileset_1: an instance of datasource.Files for the first (first to cross equator) polar orbiting platform.
        :param fileset_2: same as fileset_1, except for the second (crosses Equator after the first) polar orbiting platform.
        Note: the directories can contain wildcard characters to indicate that they are recursive.
        :param t_lo_minutes: the low end of the interval containing the time offset between the two platforms.
        :param t_hi_minutes: The high end of the interval. These can be negative but t_hi must be greater than t_lo.
        Note: the offset will likely be fixed but this allows for some slop - application dependent.
        """

        self.files_1 = fileset_1
        self.files_2 = fileset_2
        self.t_lo_minutes = t_lo_minutes
        self.t_hi_minutes = t_hi_minutes
        self._current_index = 0

        self.file_list1 = []
        self.file_list2 = []
        self.time_diff = []

        for file1, ts_1, tend, dto in self.files_1:
            file2, ts_2, _ = self.files_2.get_file_in_range(
                ts_1, self.t_lo_minutes, self.t_hi_minutes
            )
            if file2 is not None:
                self.file_list1.append(file1)
                self.file_list2.append(file2)
                self.time_diff.append(ts_2 - ts_1)
                print(file1, file2, (ts_2 - ts_1))
            else:
                print("no match")

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < len(self.file_list1):
            pair = (
                self.file_list1[self._current_index],
                self.file_list2[self._current_index],
                self.time_diff[self._current_index],
            )
            self._current_index += 1
            return pair
        else:
            raise StopIteration


class GeoData:
    """
    A simple container for geographical information and metadata.
    """

    def __init__(
        self,
        filename,
        fld_name,
        fld_2d,
        lon_2d,
        lat_2d,
        cen_lon,
        cen_lat,
        dt_obj,
        datetime_str,
        pltfrm_str,
        pressure_levels=None,
        pressure_levels_all=None
    ):
        self.filename = filename
        self.field_name = fld_name
        self.fld_2d = fld_2d
        self.lon_2d = lon_2d
        self.lat_2d = lat_2d
        self.cen_lon = cen_lon
        self.cen_lat = cen_lat
        self.dt_obj = dt_obj
        self.datetime_str = datetime_str
        self.pltfrm_str = pltfrm_str
        self.pressure_levels = pressure_levels
        self.pressure_levels_all = pressure_levels_all


# class CrIS_Retrieval(Files):
#     def __init__(self, files_path, file_time_span=8, pattern='CrIS_*atm_prof_rtv.h5'):
#         super().__init__(files_path, file_time_span, pattern)
#
#     def get_datetime(self, pathname):
#         filename = os.path.split(pathname)[1]
#         dt_str = re.search('_d.{14}', filename).group(0)
#         dto = datetime.datetime.strptime(dt_str, '_d%Y%m%d_t%H%M').replace(tzinfo=timezone.utc)
#         return dto


def extract_cris_rtvl(filename, fld_name, press_low, press_high, press_skip):
    pressure_slice = slice(
        value_to_index(cris_press_levs_nd, press_low),
        value_to_index(cris_press_levs_nd, press_high) + 1,
        press_skip,
    )
    press_levels = cris_press_levs_nd[pressure_slice]

    with h5py.File(filename, "r") as h5f:
        fld_2d = h5f[fld_name][pressure_slice, :, :]
        lon_2d = h5f["Longitude"][:, :]
        lat_2d = h5f["Latitude"][:, :]
        ylen, xlen = lon_2d.shape

    cen_lon = lon_2d[ylen // 2, xlen // 2]
    cen_lat = lat_2d[ylen // 2, xlen // 2]

    match = re.search(r"CrIS.*_d(\d*)_t(\d{6})", filename)
    dt_str = match.groups()
    datetime_obj = datetime.datetime.strptime(
        "%s%s" % (dt_str[0], dt_str[1]), "%Y%m%d%H%M%S"
    ).replace(tzinfo=timezone.utc)
    datetime_str = datetime_obj.strftime("%Y-%m-%d_%H:%M:%S")

    match = re.search(r"CrIS_(.{3})_", os.path.basename(filename))
    pltfrm_str = match.group(1).upper()

    return GeoData(
        filename,
        fld_name,
        fld_2d,
        lon_2d,
        lat_2d,
        cen_lon,
        cen_lat,
        datetime_obj,
        datetime_str,
        pltfrm_str,
        pressure_levels=press_levels,
        pressure_levels_all=cris_press_levs_nd
    )


def extract_atms_mirs(filename, fld_name, press_low, press_high, press_skip):
    with h5py.File(filename, "r") as h5f:
        player = h5f['Player'][:]
        pressure_slice = slice(
            value_to_index(player, press_low),
            value_to_index(player, press_high) + 1,
            press_skip,
        )
        press_levels = player[pressure_slice]

        fld_2d = h5f[fld_name][:, :, pressure_slice]
        lon_2d = h5f["Longitude"][:, :]
        lat_2d = h5f["Latitude"][:, :]
        ylen, xlen = lon_2d.shape

    cen_lon = lon_2d[ylen // 2, xlen // 2]
    cen_lat = lat_2d[ylen // 2, xlen // 2]

    fname = os.path.basename(filename)
    dt_str = re.search('_s.{12}', fname).group(0)
    datetime_obj = datetime.datetime.strptime(dt_str, "_s%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    datetime_str = datetime_obj.strftime("%Y-%m-%d_%H:%M:%S")

    pltfrm_str = fname.split('_')[2].upper()

    return GeoData(
        filename,
        fld_name,
        fld_2d,
        lon_2d,
        lat_2d,
        cen_lon,
        cen_lat,
        datetime_obj,
        datetime_str,
        pltfrm_str,
        pressure_levels=press_levels,
        pressure_levels_all=player
    )


def extract_avhrr(filename, fld_name):
    with h5py.File(filename, "r") as h5f:
        fld_ds = h5f[fld_name]
        scale = fld_ds.attrs["scale_factor"]
        fld_2d = fld_ds[::avhrr_skip, ::avhrr_skip]
        fld_2d = fld_2d.astype("float32")
        if scale is not None:
            fld_2d *= scale
        # convert radiance to BT -------------------------
        channel_5_wnc = h5f.attrs["channel_5_wnc"][0]
        channel_5_beta = h5f.attrs["channel_5_beta"][0]
        channel_5_alpha = h5f.attrs["channel_5_alpha"][0]
        c1 = h5f.attrs["c1"][0]
        c2 = h5f.attrs["c2"][0]

        a = c2 * channel_5_wnc
        b = np.log(1.0 + c1 * math.pow(channel_5_wnc, 3) / fld_2d)
        bt_2d = (a / b - channel_5_beta) / channel_5_alpha

        start_time = h5f["record_start_time"][0]
        start_time = start_time.astype("float64")
        dt_obj = datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds=start_time)
        dt_obj = dt_obj.replace(tzinfo=timezone.utc)
        datetime_str = dt_obj.strftime("%Y-%m-%d_%H:%M:%S")

        match = re.search(r"METOP(.{1})", os.path.basename(filename))
        pltfrm_str = match.group(1).upper()

        lon_ds = h5f["lon"]
        lat_ds = h5f["lat"]
        lat_2d = lat_ds[::avhrr_skip, ::avhrr_skip]
        lon_2d = lon_ds[::avhrr_skip, ::avhrr_skip]
        lat_2d = lat_2d.astype("float32")
        lon_2d = lon_2d.astype("float32")
        scale = lon_ds.attrs["scale_factor"]
        if scale is not None:
            lat_2d *= scale
            lon_2d *= scale

        ylen, xlen = lon_2d.shape

    cen_lon = lon_2d[ylen // 2, xlen // 2]
    cen_lat = lat_2d[ylen // 2, xlen // 2]

    return GeoData(
        filename,
        fld_name,
        bt_2d,
        lon_2d,
        lat_2d,
        cen_lon,
        cen_lat,
        dt_obj,
        datetime_str,
        pltfrm_str,
    )


def extract_data(filename, fld_name, product_str, press_low, press_high, press_skip):
    if product_str == cris_product_str:
        return extract_cris_rtvl(filename, fld_name, press_low, press_high, press_skip)
    elif product_str == metop_avhrr_product_str:
        return extract_avhrr(filename, fld_name)
    elif product_str == atms_mirs_product_str:
        return extract_atms_mirs(filename, fld_name, press_low, press_high, press_skip)


def _run_single(
    filename_t0: str,
    filename_t1: str,
    params_dict: dict,
    do_plots: bool = False,
    do_write: bool = True,
    wind_plot_skip: int = 6,
    press_low: float = press_low_default,
    press_high: float = press_high_default,
    press_skip: int = single_press_default
):
    """
    Computes winds for a single overlapping pair of granules through multiple pressure levels.
    (See global parameters at top of this module).
    :param filename_t0: path for the first granule
    :param filename_t1: path for the second (later in time) granule
    :param params_dict: dictionary with parameters
    :param do_plots: output to animated gif.
    :param do_write: output to CF-compliant NetCDF4.
    :param press_low: low pressure
    :param press_high: high pressure
    :param press_skip: number of pressure levels to skip
    :param wind_plot_skip: skip factor for wind vector plots.
    :return:
    """
    # An instance of the wind prediction model
    inference = RAFT_inference(tile_size=RAFT_tile_size, overlap=RAFT_overlap)

    geodata_t0 = extract_data(filename_t0, params_dict['field_name'], params_dict['product_str'], press_low, press_high, press_skip)
    geodata_t1 = extract_data(filename_t1, params_dict['field_name'], params_dict['product_str'], press_low, press_high, press_skip)

    _process_pair_one(
        geodata_t0,
        geodata_t1,
        inference,
        params_dict['grid_spacing'],
        params_dict['time_difference'],
        do_plots=do_plots,
        do_write=do_write,
        wind_plot_skip=wind_plot_skip
    )
    # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    #     executor.submit(_process_pair_one,
    #                     geodata_t0,
    #                     geodata_t1,
    #                     inference,
    #                     grid_spacing,
    #                     time_difference,
    #                     do_plots=do_plots,
    #                     do_write=do_write,
    #                     wind_plot_skip=wind_plot_skip)


def _process_pair(
    geodata_t0,
    geodata_t1,
    inference,
    params_dict,
    time_delta,
    do_plots=False,
    do_write=True,
    wind_plot_skip: int = 6
):

    cen_lon, cen_lat = bisect_great_circle(
        geodata_t0.cen_lon, geodata_t0.cen_lat, geodata_t1.cen_lon, geodata_t1.cen_lat
    )

    cartopy_map_name = params_dict['cartopy_map_name']
    grid_spacing = params_dict['grid_spacing']
    remap_method = params_dict['remap_method']

    if cartopy_map_name == "LambertAzimuthalEqualArea":
        projection = ccrs.LambertAzimuthalEqualArea(
            central_longitude=cen_lon, central_latitude=cen_lat
        )
    elif cartopy_map_name == "AlbersEqualArea":
        projection = ccrs.AlbersEqualArea(
            central_longitude=cen_lon, central_latitude=cen_lat
        )
    elif cartopy_map_name == "Sinusoidal":
        projection = ccrs.Sinusoidal(central_longitude=cen_lon)
    else:
        raise ValueError("Projection: " + cartopy_map_name + " is not supported")

    flds_t0 = []
    u_map_s = []
    v_map_s = []
    x_map_1d = None  # These will be the same for all pressure levels
    y_map_1d = None  # " "
    ctp_reproj = None
    press_levels = geodata_t0.pressure_levels

    for lvl_idx in range(press_levels.size):

        try:
            fld_0, fld_1, y_map_2d, x_map_2d, tile_proj, fill_mask = make_reproj_pair(
                geodata_t0,
                geodata_t1,
                lvl_idx=lvl_idx,
                projection=projection,
                grid_spacing=grid_spacing,
                method=remap_method,
                do_rotate=False,
            )
        except Exception as e:
            print("problem remapping adjacent granules, moving on to next pair")
            print(e)
            return

        print("Granule re-projection grid: ", y_map_2d.shape)
        if y_map_2d.shape[0] < RAFT_tile_size or y_map_2d.shape[1] < RAFT_tile_size:
            print("re-projection grid too small, moving on to next pair")
            return

        # This extracts the largest rectangle from the union of the two adjacent granules.
        # This is necessary because the RAFT model can't handle too much patterned missing data.
        # NaN values can cause this rectangle to change through pressure levels, so we just use the dimensions
        # from the first level. TODO: Add an extra step which does a reproject only to determine the best region. One
        # possibility: remap to grids with flat ranges and mark only the pixels w/o valid mapping for get_rectangle()
        # Or, use a special code that get_rectangle recognizes, but NaNs might still be a problem...
        if lvl_idx == 0:
            (y_a, x_a), (h, w) = get_rectangle(fld_0)

            # Adjusting h and w to be the next lowest even number
            h = h - 1 if h % 2 else h
            w = w - 1 if w % 2 else w
            if h < RAFT_tile_size or w < RAFT_tile_size:
                print("extracted region too small, nothing to do")
                return
            y_b = y_a + h
            x_b = x_a + w

        tile_0 = fld_0[y_a:y_b, x_a:x_b]
        tile_1 = fld_1[y_a:y_b, x_a:x_b]
        print("Extracted tile shape for inference: ", tile_0.shape)

        try:
            v, u = inference.do_inference(
                tile_0, tile_1, None, None, None, convert_cartesian=False
            )
        except Exception as e:
            print("problem with inference, moving to next pair")
            print(e)
            return

        if lvl_idx == 0:  # only need to do this once
            h5f = h5py.File(geodata_t0.filename, "r")
            rtrvl_temp_3d = h5f[geodata_t0.field_name][:, :, :]
            model_temp_3d = h5f["GDAS_TAir"][:, :, :]
            _, ctp, _ = simple_cld_mask(rtrvl_temp_3d, model_temp_3d, geodata_t0.pressure_levels_all)

            ctp_reproj, _ = reproject(
                ctp,
                geodata_t0.lat_2d,
                geodata_t0.lon_2d,
                tile_proj,
                region_grid=None,
                target_grid=(y_map_2d, x_map_2d),
                grid_spacing=15000,
                method=linear,
            )
            ctp_reproj[fill_mask] = np.nan
            ctp_reproj = ctp_reproj[y_a:y_b, x_a:x_b]
            h5f.close()

        y_map_1d = y_map_2d[y_a:y_b, 0]
        x_map_1d = x_map_2d[0, x_a:x_b]

        # Scale the non-dimensional model output in grid_cells/time_step to meters/second
        v_grd = (v * grid_spacing) / time_delta
        u_grd = (u * grid_spacing) / time_delta
        v_map = v_grd
        u_map = u_grd

        # --- set points below cloud top pressure to nan ----------
        # TODO: CTP from above looks to be wrong.
        # u_map = np.where(ctp_reproj < press_levels[lvl_idx], np.nan, u_map)
        # v_map = np.where(ctp_reproj < press_levels[lvl_idx], np.nan, v_map)

        flds_t0.append(tile_0)
        u_map_s.append(u_map)
        v_map_s.append(v_map)

        spd = np.sqrt(u_map * u_map + v_map * v_map)
        print(
            "press, spd range: ", press_levels[lvl_idx], np.nanmin(spd), np.nanmax(spd)
        )

        pltfrm_t0 = geodata_t0.pltfrm_str
        pltfrm_t1 = geodata_t1.pltfrm_str

        plevel_str = str(int(press_levels[lvl_idx])) + " " + "mb"
        title_0 = (
            pltfrm_t0
            + " "
            + geodata_t0.datetime_str
            + "  "
            + field_name
            + " "
            + plevel_str
        )
        title_1 = (
            pltfrm_t1
            + " "
            + geodata_t1.datetime_str
            + "  "
            + field_name
            + " "
            + plevel_str
        )
        t0_fname = (
            "CrIS_H2O_RAFT_uv_"
            + pltfrm_t0
            + "_"
            + geodata_t0.datetime_str
            + " "
            + plevel_str
            + ".png"
        )
        t1_fname = (
            "CrIS_H2O_RAFT_uv_"
            + pltfrm_t1
            + "_"
            + geodata_t1.datetime_str
            + " "
            + plevel_str
            + ".png"
        )
        anim_filename = (
            "CrIS_H2O_"
            + pltfrm_t0
            + "_"
            + geodata_t0.datetime_str
            + "_"
            + pltfrm_t1
            + " "
            + geodata_t1.datetime_str
            + " "
            + plevel_str
            + ".gif"
        )

        if do_plots:
            make_plots(
                tile_0,
                tile_1,
                title_0,
                title_1,
                y_map_2d,
                x_map_2d,
                v_map,
                u_map,
                y_a,
                y_b,
                x_a,
                x_b,
                t0_fname,
                t1_fname,
                anim_filename,
                projection,
                skip=wind_plot_skip
            )

    if do_write:
        fld_t0 = np.concatenate(flds_t0, axis=0)
        u_map = np.concatenate(u_map_s, axis=0)
        v_map = np.concatenate(v_map_s, axis=0)

        outfile = home_dir + "CrIS_H2O_RAFT_uv_" + geodata_t0.pltfrm_str + "_" + geodata_t0.datetime_str

        write_to_netcdf4(
            fld_t0,
            ctp_reproj,
            u_map,
            v_map,
            y_map_1d,
            x_map_1d,
            cen_lon,
            cen_lat,
            outfile,
            geodata_t0.field_name,
            timestamp=geodata_t0.dt_obj.timestamp(),
            has_time=True,
            z=press_levels,
            cartopy_map_name=cartopy_map_name,
        )

    print("_process_pair: done -----------------------------------------------------")


def _process_pair_one(
    geodata_t0,
    geodata_t1,
    inference,
    grid_spacing,
    time_difference,
    do_plots=False,
    do_write=True,
    wind_plot_skip=6,
):
    """
    For 2D fields only (not pressure or channel dimension)
    :param geodata_t0: data container for the first granule
    :param geodata_t1: data container for the second (later in time) granule
    :param inference: an instance of the pre-trained RAFT model
    :param grid_spacing: target grid spacing.
    :param time_difference: difference in time between the two orbiting platforms.
    :param do_plots: If true, plots the derived winds.
    :param do_write: If true, writes the derived winds to a CF-compliant netcdf file.
    :param wind_plot_skip: reduces number of wind vectors in the plot.
    :return:
    """

    cen_lon, cen_lat = bisect_great_circle(
        geodata_t0.cen_lon, geodata_t0.cen_lat, geodata_t1.cen_lon, geodata_t1.cen_lat
    )

    if cartopy_map_name == "LambertAzimuthalEqualArea":
        projection = ccrs.LambertAzimuthalEqualArea(
            central_longitude=cen_lon, central_latitude=cen_lat
        )
    elif cartopy_map_name == "AlbersEqualArea":
        projection = ccrs.AlbersEqualArea(
            central_longitude=cen_lon, central_latitude=cen_lat
        )
    elif cartopy_map_name == "Sinusoidal":
        projection = ccrs.Sinusoidal(central_longitude=cen_lon)
    else:
        raise ValueError("Projection: " + cartopy_map_name + " is not supported")

    flds_t0 = []
    u_map_s = []
    v_map_s = []
    ctp_reproj = None

    try:
        fld_0, fld_1, y_map_2d, x_map_2d, tile_proj, fill_mask = make_reproj_pair(
            geodata_t0,
            geodata_t1,
            projection=projection,
            grid_spacing=grid_spacing,
            method="linear",
            do_rotate=False,
        )
    except Exception as e:
        print("problem remapping adjacent granules, moving on to next pair")
        print(e)
        return

    print("Granule re-projection grid: ", y_map_2d.shape)
    if y_map_2d.shape[0] < RAFT_tile_size or y_map_2d.shape[1] < RAFT_tile_size:
        print("re-projection grid too small, moving on to next pair")
        return

    # This extracts the largest rectangle from the union of the two adjacent granules.
    # This is necessary because the RAFT model can't handle too much patterned missing data.

    (y_a, x_a), (h, w) = get_rectangle(fld_0)

    # Adjusting h and w to be the next lowest even number
    h = h - 1 if h % 2 else h
    w = w - 1 if w % 2 else w
    if h < RAFT_tile_size or w < RAFT_tile_size:
        print("extracted region too small, nothing to do")
        return
    y_b = y_a + h
    x_b = x_a + w

    tile_0 = fld_0[y_a:y_b, x_a:x_b]
    tile_1 = fld_1[y_a:y_b, x_a:x_b]
    print("Extracted tile shape for inference: ", tile_0.shape)

    try:
        v, u = inference.do_inference(
            tile_0, tile_1, None, None, None, convert_cartesian=False
        )
    except Exception as e:
        print("problem with inference, moving to next pair")
        print(e)
        return

    y_map_1d = y_map_2d[y_a:y_b, 0]
    x_map_1d = x_map_2d[0, x_a:x_b]

    # Scale the non-dimensional model output in grid_cells/time_step to meters/second
    v_grd = (v * grid_spacing) / time_difference
    u_grd = (u * grid_spacing) / time_difference
    v_map = v_grd
    u_map = u_grd

    flds_t0.append(tile_0)
    u_map_s.append(u_map)
    v_map_s.append(v_map)

    spd = np.sqrt(u_map * u_map + v_map * v_map)
    print("spd range: ", np.nanmin(spd), np.nanmax(spd))

    pltfrm_t0 = geodata_t0.pltfrm_str
    pltfrm_t1 = geodata_t1.pltfrm_str

    title_0 = pltfrm_t0 + " " + geodata_t0.datetime_str + "  " + field_name
    title_1 = pltfrm_t1 + " " + geodata_t1.datetime_str + "  " + field_name
    t0_fname = "CrIS_H2O_RAFT_uv_" + pltfrm_t0 + "_" + geodata_t0.datetime_str + ".png"
    t1_fname = "CrIS_H2O_RAFT_uv_" + pltfrm_t1 + "_" + geodata_t1.datetime_str + ".png"
    anim_filename = (
        "CrIS_H2O_"
        + pltfrm_t0
        + "_"
        + geodata_t0.datetime_str
        + "_"
        + pltfrm_t1
        + " "
        + geodata_t1.datetime_str
        + ".gif"
    )

    if do_plots:
        make_plots(
            tile_0,
            tile_1,
            title_0,
            title_1,
            y_map_2d,
            x_map_2d,
            v_map,
            u_map,
            y_a,
            y_b,
            x_a,
            x_b,
            t0_fname,
            t1_fname,
            anim_filename,
            projection,
            skip=wind_plot_skip,
        )

    if do_write:
        fld_t0 = np.concatenate(flds_t0, axis=0)
        u_map = np.concatenate(u_map_s, axis=0)
        v_map = np.concatenate(v_map_s, axis=0)

        outfile = home_dir + "CrIS_H2O_RAFT_uv_" + geodata_t0.pltfrm_str + "_" + geodata_t0.datetime_str

        write_to_netcdf4(
            fld_t0,
            ctp_reproj,
            u_map,
            v_map,
            y_map_1d,
            x_map_1d,
            cen_lon,
            cen_lat,
            outfile,
            geodata_t0.field_name,
            timestamp=geodata_t0.dt_obj.timestamp(),
            has_time=True,
            z=None,
            cartopy_map_name=cartopy_map_name,
        )

    print("Processing done -----------------------------------------------------")


def _run_multi(
    fileset_1: OverlapPair,
    fileset_2: OverlapPair,
    params_dict: dict,
    do_plots: bool = False,
    do_write: bool = True,
    press_low: float = press_low_default,
    press_high: float = press_high_default,
    press_skip: float = press_skip_default,
    wind_plot_skip: int = 6
):
    """
    Computes winds from a set (OverlapPair iterable) of overlapping pairs of granules through multiple pressure levels.
    (See global parameters at top of this module)
    :param fileset_1: an instance of OverlapPair for the first platform
    :param fileset_2: an instance of OverlapPair for the second platform
    :param params_dict: a dictionary of parameters
    :param do_plots: output to animated gif.
    :param do_write: output to CF-compliant NetCDF4 file.
    :param press_low: low pressure
    :param press_high: high pressure
    :param press_skip: skip pressure
    :param wind_plot_skip: skip factor for wind vectors in plot
    :return:
    """

    # An instance of the wind prediction model
    inference = RAFT_inference(tile_size=RAFT_tile_size, overlap=RAFT_overlap)

    ovlp_pair = OverlapPair(fileset_1, fileset_2)

    for file_1, file_2, time_delta in ovlp_pair:
        geodata_1 = extract_data(file_1, params_dict['field_name'], params_dict['product_str'], press_low, press_high, press_skip)
        geodata_2 = extract_data(file_2, params_dict['field_name'], params_dict['product_str'], press_low, press_high, press_skip)
        _process_pair(
            geodata_1,
            geodata_2,
            inference,
            params_dict,
            time_delta,
            do_plots=do_plots,
            do_write=do_write,
            wind_plot_skip=wind_plot_skip
        )
        print("_process_pair done: ", file_1, file_2)


def _process_pair_accum(
    geodata_t0,
    geodata_t1,
    inference,
    grid_spacing,
    time_difference,
    projection,
    y_rmap_2d,
    x_rmap_2d,
    region_field_2d,
    region_u_2d,
    region_v_2d,
    do_accum=True,
):
    """
    Computes winds from an overlapping pair of granules at a single pressure level
    remapping the results to a multiple orbit coverage domain.
    (See global parameters at top of this module)
    :param geodata_t0: data container for the first granule
    :param geodata_t1: data container for the second (later in time) granule
    :param inference: an instance of the pre-trained RAFT model
    :param grid_spacing: target grid spacing
    :param time_difference: difference in time between the two orbiting platforms.
    :param projection: the projection of the common domain
    :param y_rmap_2d: y locations of the target region grid
    :param x_rmap_2d: x locations of the target region grid
    :param region_field_2d: the accumulated values of the target region grid
    :param region_u_2d: the accumulated u-component of the target region grid
    :param region_v_2d: the accumulated v-component of the target region grid
    :param do_accum: True, does the accumulation. False, creates a separate region.
    :return:
    """
    try:
        fld_0, fld_1, y_map_2d, x_map_2d, tile_proj, fill_mask = make_reproj_pair(
            geodata_t0,
            geodata_t1,
            lvl_idx=0,
            grid_spacing=grid_spacing,
            method="linear",
            do_rotate=False,
        )
    except Exception as e:
        print("problem remapping adjacent granules, moving on to next pair")
        print(e)
        return

    print("Granule re-projection grid: ", y_map_2d.shape)
    if y_map_2d.shape[0] < RAFT_tile_size or y_map_2d.shape[1] < RAFT_tile_size:
        print("re-projection grid too small, moving on to next pair")
        return

    # This extracts the largest rectangle from the union of the two adjacent granules.
    # This is necessary because the RAFT model can't handle too much patterned missing data.
    (y_a, x_a), (h, w) = get_rectangle(fld_0)

    # Adjusting h and w to be the next lowest even number
    h = h - 1 if h % 2 else h
    w = w - 1 if w % 2 else w
    if h < RAFT_tile_size or w < RAFT_tile_size:
        print("extracted region too small, nothing to do")
        return
    y_b = y_a + h
    x_b = x_a + w

    tile_0 = fld_0[y_a:y_b, x_a:x_b]
    tile_1 = fld_1[y_a:y_b, x_a:x_b]
    print("Extracted tile shape for inference: ", tile_0.shape)

    try:
        v, u = inference.do_inference(
            tile_0, tile_1, None, None, None, convert_cartesian=False
        )
    except Exception as e:
        print("problem with inference, moving to next pair")
        print(e)
        return

    # Scale the non-dimensional model output in grid_cells/time_step to meters/second
    v_grd = (v * grid_spacing) / time_difference
    u_grd = (u * grid_spacing) / time_difference
    v_map = v_grd
    u_map = u_grd

    spd = np.sqrt(u_map * u_map + v_map * v_map)
    print("wind speed range: ", np.min(spd), np.max(spd))

    target_xy = projection.transform_points(
        tile_proj, x_map_2d[y_a:y_b, x_a:x_b], y_map_2d[y_a:y_b, x_a:x_b]
    )[..., :2]
    u_proj, v_proj = projection.transform_vectors(
        tile_proj, x_map_2d[y_a:y_b, x_a:x_b], y_map_2d[y_a:y_b, x_a:x_b], u_map, v_map
    )

    tile_u_region = resample(
        u_proj, target_xy[..., 1], target_xy[..., 0], y_rmap_2d, x_rmap_2d
    )
    tile_v_region = resample(
        v_proj, target_xy[..., 1], target_xy[..., 0], y_rmap_2d, x_rmap_2d
    )
    tile_0_region = resample(
        tile_0, target_xy[..., 1], target_xy[..., 0], y_rmap_2d, x_rmap_2d
    )
    tile_1_region = resample(
        tile_1, target_xy[..., 1], target_xy[..., 0], y_rmap_2d, x_rmap_2d
    )

    if do_accum:
        np.copyto(
            region_field_2d,
            tile_1_region,
            where=~np.isnan(tile_1_region) & np.isnan(region_field_2d),
        )
        np.copyto(
            region_u_2d,
            tile_u_region,
            where=~np.isnan(tile_u_region) & np.isnan(region_u_2d),
        )
        np.copyto(
            region_v_2d,
            tile_v_region,
            where=~np.isnan(tile_v_region) & np.isnan(region_v_2d),
        )
    else:
        outfile = home_dir + "CrIS_H20_RAFT_uv_" + geodata_t0.pltfrm_str + "_" + geodata_t0.datetime_str

        write_to_netcdf4(
            tile_1_region,
            None,
            tile_u_region,
            tile_v_region,
            y_rmap_2d[:, 0],
            x_rmap_2d[0, :],
            -50.0,
            30.0,
            outfile,
            geodata_t0.field_name,
            timestamp=geodata_t0.dt_obj.timestamp(),
            has_time=True,
            cartopy_map_name=cartopy_map_name,
        )

    print("Processing done -----------------------------------------------------")


def run_multi_accum(
    fileset_1: OverlapPair,
    fileset_2: OverlapPair,
    params_dict: dict,
    do_accum: bool = True,
    plot_skip: int = 10,
    lon_min: float = -100.0,
    lon_max: float = 0.0,
    lat_min: float = 0.0,
    lat_max: float = 60.0,
    press_level: float = single_press_default
):
    """
    Computes winds from a set (OverlapPair iterable) of overlapping pairs of granules at a single pressure level
    remapping the results to a multiple orbit coverage domain.
    (See global parameters at top of this module)
    :param fileset_1: an instance of datasource.Files for the first platform
    :param fileset_2: an instance of datasource.Files for the second platform
    :param do_accum: if True, creates a single coverage plot. If False, writes each pair on the coverage domain to a
    NetCDF4 file.
    :param plot_skip: how many winds to skip in the plot (default: 10)
    :param lon_min, lon_max, lat_min, lat_max: lat-lon box region definition (degrees)
    :param press_level: target pressure level
    """

    grid_spacing = params_dict['grid_spacing']
    cartopy_map_name = params_dict['cartopy_map_name']

    # Setup grid over the region of interest on the projection plane
    if cartopy_map_name == "LambertAzimuthalEqualArea":
        projection = ccrs.LambertAzimuthalEqualArea(
            central_longitude=-50.0, central_latitude=30.0
        )
    elif cartopy_map_name == "AlbersEqualArea":
        projection = ccrs.AlbersEqualArea(
            central_longitude=-50.0, central_latitude=30.0
        )
    elif cartopy_map_name == "Sinusoidal":
        projection = ccrs.Sinusoidal(central_longitude=-50.0)
    else:
        raise ValueError("Projection: " + cartopy_map_name + " is not supported")

    x_a, y_a = projection.transform_point(lon_min, lat_min, ccrs.PlateCarree())
    x_b, y_b = projection.transform_point(lon_max, lat_max, ccrs.PlateCarree())
    x_rmap_1d = np.arange(x_a, x_b, grid_spacing)
    y_rmap_1d = np.arange(y_a, y_b, grid_spacing)
    x_rmap_2d, y_rmap_2d = np.meshgrid(x_rmap_1d, y_rmap_1d)
    print("Target region: size: ", x_rmap_2d.shape)

    # initialize region arrays for the H20 field and the predicted (v, u) wind components ----
    region_field_2d = np.empty(y_rmap_2d.shape, dtype=np.float32)
    region_u_2d = np.empty(y_rmap_2d.shape, dtype=np.float32)
    region_v_2d = np.empty(y_rmap_2d.shape, dtype=np.float32)
    region_field_2d[:,] = np.nan
    region_u_2d[:,] = np.nan
    region_v_2d[:,] = np.nan

    # An instance of the wind prediction model
    inference = RAFT_inference(tile_size=RAFT_tile_size, overlap=RAFT_overlap)

    ovlp_pair = OverlapPair(fileset_1, fileset_2)

    press_low = press_level
    press_high = press_level
    press_skip = 1

    for file_1, file_2, time_delta in ovlp_pair:
        geodata_1 = extract_data(
            file_1, params_dict['field_name'], params_dict['product_str'], press_low, press_high, press_skip
        )
        geodata_2 = extract_data(
            file_2, params_dict['field_name'], params_dict['product_str'], press_low, press_high, press_skip
        )

        if not do_accum:
            region_field_2d[:,] = np.nan
            region_u_2d[:,] = np.nan
            region_v_2d[:,] = np.nan

        _process_pair_accum(
            geodata_1,
            geodata_2,
            inference,
            grid_spacing,
            time_delta,
            projection,
            y_rmap_2d,
            x_rmap_2d,
            region_field_2d,
            region_u_2d,
            region_v_2d,
            do_accum=do_accum,
        )

    if do_accum:
        plevel_str = str(int(press_level)) + " " + "mb"
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(1, 1, 1, projection=projection)
        ax.pcolormesh(x_rmap_2d, y_rmap_2d, region_field_2d, cmap="jet")
        ax.quiver(
            x_rmap_2d[::plot_skip, ::plot_skip],
            y_rmap_2d[::plot_skip, ::plot_skip],
            region_u_2d[::plot_skip, ::plot_skip],
            region_v_2d[::plot_skip, ::plot_skip],
            color="black",
            scale=1000.0,
        )
        ax.gridlines(draw_labels=True)
        ax.coastlines(resolution="50m", color="green", linewidth=0.25)
        plt.title("CrIS_" + field_name + "_RAFT_uv_" + plevel_str)
        # plt.show()
        t1_fname = (
            "CrIS_"
            + field_name
            + "_RAFT_uv_"
            + plevel_str
            + "_twin_hurricanes_"
            + "nh_descend"
            + ".png"
        )
        fig.savefig(home_dir + t1_fname, dpi=300)


def run_multi(path_to_first,
              path_to_second,
              product_str,
              do_plots: bool = False,
              do_write: bool = True,
              press_low: float = press_low_default,
              press_high: float = press_high_default,
              press_skip: float = press_skip_default,
              wind_plot_skip: int = 6):
    """
    Computes winds from a set (OverlapPair iterable) of overlapping pairs of granules through multiple pressure levels.
    (See global parameters at top of this module)
    :param path_to_first: directory containing files of first orbit platform to cross equator.
    :param path_to_second: directory containing files for the second platform
    :param product_str: name of product to work on.
    :param do_plots: output to animated gif.
    :param do_write: output to CF-compliant NetCDF4 file.
    :param press_low: low pressure
    :param press_high: high pressure
    :param press_skip: skip pressure
    :param wind_plot_skip: skip factor for wind vectors in plot
    :return:
    """

    files_1, files_2, params_dict = None, None, None

    if product_str == cris_product_str:
        files_1 = CrIS_Retrieval(path_to_first)
        files_2 = CrIS_Retrieval(path_to_second)
        params_dict = cris_rtvl_params
    elif product_str == atms_mirs_product_str:
        files_1 = ATMS_MIRS(path_to_first)
        files_2 = ATMS_MIRS(path_to_second)
        params_dict = atms_mirs_rtvl_params
    else:
        print(product_str + "Product not supported")

    _run_multi(files_1,
               files_2,
               params_dict,
               do_plots=do_plots,
               do_write=do_write,
               press_low=press_low,
               press_high=press_high,
               press_skip=press_skip,
               wind_plot_skip=wind_plot_skip
               )


def run_single(filepath_t0,
               filepath_t1,
               product_str,
               do_plots=True,
               do_write=False,
               press_low=press_low_default,
               press_high=press_high_default,
               press_skip=press_skip_default,
               wind_plot_skip=20
               ):
    """
    Computes winds for a single overlapping pair of granules through multiple pressure levels.
    (See global parameters at top of this module).
    :param filepath_t0: path for the first granule
    :param filepath_t1: path for the second (later in time) granule
    :param product_str: product identifier
    :param do_plots: output to animated gif.
    :param do_write: output to CF-compliant NetCDF4.
    :param press_low: low pressure
    :param press_high: high pressure
    :param press_skip: number of pressure levels to skip
    :param wind_plot_skip: skip factor for wind vector plots.
    :return:
    """

    params_dict = None
    if product_str == metop_avhrr_product_str:
        params_dict = avhrr_params
    else:
        print(product_str + "Product not supported")

    _run_single(filepath_t0,
                filepath_t1,
                params_dict,
                do_plots=do_plots,
                do_write=do_write,
                press_low=press_low,
                press_high=press_high,
                press_skip=press_skip,
                wind_plot_skip=wind_plot_skip
                )


if __name__ == "__main__":
    if product_str == cris_product_str:
        files_1 = CrIS_Retrieval(path_to_first)
        files_2 = CrIS_Retrieval(path_to_second)
        # run_multi_accum(files_1, files_2, cris_rtvl_params, do_accum=False)
        # run_multi_accum(files_1, files_2, cris_rtvl_params, do_accum=True)
        _run_multi(
            files_1,
            files_2,
            cris_rtvl_params,
            do_plots=False,
            do_write=True
        )
        # TODO: divide up the target directories and send subsets to different CPUs via code below.
        # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        #     executor.submit(run_multi,
        #                     files_1,
        #                     files_2,
        #                     do_plots=False,
        #                     do_write=True,
        #                     pressure_slice=pressure_slice_all,
        #                     )
    elif product_str == metop_avhrr_product_str:
        _run_single(
            "/Users/tomrink/data/avhrr/METOPC_AVHR_C_EUMP_20240703201303_29349_eps_o_l1b_7.nc",
            "/Users/tomrink/data/avhrr/METOPB_AVHR_C_EUMP_20240703210103_61192_eps_o_l1b_7.nc",
            avhrr_params,
            do_plots=True,
            do_write=False,
            wind_plot_skip=20
        )
