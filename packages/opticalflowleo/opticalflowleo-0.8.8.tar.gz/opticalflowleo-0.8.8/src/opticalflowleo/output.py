from netCDF4 import Dataset
import numpy as np


def write_to_netcdf4(fld_reproj, ctp_reproj, u_wind, v_wind, y, x, center_lon, center_lat, filename, fld_name, z=None, has_time=False,
                     timestamp=None, use_nan=True, cartopy_map_name='LambertAzimuthalEqualArea'):
    outfile_name = filename+'.nc4'
    rootgrp = Dataset(outfile_name, 'w', format='NETCDF4')

    rootgrp.setncattr('Conventions', 'CF-1.7')

    dim_0_name = 'x'
    dim_1_name = 'y'
    time_dim_name = 'time'
    dim_2_name = 'pressure'
    # geo_coords = 'time y x'
    geo_coords = 'time pressure y x'

    if y.ndim == 2:
        rootgrp.createDimension(dim_0_name, size=y.shape[1])
        rootgrp.createDimension(dim_1_name, size=y.shape[0])
    elif y.ndim == 1:
        rootgrp.createDimension(dim_0_name, size=x.shape[0])
        rootgrp.createDimension(dim_1_name, size=y.shape[0])
    rootgrp.createDimension(time_dim_name, size=1)
    if z is not None:
        rootgrp.createDimension(dim_2_name, size=z.size)

    if timestamp is not None:
        tvar = rootgrp.createVariable('time', 'f8', time_dim_name)
        tvar[0] = timestamp
        tvar.units = 'seconds since 1970-01-01 00:00:00'

    if not has_time:
        var_dim_list = [dim_1_name, dim_0_name]
        if z is not None:
            var_dim_list = [dim_2_name, dim_1_name, dim_0_name]
    else:
        var_dim_list = [time_dim_name, dim_1_name, dim_0_name]
        if z is not None:
            var_dim_list = [time_dim_name, dim_2_name, dim_1_name, dim_0_name]

    has_z = False
    if z is not None:
        z_ds = rootgrp.createVariable(dim_2_name, 'f4', dim_2_name)
        z_ds.units = 'hPa'
        # z_ds.setncattr('axis', 'Z')
        z_ds.setncattr('standard_name', 'pressure')
        z_ds[:,] = z
        has_z = True

    if ctp_reproj is not None:
        if has_time:
            ctp_ds = rootgrp.createVariable('cloud_top_pressure', 'f4', [time_dim_name, dim_1_name, dim_0_name])
            ctp_reproj = ctp_reproj.reshape((1, y.shape[0], x.shape[0]))
        else:
            ctp_ds = rootgrp.createVariable('cloud_top_pressure', 'f4', [dim_1_name, dim_0_name])
        ctp_ds.units = 'hPa'
        ctp_ds.setncattr('coordinates', geo_coords)
        ctp_ds.setncattr('grid_mapping', 'Projection')
        ctp_ds[:,] = ctp_reproj

    data_fld_ds = rootgrp.createVariable(fld_name, 'f4', var_dim_list)
    data_fld_ds.units = 'kg kg-1'
    data_fld_ds.setncattr('coordinates', geo_coords)
    data_fld_ds.setncattr('grid_mapping', 'Projection')
    if not use_nan:
        data_fld_ds.setncattr('missing', -1.0)
    else:
        data_fld_ds.setncattr('missing', np.nan)
    if has_time:
        if has_z:
            fld_reproj = fld_reproj.reshape((1, z.shape[0], y.shape[0], x.shape[0]))
        else:
            fld_reproj = fld_reproj.reshape((1, y.shape[0], x.shape[0]))
    data_fld_ds[:, ] = fld_reproj

    u_fld_ds = rootgrp.createVariable('Derived u-component of wind', 'f4', var_dim_list)
    u_fld_ds.setncattr('standard_name', 'x_wind')
    u_fld_ds.units = 'm s-1'
    u_fld_ds.setncattr('coordinates', geo_coords)
    u_fld_ds.setncattr('grid_mapping', 'Projection')
    if not use_nan:
        u_fld_ds.setncattr('missing', -1.0)
    else:
        u_fld_ds.setncattr('missing', np.nan)
    if has_time:
        if has_z:
            u_wind = u_wind.reshape((1, z.shape[0], y.shape[0], x.shape[0]))
        else:
            u_wind = u_wind.reshape((1, y.shape[0], x.shape[0]))
    u_fld_ds[:, ] = u_wind

    v_fld_ds = rootgrp.createVariable('Derived v-component of wind', 'f4', var_dim_list)
    v_fld_ds.setncattr('standard_name', 'y_wind')
    v_fld_ds.units = 'm s-1'
    v_fld_ds.setncattr('coordinates', geo_coords)
    v_fld_ds.setncattr('grid_mapping', 'Projection')
    if not use_nan:
        v_fld_ds.setncattr('missing', -1.0)
    else:
        v_fld_ds.setncattr('missing', np.nan)
    if has_time:
        if has_z:
            v_wind = v_wind.reshape((1, z.shape[0], y.shape[0], x.shape[0]))
        else:
            v_wind = v_wind.reshape((1, y.shape[0], x.shape[0]))
    v_fld_ds[:, ] = v_wind

    if cartopy_map_name == 'LambertAzimuthalEqualArea':
        proj_ds = rootgrp.createVariable('Projection', 'b')
        proj_ds.setncattr('long_name', 'LambertAzimuthalEqualArea')
        proj_ds.setncattr('grid_mapping_name', 'lambert_azimuthal_equal_area')
        proj_ds.setncattr('latitude_of_projection_origin', center_lat)
        proj_ds.setncattr('longitude_of_projection_origin', center_lon)
    elif cartopy_map_name == 'AlbersEqualArea':
        proj_ds = rootgrp.createVariable('Projection', 'b')
        proj_ds.setncattr('long_name', 'AlbersEqualArea')
        proj_ds.setncattr('grid_mapping_name', 'albers_conical_equal_area')
        proj_ds.setncattr('latitude_of_projection_origin', center_lat)
        proj_ds.setncattr('longitude_of_projection_origin', center_lon)
        proj_ds.setncattr('standard_parallel', [20.0, 50.0])
    elif cartopy_map_name == 'Sinusoidal':
        proj_ds = rootgrp.createVariable('Projection', 'b')
        proj_ds.setncattr('long_name', 'Sinusoidal')
        proj_ds.setncattr('grid_mapping_name', 'sinusoidal')
        proj_ds.setncattr('longitude_of_projection_origin', center_lon)

    x_ds = rootgrp.createVariable(dim_0_name, 'f8', [dim_0_name])
    x_ds.units = 'meter'
    x_ds.setncattr('axis', 'X')
    x_ds.setncattr('standard_name', 'projection_x_coordinate')
    x_ds[:,] = x

    y_ds = rootgrp.createVariable(dim_1_name, 'f8', [dim_1_name])
    y_ds.units = 'meter'
    y_ds.setncattr('axis', 'Y')
    y_ds.setncattr('standard_name', 'projection_y_coordinate')
    y_ds[:,] = y
