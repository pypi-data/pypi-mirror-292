import time
import numpy as np
from scipy.interpolate import RegularGridInterpolator, griddata
from cartopy.crs import LambertAzimuthalEqualArea
import cartopy.crs as ccrs
from netCDF4 import Dataset
import largestinteriorrectangle as lir
import xarray as xr
import concurrent.futures

# resample methods:
linear = 'linear'
cubic = 'cubic'
nearest = 'nearest'


def fill_missing(fld_a, fld_b, mask):
    min_val = min(np.nanmin(fld_a), np.nanmin(fld_b))
    max_val = max(np.nanmax(fld_a), np.nanmax(fld_b))
    random_values_a = np.random.uniform(min_val, max_val, size=fld_a.shape)
    random_values_b = np.random.uniform(min_val, max_val, size=fld_a.shape)

    fld_a[mask] = random_values_a[mask]
    fld_b[mask] = random_values_b[mask]


def time_linear_interp_grids(grid_a, grid_b, time_a, time_b, time_i):
    grd_shape = grid_a.shape

    grid_a = grid_a.flatten()
    grid_b = grid_b.flatten()

    del_time = time_b - time_a

    w_a = 1.0 - (time_i - time_a) / del_time
    w_b = (time_i - time_a) / del_time

    grid_i = w_a * grid_a + w_b * grid_b
    grid_i = np.reshape(grid_i, grd_shape)

    return grid_i


def rotate_grid(x, y, angle):
    """
    Rotates a grid by a given angle (counter-clockwise from x^ in a right-handed coordinate system.

    :param x: x coordinates of grid
    :param y: y coordinates of grid
    :param angle: rotation angle in radians
    :return: the rotated grid coordinates
    """
    x_r = x * np.cos(angle) - y * np.sin(angle)
    y_r = x * np.sin(angle) + y * np.cos(angle)

    return x_r, y_r


def resample_reg_grid(scalar_field, y, x, y_s, x_s, method='linear'):

    intrp = RegularGridInterpolator((y, x), scalar_field, method=method, bounds_error=False)

    xg, yg = np.meshgrid(x_s, y_s, indexing='xy')
    yg, xg = yg.flatten(), xg.flatten()
    pts = np.array([yg, xg])
    t_pts = np.transpose(pts)

    return np.reshape(intrp(t_pts), (y_s.shape[0], x_s.shape[0]))


def resample(scalar_field, y_d, x_d, y_t, x_t, method='linear'):
    # 2D target locations shape
    t_shape = y_t.shape
    # reproject scalar fields
    fld_repro = griddata((y_d.flatten(), x_d.flatten()), scalar_field.flatten(),(y_t.flatten(), x_t.flatten()), method=method)
    # TODO: experimental parallel processing. See test_parallel below and my_griddata
    # fld_repro = my_griddata((y_d, x_d), scalar_field,(y_t, x_t), method=method)
    fld_repro = fld_repro.reshape(t_shape)
    return fld_repro


# def my_griddata(data_yx, scalar_field, map_yx, method='linear'):
#     # split y_d, x_d, scalar_field along the outer dimension
#     outer_dim_len = scalar_field.shape[1]
#     y_d = data_yx[0]
#     x_d = data_yx[1]
#     y_d_s = np.split(y_d, 2, axis=0)
#     x_d_s = np.split(x_d, 2, axis=0)
#     scalar_field_s = np.split(scalar_field, 2, axis=0)
#     y_t = map_yx[0]
#     x_t = map_yx[1]
#     y_t_s = np.split(y_t, 2, axis=0)
#     x_t_s = np.split(x_t, 2, axis=0)
#
#     with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
#
#         result = list(executor.map(griddata, [(y_d_s[0].flatten(), x_d_s[0].flatten()), (y_d_s[1].flatten(), x_d_s[1].flatten())],
#                                    [scalar_field_s[0].flatten(), scalar_field_s[1].flatten()],
#                                    [(y_t_s[0].flatten(), x_t_s[0].flatten()), (y_t_s[1].flatten(), x_t_s[1].flatten())]))
#     result = np.concatenate(result, axis=0)
#
#     return result


