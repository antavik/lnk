import pytest

import utils

from constants import TimeUnit as TU, LNK


@pytest.mark.parametrize(
        "test_input, expected",
        [
            ('11d', (11, TU('days'))),
            ('22h', (22, TU('hours'))),
            ('33m', (33, TU('minutes'))),
            ('44s', (44, TU('seconds'))),
            ('00s', (0, TU('seconds'))),
            ('01s', (1, TU('seconds'))),
        ]
)
def test_parse_ttl__valid_inputes__valid_output(test_input, expected):
    assert utils.parse_ttl(test_input) == expected


@pytest.mark.parametrize("test_input", ['11 d', '22 sec', '0.1s'])
def test_parse_ttl__invalid_inputes__exception(test_input):
    with pytest.raises(ValueError):
        utils.parse_ttl(test_input)


@pytest.mark.parametrize(
        "test_input, expected",
        [
            ((11, TU('days')), 950400),
            ((22, TU('hours')), 79200),
            ((33, TU('minutes')), 1980),
            ((44, TU('seconds')), 44),
        ]
)
def test_calc_seconds__valid_inputes__valid_output(test_input, expected):
    assert utils.calc_seconds(*test_input) == expected


@pytest.mark.parametrize(
        "test_input",
        [
            (11, 'days'),
            (22, 'sec'),
        ]
)
def test_calc_seconds__invalid_inputes__exception(test_input):
    with pytest.raises(ValueError):
        utils.calc_seconds(*test_input)


def test_url_storage_key__string__string():
    test_input = 'test'
    result = utils.url_storage_key(test_input)

    assert result == f'{LNK}-u:{test_input}'


def test_clip_storage_key__string__string():
    test_input = 'test'
    result = utils.clip_storage_key(test_input)

    assert result == f'{LNK}-c:{test_input}'


def test_clip_task_name__string__string():
    test_input = 'test'
    result = utils.clip_task_name(test_input)

    assert result == f'clip_{test_input}'


@pytest.mark.parametrize(
        "test_input, expected",
        [
            ('t', True),
            ('f', False),
            ('true', True),
            ('false', False),
            ('1', True),
            ('0', False),
            ('yes', True),
            ('no', False),
            ('y', True),
            ('n', False),
            ('', False),
        ]
)
def test_str2bool___valid_inputes__valid_output(test_input, expected):
    assert utils.str2bool(test_input) == expected
    assert utils.str2bool(test_input.upper()) == expected


@pytest.mark.parametrize("test_input", ['yEs', 'False'])
def test_str2bool__invalid_inputes__exception(test_input):
    with pytest.raises(ValueError):
        utils.str2bool(test_input)
