from statute_utils import STYLES_NAMED, STYLES_SERIAL


def test_named_collection():
    for named in STYLES_NAMED:
        if named.matches:
            for sample in named.matches:
                assert named.pattern.fullmatch(sample)


def test_serial_collection():
    for serial in STYLES_SERIAL:
        if serial.matches:
            for sample in serial.matches:
                assert serial.pattern.fullmatch(sample)


# def test_named_and_dated_collection():
#     for named in STYLES_NAMED:
#         if named.options:
#             for option in named.options:
#                 if set_mini_statute_files_table():
#                     assert option.date