# -----------------------------------------------------------------------
# Keep this for now, it's a version of reproject below that does the rotate grid thing to try and better align the
# orbit track with the axes of the map projection grid.
# def reproject(fld_2d, lat_2d, lon_2d, proj, target_grid=None, grid_spacing=15000, method=linear, grid_rotate_angle=None):
#     """
#     :param fld_2d: the 2D scalar field to reproject
#     :param lat_2d: 2D latitude of the scalar field domain
#     :param lon_2d: 2D longitude of the scalar field domain
#     :param proj: the map projection (Cartopy). Default: LambertAzimuthalEqualArea
#     :param target_grid: the resampling target (y_map, x_map) where y_map and x_map are 2D. If None, the grid is
#            created automatically. The target grid is always returned.
#     :param grid_spacing: distance between the target grid points (in meters)
#     :param method: resampling method: 'linear', 'nearest', 'cubic'
#     :param grid_rotate_angle: target grid rotation angle (in radians)
#     :return: reprojected 2D scalar field, the target grid (will be 2D if rotate=True)
#     """
#
#     data_xy = proj.transform_points(ccrs.PlateCarree(), lon_2d, lat_2d)[..., :2]
#
#     # Generate a regular 2d grid extending the min and max of the xy dimensions with spacing of 20000m
#     if target_grid is None:
#         x_min, y_min = np.amin(data_xy, axis=(0, 1))
#         x_max, y_max = np.amax(data_xy, axis=(0, 1))
#         # Make the target domain just a little bigger
#         x_map = np.arange(x_min - grid_spacing, x_max + grid_spacing, grid_spacing)
#         y_map = np.arange(y_min - grid_spacing, y_max + grid_spacing, grid_spacing)
#         x_map_2d, y_map_2d = np.meshgrid(x_map, y_map)
#     else:
#         y_map_2d, x_map_2d = target_grid
#
#     if grid_rotate_angle is not None:
#         x_map_2d, y_map_2d = rotate_grid(x_map_2d, y_map_2d, grid_rotate_angle)
#     fld_reproj = resample(fld_2d, data_xy[..., 1], data_xy[..., 0], y_map_2d, x_map_2d, method=method)
#
#     return fld_reproj, (y_map_2d, x_map_2d)
#  --------------------------------------------------------------------------------------------------


def reproject(fld_2d, lat_2d, lon_2d, proj, region_grid=None, target_grid=None, grid_spacing=15000, method=linear):
    """
    :param fld_2d: the 2D scalar field to reproject
    :param lat_2d: 2D latitude of the scalar field domain
    :param lon_2d: 2D longitude of the scalar field domain
    :param proj: the map projection (Cartopy). Default: LambertAzimuthalEqualArea
    :param region_grid: the larger region grid that we pull the target grid from
    :param target_grid: the resampling target (y_map, x_map) where y_map and x_map are 2D. If None, the grid is created
           automatically. The target grid is always returned.
    :param grid_spacing: distance between the target grid points (in meters)
    :param method: resampling method: 'linear', 'nearest', 'cubic'
    :param grid_rotate_angle: target grid rotation angle (in radians)
    :return: reprojected 2D scalar field, the target grid (will be 2D if rotate=True)
    """

    data_xy = proj.transform_points(ccrs.PlateCarree(), lon_2d, lat_2d)[..., :2]

    # Generate a regular 2d grid extending the min and max of the xy dimensions with grid_spacing
    if target_grid is None:
        x_min, y_min = np.amin(data_xy, axis=(0, 1))
        x_max, y_max = np.amax(data_xy, axis=(0, 1))
        if region_grid is not None:
            # find the sub grid (target) in the larger region grid
            rmap_y_1d, rmap_x_1d = region_grid
            # Finding the nearest neighbor indexes of x_min, y_min in the numpy arrays rmap_y_1d and rmap_x_1d
            y_min_idx = np.abs(rmap_y_1d - y_min).argmin()
            x_min_idx = np.abs(rmap_x_1d - x_min).argmin()
            y_max_idx = np.abs(rmap_y_1d - y_max).argmin()
            x_max_idx = np.abs(rmap_x_1d - x_max).argmin()

            y_min = rmap_y_1d[y_min_idx]
            y_max = rmap_y_1d[y_max_idx]
            x_min = rmap_x_1d[x_min_idx]
            x_max = rmap_x_1d[x_max_idx]

        x_map = np.arange(x_min, x_max, grid_spacing)
        y_map = np.arange(y_min, y_max, grid_spacing)
        x_map_2d, y_map_2d = np.meshgrid(x_map, y_map)
    else:
        y_map_2d, x_map_2d = target_grid

    fld_reproj = resample(fld_2d, data_xy[..., 1], data_xy[..., 0], y_map_2d, x_map_2d, method=method)

    return fld_reproj, (y_map_2d, x_map_2d)


