# ActivitySim
# See full license in LICENSE.txt.

import numpy as np
import pandas as pd
import numpy.testing as npt
import pandas.testing as pdt
import pytest

from .. import skim


@pytest.fixture
def data():
    return np.arange(100, dtype='int').reshape((10, 10))


def test_basic(data):
    sk = skim.SkimWrapper(data)

    orig = [5, 9, 1]
    dest = [2, 9, 6]

    npt.assert_array_equal(
        sk.get(orig, dest),
        [52, 99, 16])


def test_offset_int(data):
    sk = skim.SkimWrapper(data, skim.OffsetMapper(-1))

    orig = [6, 10, 2]
    dest = [3, 10, 7]

    npt.assert_array_equal(
        sk.get(orig, dest),
        [52, 99, 16])


def test_offset_list(data):

    offset_mapper = skim.OffsetMapper()
    offset_mapper.set_offset_list([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # should have figured out it could use an int offset instead of list
    assert offset_mapper.offset_int == -1

    offset_mapper = skim.OffsetMapper()
    offset_mapper.set_offset_list([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    sk = skim.SkimWrapper(data, offset_mapper)

    orig = [60, 100, 20]
    dest = [30, 100, 70]

    npt.assert_array_equal(
        sk.get(orig, dest),
        [52, 99, 16])


# fixme - nan support disabled in skim.py (not sure we need it?)
# def test_skim_nans(data):
#     sk = skim.SkimWrapper(data)
#
#     orig = [5, np.nan, 1, 2]
#     dest = [np.nan, 9, 6, 4]
#
#     npt.assert_array_equal(
#         sk.get(orig, dest),
#         [np.nan, np.nan, 16, 24])


def test_skims(data):

    skims_shape = data.shape + (2,)

    skim_data = np.zeros(skims_shape, dtype=data.dtype)
    skim_data[:, :, 0] = data
    skim_data[:, :, 1] = data*10

    skim_info = {
        'block_offsets': {'AM': (0, 0), 'PM': (0, 1)}
    }

    skim_dict = skim.SkimDict([skim_data], skim_info)

    skims = skim_dict.wrap("taz_l", "taz_r")

    df = pd.DataFrame({
        "taz_l": [1, 9, 4],
        "taz_r": [2, 3, 7],
    })

    skims.set_df(df)

    pdt.assert_series_equal(
        skims["AM"],
        pd.Series(
            [12, 93, 47],
            index=[0, 1, 2]
        ).astype(data.dtype)
    )

    pdt.assert_series_equal(
        skims["PM"],
        pd.Series(
            [120, 930, 470],
            index=[0, 1, 2]
        ).astype(data.dtype)
    )


def test_3dskims(data):

    skims_shape = data.shape + (2,)

    skim_data = np.zeros(skims_shape, dtype=int)
    skim_data[:, :, 0] = data
    skim_data[:, :, 1] = data*10

    skim_info = {
        'block_offsets': {('SOV', 'AM'): (0, 0), ('SOV', 'PM'): (0, 1)},
        'key1_block_offsets': {'SOV': (0, 0)}
    }
    skim_dict = skim.SkimDict([skim_data], skim_info)

    stack = skim.SkimStack(skim_dict)

    skims3d = stack.wrap(left_key="taz_l", right_key="taz_r", skim_key="period")

    df = pd.DataFrame({
        "taz_l": [1, 9, 4],
        "taz_r": [2, 3, 7],
        "period": ["AM", "PM", "AM"]
    })

    skims3d.set_df(df)

    pdt.assert_series_equal(
        skims3d["SOV"],
        pd.Series(
            [12, 930, 47],
            index=[0, 1, 2]
        ),
        check_dtype=False
    )
