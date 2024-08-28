# coding: utf-8

"""
module to define a standard tomography acquisition (made by bliss)
"""

import logging

from nxtomomill.converter.hdf5.acquisition.standardacquisition import (
    StandardAcquisition,
)

_logger = logging.getLogger(__name__)

__all__ = [
    "XRD3DAcquisition",
]


class XRD3DAcquisition(StandardAcquisition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rocking = None
        self._n_steps_rotation = []
        self._n_steps_rocking = 0

    @property
    def rocking(self):
        return self._rocking

    @rocking.setter
    def rocking(self, rocking):
        self._rocking = rocking

    @property
    def n_steps_rocking(self):
        return self._n_steps_rocking

    @n_steps_rocking.setter
    def n_steps_rocking(self, n_steps_rocking):
        self._n_steps_rocking = n_steps_rocking

    @property
    def n_steps_rotation(self):
        return self._n_steps_rotation

    @n_steps_rotation.setter
    def n_steps_rotation(self, n_steps_rotation):
        self._n_steps_rotation = n_steps_rotation

    def _get_rocking_dataset(self, entry, n_frames):
        for grp in self._get_positioners_node(entry), entry:
            try:
                rocking, unit = self._get_node_values_for_frame_array(
                    node=grp,
                    n_frame=n_frames,
                    keys=self.configuration.rocking_keys,
                    info_retrieve="rocking",
                    expected_unit=None,
                )
            except (ValueError, KeyError):
                pass
            else:
                return rocking, None

        _url_path = self.root_url.path() if self.root_url is not None else "?"
        mess = f"Unable to find rocking for {_url_path}"
        if self.raise_error_if_issue:
            raise ValueError(mess)
        else:
            mess += "default value will be set. (0)"
            _logger.warning(mess)
            return [0] * n_frames, None

    def _treate_valid_camera(
        self,
        detector_node,
        entry,
        frame_type,
        input_file_path,
        entry_path,
        entry_url,
    ):
        super()._treate_valid_camera(
            detector_node=detector_node,
            entry=entry,
            frame_type=frame_type,
            input_file_path=input_file_path,
            entry_path=entry_path,
            entry_url=entry_url,
        )
        # store rocking information
        rocking, _ = self._get_rocking_dataset(
            entry=entry, n_frames=self._current_scan_n_frame
        )
        self._rocking.extend(rocking)
        self._n_steps_rocking += 1
        self._n_steps_rotation += [self._current_scan_n_frame]

    def _preprocess_registered_entries(self):
        self._rocking = []
        super()._preprocess_registered_entries()

    def to_NXtomos(self, request_input, input_callback, check_tomo_n=True) -> tuple:
        nx_tomo = super().to_NXtomos(request_input, input_callback, check_tomo_n)[0]

        # define sample information for 3dxrd
        nx_tomo.sample.rocking = self.rocking
        nx_tomo.sample.n_steps_rocking = self.n_steps_rocking
        nx_tomo.sample.n_steps_rotation = self.n_steps_rotation
        return (nx_tomo,)