def bisect_great_circle(lon_a, lat_a, lon_b, lat_b):
    lon_a = np.radians(lon_a)
    lat_a = np.radians(lat_a)
    lon_b = np.radians(lon_b)
    lat_b = np.radians(lat_b)

    dlon = lon_b - lon_a

    Bx = np.cos(lat_b) * np.cos(dlon)
    By = np.cos(lat_b) * np.sin(dlon)

    lat_c = np.arctan2(np.sin(lat_a) + np.sin(lat_b), np.sqrt((np.cos(lat_a) + Bx) ** 2 + By ** 2))
    lon_c = lon_a + np.arctan2(By, np.cos(lat_a) + Bx)

    lon_c = np.degrees(lon_c)
    lat_c = np.degrees(lat_c)

    return lon_c, lat_c


def get_rotation_angle(lat_2d, lon_2d, proj):
    track_len, xtrack_len = lat_2d.shape

    # determine an along-track unit vector in the map projection coordinate system
    lat_a, lon_a = lat_2d[0, xtrack_len // 2], lon_2d[0, xtrack_len // 2]
    lat_b, lon_b = lat_2d[track_len-1, xtrack_len // 2], lon_2d[track_len-1, xtrack_len // 2]
    x_a, y_a = proj.transform_point(lon_a, lat_a, ccrs.PlateCarree())
    x_b, y_b = proj.transform_point(lon_b, lat_b, ccrs.PlateCarree())
    mag = np.sqrt((x_b - x_a) ** 2 + (y_b - y_a) ** 2)
    u_vec = [(x_b - x_a) / mag, (y_b - y_a) / mag]

    # compute angle between along track unit vector and map y^
    y_vec = [0, 1]
    rotation_angle = np.arccos(np.dot(u_vec, y_vec))

    return rotation_angle


def make_reproj_pair(geodata_t0, geodata_t1, lvl_idx=None, projection=None, region_grid=None, grid_spacing=15000, method=linear, do_rotate=False):

    fld_2d_t0, lon_2d_t0, lat_2d_t0, cen_lon_t0, cen_lat_t0 = (
        geodata_t0.fld_2d, geodata_t0.lon_2d, geodata_t0.lat_2d, geodata_t0.cen_lon, geodata_t0.cen_lat)

    fld_2d_t1, lon_2d_t1, lat_2d_t1, cen_lon_t1, cen_lat_t1 = (
        geodata_t1.fld_2d, geodata_t1.lon_2d, geodata_t1.lat_2d, geodata_t1.cen_lon, geodata_t1.cen_lat)

    if projection is None:
        cen_lon, cen_lat = bisect_great_circle(cen_lon_t0, cen_lat_t0, cen_lon_t1, cen_lat_t1)
        proj = LambertAzimuthalEqualArea(central_longitude=cen_lon, central_latitude=cen_lat)
    else:
        proj = projection

    # -- Need to do more work on this rotate stuff -------------------------
    # rot_angle = None
    # if do_rotate:
    #     rot_angle = get_rotation_angle(lat_2d_t0, lon_2d_t0, proj)
    #     print('Rotation angle: ', np.degrees(rot_angle))

    if lvl_idx is not None:
        fld_2d_t0 = fld_2d_t0[lvl_idx, ]
        fld_2d_t1 = fld_2d_t1[lvl_idx, ]

    fld_proj_0, grid_0 = reproject(fld_2d_t0, lat_2d_t0, lon_2d_t0, proj, region_grid=region_grid, grid_spacing=grid_spacing, method=method)
    fld_proj_1, _ = reproject(fld_2d_t1, lat_2d_t1, lon_2d_t1, proj, region_grid=region_grid, target_grid=grid_0, grid_spacing=grid_spacing, method=method)

    mask = np.logical_or(np.isnan(fld_proj_0), np.isnan(fld_proj_1))

    fld_proj_0[mask] = np.nan
    fld_proj_1[mask] = np.nan

    y_map_2d, x_map_2d = grid_0

    # Convert numpy.ndarray to xarray.DataArray
    # fld_proj_0_xr = xr.DataArray(fld_proj_0, coords={"y": y_map, "x": x_map}, dims=["y", "x"])
    # fld_proj_1_xr = xr.DataArray(fld_proj_1, coords={"y": y_map, "x": x_map}, dims=["y", "x"])

    return fld_proj_0, fld_proj_1, y_map_2d, x_map_2d, proj, mask


def make_tiles(fld_2d, T):
    """
    Divide the 2D array into M x N tiles of dimension T x T and return a list
    of all tiles without any NaN values.

    :param fld_2d: Input 2D array to split into tiles
    :param T: The dimension of the tile. The tile will be of size T x T
    :return: list of tiles (2D arrays) without any NaN values
    """
    # Determine the shape of the input array
    M, N = fld_2d.shape

    # Compute the number of tiles along each axis
    tile_cnt_x = N // T
    tile_cnt_y = M // T

    tiles = []  # List to hold the tiles
    coords = []

    # Loop over tiles
    for j in range(tile_cnt_y):
        for i in range(tile_cnt_x):
            # Extract the tile
            tile = fld_2d[j*T:(j+1)*T, i*T:(i+1)*T]
            # If there are no NaN values in the tile, then add it to the list
            if not np.isnan(tile).any():
                tiles.append(tile)
                coords.append([[j*T, i*T], [(j+1)*T, (i+1)*T]])

    return tiles, coords


def get_rectangle(fld_0):
    rect = lir.lir(np.where(np.isnan(fld_0), False, True))
    return [rect[1], rect[0]], [rect[3], rect[2]]


def worker(value_array, scalar_value=2):
    for k in range(len(value_array)):
        value_array[k] *= scalar_value
    return value_array


# Remove this soon.
def test_parallel():
    num_elems = 100000000
    value_array = [k for k in range(num_elems)]

    value_array1 = [k for k in range(int(num_elems/4))]
    value_array2 = [k for k in range(int(num_elems/4))]
    value_array3 = [k for k in range(int(num_elems/4))]
    value_array4 = [k for k in range(int(num_elems/4))]

    scalar_value = 4
    t0 = time.time()
    value_array = worker(value_array, scalar_value=scalar_value)
    t1 = time.time()
    print('total time: ', (t1 - t0))

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(worker, value_array1, scalar_value=scalar_value),
                   executor.submit(worker, value_array2, scalar_value=scalar_value),
                   executor.submit(worker, value_array3, scalar_value=scalar_value),
                   executor.submit(worker, value_array4, scalar_value=scalar_value)]
        t0 = time.time()
        result = [f.result() for f in futures]
        t1 = time.time()
        print('total time: ', (t1 - t0))
        # result = list(executor.map(worker, [value_array1, value_array2, value_array3, value_array4],
        #                            [scalar_value, scalar_value, scalar_value, scalar_value]))
