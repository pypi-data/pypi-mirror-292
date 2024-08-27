import datetime, os
from datetime import timezone
import glob
import numpy as np
from .util import GenericException
import re


class Files:
    """
    Provides a time-ordered view of a set of files of identical structure and contents but separated by time.
    """
    def __init__(self, files_path, file_time_span, pattern):
        """
        :param files_path: Location of target files, can have wildcard characters.
        :param file_time_span: Duration of a file (minutes). For example, an 8-minute polar orbiting granule or the
        time between successive geostationary CONUS products. Assumed to be fixed.
        :param pattern: The glob pattern that matches the files: concatenated with files_path.
        """
        self.flist = []
        self.ftimes = []
        self.dto_s = []

        for path in glob.glob(files_path + pattern, recursive=True):
            self.flist.append(path)
        if len(self.flist) == 0:
            raise GenericException('no matching files found in: ' + files_path + '  matching: ' + pattern)

        self.span_seconds = datetime.timedelta(minutes=file_time_span).seconds

        for pname in self.flist:
            dto = self.get_datetime(pname)
            dto_start = dto
            dto_end = dto + datetime.timedelta(minutes=file_time_span)
            self.ftimes.append((dto_start.timestamp(), dto_end.timestamp()))
            self.dto_s.append(dto)

        self.ftimes = np.array(self.ftimes)
        self.flist = np.array(self.flist)
        self.dto_s = np.array(self.dto_s)

        sidxs = np.argsort(self.ftimes[:, 0])  # sort on start time

        self.ftimes = self.ftimes[sidxs, :]
        self.flist = self.flist[sidxs]
        self.dto_s = self.dto_s[sidxs]

        self._current_index = 0
        self.number_of_files = len(self.flist)

    def get_number_of_files(self):
        """
        :return: The number of files self managers
        """
        return self.number_of_files

    def get_datetime(self, pathname):
        """
        :param pathname: The full-path of the file.
        :return: The file's time label as a datetime object.
        """
        pass

    def get_file_containing_time(self, timestamp):
        """
        :param timestamp: seconds since the epoch
        :return: the file whose time range contains timestamp.
        """
        k = -1
        for i in range(self.ftimes.shape[0]):
            if (timestamp >= self.ftimes[i, 0]) and (timestamp < self.ftimes[i, 1]):
                k = i
                break
        if k < 0:
            return None, None, None

        return self.flist[k], self.ftimes[k, 0], k

    def get_file(self, timestamp, window=None):
        """
        :param timestamp: seconds since the epoch.
        :param window: the duration (minutes) of files in this object. Defaults to the constructor time span.
        :return: the file whose start time is closest to timestamp.
        """
        if window is None:
            window = self.span_seconds
        else:
            window = datetime.timedelta(minutes=window).seconds
        diff = self.ftimes[:, 0] - timestamp
        midx = np.argmin(np.abs(diff))
        if np.abs(self.ftimes[midx, 0] - timestamp) < window:
            return self.flist[midx], self.ftimes[midx, 0], midx
        else:
            return None, None, None

    def get_file_in_range(self, timestamp, t_lo_minutes, t_hi_minutes):
        """
        :param timestamp:
        :param t_lo_minutes: can be negative or positive
        :param t_hi_minutes: can be negative or positive, but must be greater than t_lo_minutes.
        :return: the file whose time label is within the range (timestamp + t_lo_minutes, timestamp + t_hi_minutes).
        If more than one, return the first occurrence.
        """

        if t_hi_minutes <= t_lo_minutes:
            raise ValueError('t_hi_minutes must be greater than t_lo_minutes')

        t_lo = timestamp + datetime.timedelta(minutes=t_lo_minutes).seconds
        t_hi = timestamp + datetime.timedelta(minutes=t_hi_minutes).seconds

        m_idx = np.where(np.logical_and(self.ftimes[:, 0] >= t_lo, self.ftimes[:, 0] < t_hi))[0]
        if len(m_idx) > 0:
            m_idx = m_idx[0]  # the first occurrence
            return self.flist[m_idx], self.ftimes[m_idx, 0], m_idx
        else:
            return None, None, None

    def get_parameters(self):
        pass

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < len(self.flist):
            fname = self.flist[self._current_index]
            t_start = self.ftimes[self._current_index, 0]
            t_stop = self.ftimes[self._current_index, 1]
            dto = self.dto_s[self._current_index]
            self._current_index += 1
            return fname, t_start, t_stop, dto

        self._current_index = 0
        raise StopIteration


class CrIS_Retrieval(Files):
    def __init__(self, files_path, file_time_span=8, pattern='CrIS_*atm_prof_rtv.h5'):
        super().__init__(files_path, file_time_span, pattern)

    def get_datetime(self, pathname):
        filename = os.path.split(pathname)[1]
        dt_str = re.search('_d.{14}', filename).group(0)
        dto = datetime.datetime.strptime(dt_str, '_d%Y%m%d_t%H%M').replace(tzinfo=timezone.utc)
        return dto


class ATMS_MIRS(Files):
    def __init__(self, files_path, file_time_span=8, pattern='NPR-MIRS-SND*.nc'):
        super().__init__(files_path, file_time_span, pattern)

    def get_datetime(self, pathname):
        filename = os.path.split(pathname)[1]
        dt_str = re.search('_s.{12}', filename).group(0)
        dto = datetime.datetime.strptime(dt_str, '_s%Y%m%d%H%M').replace(tzinfo=timezone.utc)
        return dto
