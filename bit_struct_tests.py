# External Dependencies
import pytest

# Package imports
from BitS import (
    Biterator,
    BitField,
    BitStruct,
    BitCollection,
    FlitStruct
)

# Test Data
CHECKERBOARD_BYTES = bytearray(b"\xAA\x55"*8)
CHECKERBOARD_BITS = "0b" + "1010101001010101" * 8
"""
CHECKERBOARD_BITS should look like this in a bit map:

    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    
    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    
    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    
    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    1 0 1 0  1 0 1 0
    0 1 0 1  0 1 0 1
    
"""


# Test Structs
class BYTE_ALIGNED_32BIT_STRUCT(BitStruct):

    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=4,    name="Apple"),
                BitField(size=4,    name="Banana"),
                BitField(size=8,    name="Carrot"),
                BitField(size=16,   name="Durian")
            ], name="Byte Aligned 32bit Struct"
        )


class NON_BYTE_ALIGNED_27BIT_STRUCT(BitStruct):

    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=7, name="Elderberry"),
                BitField(size=5, name="Fig"),
                BitField(size=2, name="Grapefruit"),
                BitField(size=13, name="Honeydew")
            ],
            name="Non Byte Aligned 27bit Struct"
        )


class OVERLAPPING_BOUNDARY_STRUCT(BitStruct):

    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=20, name="Jackfruit"),
                BitField(size=30, name="Kumquat"),
                BitField(size=20, name="Lemon")
            ],
            name="Overlapping BitFields"
        )


# specifically sized structs
class EIGHT_BIT_STRUCT(BitStruct):
    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=2, name="OMG"),
                BitField(size=1, name="OHLAWD"),
                BitField(size=5, name="HE COMIN'!")
            ], name="8 bits"
        )


class TEN_BIT_STRUCT(BitStruct):
    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=3, name="Apple"),
                BitField(size=4, name="Banana"),
                BitField(size=3, name="Carrot")
            ], name="10 bits"
        )


class FIFTEEN_BIT_STRUCT(BitStruct):
    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=7, name="Durian"),
                BitField(size=8, name="Elderberry"),
            ], name="15 bits"
        )


class TWENTY_BIT_STRUCT(BitStruct):
    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=14, name="Fig"),
                BitField(size=2, name="Grapefruit"),
                BitField(size=4, name="Honeydew")
            ], name="20 bits"
        )


class THIRTY_BIT_STRUCT(BitStruct):
    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=14, name="Jackfruit"),
                BitField(size=5,  name="Kumquat"),
                BitField(size=11, name="Lemon")
            ], name="30 bits"
        )


class FOURTY_BIT_STRUCT(BitStruct):
    def __init__(self):
        super().__init__(
            bitfields=[
                BitField(size=7, name="Mango"),
                BitField(size=13, name="Nugget"),
                BitField(size=15, name="Orange"),
                BitField(size=5, name="Pear")
            ], name="40 bits"
        )


# ============================= Biterator Tests =============================
@pytest.mark.parametrize(
    "bytedata, expected_iterations, expected_output", [
        (CHECKERBOARD_BYTES, 16, CHECKERBOARD_BITS[2:]),
        (bytearray(b""), 0, "")
    ]
)
def test_Biterator_outputs_bins(bytedata, expected_iterations, expected_output):
    test_str = ""
    iterations = 0
    for available_bins in Biterator(bytedata):
        test_str += available_bins
        iterations += 1
    assert iterations == expected_iterations
    assert test_str == expected_output


def test_Biterator_throws_on_empty_next():
    data = Biterator(bytearray(b""))
    try:
        next(data)
        assert False
    except StopIteration:
        assert True


@pytest.mark.parametrize(
    "bytestring, expected", [
        (b"\xFF\x00", ["11111111", "00000000"]),
        (b"\xAA\x55", ["10101010", "01010101"]),
        (b"\x01", ["00000001"]),
        (b"\x01\x02\x03", ["00000001", "00000010", "00000011"]),
        (b"\xF0" * 100, ["11110000"]*100)
    ]
)
def test_Biterator_generates(bytestring, expected):
    # generator is a classmethod and does not need to be instantiated
    idx = 0
    for bins in Biterator.generator(bytestring):
        assert bins == expected[idx]
        idx += 1


# ============================= BitField Tests =============================
@pytest.mark.parametrize(
    "bitfield, expected", [
        # small and simple
        (BitField(size=1,    name="Apple",           value=0), "0"),
        (BitField(size=2,    name="Banana",          value=1), "01"),
        (BitField(size=3,    name="Carrot",          value=2), "010"),
        (BitField(size=4,    name="Durian",          value=3), "0011"),

        # somewhat larger
        (BitField(size=8,    name="Elderberry",      value=128), "10000000"),
        (BitField(size=9,    name="Fig",             value=255), "011111111"),
        (BitField(size=10,   name="Grapefruit",      value=37),  "0000100101"),
        (BitField(size=11,   name="Honeydew",        value=177), "00010110001"),

        # whacky
        (BitField(size=47,   name="Jackfruit",       value=2314286), "00000000000000000000000001000110101000000101110"),
        (BitField(size=21,   name="Kumquat",         value=98765),   "000011000000111001101"),
        (BitField(size=30,   name="Lemon",           value=6),       "000000000000000000000000000110"),
        (BitField(size=17,   name="Mango",           value=111111),  "11011001000000111")
    ]
)
def test_BitField_outputs_valid_bin(bitfield, expected):
    assert bitfield.to_bin() == expected


@pytest.mark.parametrize(
    "bitfield, expected", [
        # small and simple
        (BitField(size=1,    name="Apple",           value=0), b"\x00"),
        (BitField(size=2,    name="Banana",          value=1), b"\x01"),
        (BitField(size=3,    name="Carrot",          value=2), b"\x02"),
        (BitField(size=4,    name="Durian",          value=3), b"\x03"),

        # somewhat larger
        (BitField(size=8,    name="Elderberry",      value=128), b"\x80"),
        (BitField(size=9,    name="Fig",             value=255), b"\x00\xFF"),
        (BitField(size=10,   name="Grapefruit",      value=37),  b"\x00\x25"),
        (BitField(size=11,   name="Honeydew",        value=177), b"\x00\xB1"),

        # whacky
        (BitField(size=47,   name="Jackfruit",       value=2314286), b"\x00\x00\x00\x23\x50\x2E"),
        (BitField(size=21,   name="Kumquat",         value=98765),   b"\x01\x81\xCD"),
        (BitField(size=30,   name="Lemon",           value=6),       b"\x00\x00\x00\x06"),
        (BitField(size=17,   name="Mango",           value=111111),  b"\01\xB2\x07")
    ]
)
def test_BitField_outputs_valid_bytes(bitfield, expected):
    assert bytes(bitfield) == expected


@pytest.mark.parametrize(
    "bitfield, expected_int, expected_hex", [
        # small and simple
        (BitField(size=1,    name="Apple",           value=0), 0, "0x0"),
        (BitField(size=2,    name="Banana",          value=1), 1, "0x1"),
        (BitField(size=3,    name="Carrot",          value=2), 2, "0x2"),
        (BitField(size=4,    name="Durian",          value=3), 3, "0x3"),

        # somewhat larger
        (BitField(size=8,    name="Elderberry",      value=128), 128, "0x80"),
        (BitField(size=9,    name="Fig",             value=255), 255, "0xff"),
        (BitField(size=10,   name="Grapefruit",      value=37),  37, "0x25"),
        (BitField(size=11,   name="Honeydew",        value=177), 177, "0xb1"),

        # whacky
        (BitField(size=47,   name="Jackfruit",       value=2314286), 2314286, "0x23502e"),
        (BitField(size=21,   name="Kumquat",         value=98765),   98765, "0x181cd"),
        (BitField(size=30,   name="Lemon",           value=6),       6, "0x6"),
        (BitField(size=17,   name="Mango",           value=111111),  111111, "0x1b207")
    ]
)
def test_BitField_converts_to_int_hex(bitfield, expected_int, expected_hex):
    assert int(bitfield) == expected_int
    assert hex(bitfield) == expected_hex


@pytest.mark.parametrize(
    "bitfield, expected_str", [
        # small and simple
        (BitField(size=1,    name="Apple",           value=0), "Apple:\t0"),
        (BitField(size=2,    name="Banana",          value=1), "Banana:\t1"),
        (BitField(size=3,    name="Carrot",          value=2), "Carrot:\t2"),
        (BitField(size=4,    name="Durian",          value=3), "Durian:\t3"),

        # somewhat larger
        (BitField(size=8,    name="Elderberry",      value=128), "Elderberry:\t128"),
        (BitField(size=9,    name="Fig",             value=255), "Fig:\t255"),
        (BitField(size=10,   name="Grapefruit",      value=37),  "Grapefruit:\t37"),
        (BitField(size=11,   name="Honeydew",        value=177), "Honeydew:\t177"),

        # whacky
        (BitField(size=47,   name="Jackfruit",       value=2314286), "Jackfruit:\t2314286"),
        (BitField(size=21,   name="Kumquat",         value=98765),   "Kumquat:\t98765"),
        (BitField(size=30,   name="Lemon",           value=6),       "Lemon:\t6"),
        (BitField(size=17,   name="Mango",           value=111111),  "Mango:\t111111")
    ]
)
def test_BitField_converts_to_str(bitfield, expected_str):
    assert str(bitfield) == expected_str


@pytest.mark.parametrize(
    "bitfield, expected_dict", [
        # small and simple
        (BitField(size=1,    name="Apple",           value=0), {"Apple": 0}),
        (BitField(size=2,    name="Banana",          value=1), {"Banana": 1}),
        (BitField(size=3,    name="Carrot",          value=2), {"Carrot": 2}),
        (BitField(size=4,    name="Durian",          value=3), {"Durian": 3}),

        # somewhat larger
        (BitField(size=8,    name="Elderberry",      value=128), {"Elderberry": 128}),
        (BitField(size=9,    name="Fig",             value=255), {"Fig": 255}),
        (BitField(size=10,   name="Grapefruit",      value=37),  {"Grapefruit": 37}),
        (BitField(size=11,   name="Honeydew",        value=177), {"Honeydew": 177}),

        # whacky
        (BitField(size=47,   name="Jackfruit",       value=2314286), {"Jackfruit": 2314286}),
        (BitField(size=21,   name="Kumquat",         value=98765),   {"Kumquat": 98765}),
        (BitField(size=30,   name="Lemon",           value=6),       {"Lemon": 6}),
        (BitField(size=17,   name="Mango",           value=111111),  {"Mango": 111111})
    ]
)
def test_BitField_converts_to_dict(bitfield, expected_dict):
    assert bitfield.to_dict() == expected_dict


@pytest.mark.parametrize(
    "bitfield, setval", [
        # small and simple
        (BitField(size=1, name="Apple"),    2),
        (BitField(size=2, name="Banana"),   4),
        (BitField(size=3, name="Carrot"),   8),
        (BitField(size=4, name="Durian"),   16),

        # somewhat larger
        (BitField(size=8, name="Elderberry"),   256),
        (BitField(size=9, name="Fig"),          512),
        (BitField(size=10, name="Grapefruit"),  1024),
        (BitField(size=11, name="Honeydew"),    2048),

        # whacky
        (BitField(size=47, name="Jackfruit"),   140737488355328),
        (BitField(size=21, name="Kumquat"),     2097152),
        (BitField(size=30, name="Lemon"),       1073741824),
        (BitField(size=17, name="Mango"),       131072)
    ]
)
def test_BitField_throws_invalid_assignment(bitfield, setval):
    # each value should be too large for the field size
    try:
        bitfield.value = setval
        assert False
    except ValueError as err:
        assert str(err) == f"{setval} is too large for the field size: {bitfield.size} bits"
    # these properties should be immutable, will always throw
    try:
        bitfield.name = "TEST NAME"
        assert False
    except AttributeError as err:
        assert str(err) == "name field cannot be modified"
    try:
        bitfield.size = setval
    except AttributeError as err:
        assert str(err) == "size field cannot be modified"


# ============================= BitStruct Tests =============================
@pytest.mark.parametrize(
    "bitstruct, test_data, expected_values, expected_bins", [
        # sufficient bits
        (BYTE_ALIGNED_32BIT_STRUCT(),     CHECKERBOARD_BITS,  (10, 10, 85, 43605), "10101010010101011010101001010101"),
        (NON_BYTE_ALIGNED_27BIT_STRUCT(), CHECKERBOARD_BITS,  (85, 5, 1, 3410),    "101010100101010110101010010"),
        (OVERLAPPING_BOUNDARY_STRUCT(),   CHECKERBOARD_BITS,  (697690, 693545302, 693610), "1010101001010101101010100101010110101010010101011010101001010101101010"),

        # insufficent bits / should throw
        (BYTE_ALIGNED_32BIT_STRUCT(),     "1010101001010101",     False, None),
        (NON_BYTE_ALIGNED_27BIT_STRUCT(), "1010101001010101",     False, None),
        (OVERLAPPING_BOUNDARY_STRUCT(),   "1010101001010101",     False, None)

    ]
)
def test_BitStruct_outputs_from_binary(bitstruct, test_data, expected_values, expected_bins):
    try:
        bitstruct.from_bin(test_data)
        for idx, val in enumerate(expected_values):
            assert bitstruct[idx].value == val

        assert bitstruct.to_bin() == expected_bins
    except ValueError as err:
        assert str(err) == "Not enough bins to fill the BitStruct"


# converting a bit struct to a bytearray is often extremely misleading.
@pytest.mark.parametrize(
    "bitstruct, test_data, expected_values, expected_bytes", [
        # sufficient Bytes
        (BYTE_ALIGNED_32BIT_STRUCT(),     CHECKERBOARD_BYTES,       (10, 10, 85, 43605), b"\xAA\x55\xAA\x55"),
        (NON_BYTE_ALIGNED_27BIT_STRUCT(), CHECKERBOARD_BYTES,       (85, 5, 1, 3410),    b"\x05\x52\xAD\x52"),
        (OVERLAPPING_BOUNDARY_STRUCT(),   CHECKERBOARD_BYTES,       (697690, 693545302, 693610), b"\x2A\x95\x6A\x95\x6A\x95\x6A\x95\x6A"),

        # insufficent bytes / should throw
        (BYTE_ALIGNED_32BIT_STRUCT(),     b"\xAA\x55",     False, None),
        (NON_BYTE_ALIGNED_27BIT_STRUCT(), b"\xAA\x55",     False, None),
        (OVERLAPPING_BOUNDARY_STRUCT(),   b"\xAA\x55",     False, None)

    ]
)
def test_BitStruct_outputs_from_bytes(bitstruct, test_data, expected_values, expected_bytes):
    try:
        bitstruct.from_bytes(test_data)
        for idx, val in enumerate(expected_values):
            assert bitstruct[idx].value == val
        assert bytes(bitstruct) == expected_bytes
    except ValueError as err:
        assert str(err) == "Not enough bytes to fill the BitStruct"


# unclear why you would want to do this outside of an exercise in math
@pytest.mark.parametrize(
    "bitstruct, test_data, expected_int, expected_hex", [
        # sufficient Bytes
        (BYTE_ALIGNED_32BIT_STRUCT(),     CHECKERBOARD_BYTES,       2857740885, "0xaa55aa55"),
        (NON_BYTE_ALIGNED_27BIT_STRUCT(), CHECKERBOARD_BYTES,       89304402,    "0x552ad52"),
        (OVERLAPPING_BOUNDARY_STRUCT(),   CHECKERBOARD_BYTES,       785529833239989622122, "0x2a956a956a956a956a"),
    ]
)
def test_BitStruct_converts_to_int_hex(bitstruct, test_data, expected_int, expected_hex):
    bitstruct.from_bytes(test_data)
    assert int(bitstruct) == expected_int
    assert hex(bitstruct) == expected_hex


@pytest.mark.parametrize(
    "bitstruct, test_data, expected_values", [
        # sufficient Bytes
        (BYTE_ALIGNED_32BIT_STRUCT(),     CHECKERBOARD_BYTES,       (10, 10, 85, 43605)),
        (NON_BYTE_ALIGNED_27BIT_STRUCT(), CHECKERBOARD_BYTES,       (85, 5, 1, 3410)),
        (OVERLAPPING_BOUNDARY_STRUCT(),   CHECKERBOARD_BYTES,       (697690, 693545302, 693610)),
    ]
)
def test_BitStruct_converts_to_str(bitstruct, test_data, expected_values):
    empty_string = str(bitstruct)
    print_width = max([len(field.name) for field in bitstruct])
    assert f"\t{bitstruct.name}:\n" in empty_string
    for field in bitstruct:
        padding = " " * (print_width - len(field.name) + 4)
        assert f"{field.name}:{padding}0" in empty_string

    bitstruct.from_bytes(test_data)
    filled_string = str(bitstruct)
    assert f"\t{bitstruct.name}:\n" in filled_string
    for field in bitstruct:
        padding = " " * (print_width - len(field.name) + 4)
        assert f"{field.name}:{padding}{field.value}" in filled_string


@pytest.mark.parametrize(
    "bitstruct", [
        (BYTE_ALIGNED_32BIT_STRUCT()),
        (NON_BYTE_ALIGNED_27BIT_STRUCT()),
        (OVERLAPPING_BOUNDARY_STRUCT())
    ]
)
def test_BitStruct_throws_invalid_assignment(bitstruct):
    try:
        bitstruct.fields = 11
        assert False
    except AttributeError as err:
        assert str(err) == "Cannot modify BitStruct's fields"
    try:
        bitstruct.name = "TEST NAME"
        assert False
    except AttributeError as err:
        assert str(err) == "Cannot modify BitStruct's name"
    try:
        bitstruct.size = {"TEST KEY": "TEST VALUE"}
        assert False
    except AttributeError as err:
        assert str(err) == "Cannot modify BitStruct's size"
    try:
        bitstruct.idx = 0xFF
        assert False
    except AttributeError as err:
        assert str(err) == "Cannot modify BitStruct's index"


@pytest.mark.parametrize(
    "bitstruct, expected_bin", [
        (BYTE_ALIGNED_32BIT_STRUCT(),     "00010001000000010000000000000001"),
        (NON_BYTE_ALIGNED_27BIT_STRUCT(), "000000100001010000000000001"),
        (OVERLAPPING_BOUNDARY_STRUCT(),   "0000000000000000000100000000000000000000000000000100000000000000000001")
    ]
)
def test_BitStruct_supports_assignment_output(bitstruct, expected_bin):
    for field in bitstruct:
        field.value = 1
    assert bitstruct.to_bin() == expected_bin


# ============================= BitCollection Tests =============================
@pytest.mark.parametrize(
    "bitstructs, expected", [
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
            ], 128
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], 128
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT()
            ], 128
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ], 128
        ),
        (
            [
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ], 120
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                EIGHT_BIT_STRUCT(),
            ], 136
        )
    ]
)
def test_BitCollection_constructor_calculates_size(bitstructs, expected):
    testBitStruct = BitCollection(bitstructs=bitstructs)
    assert testBitStruct.size == expected


@pytest.mark.parametrize(
    "bitstructs", [
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
            ]
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ]
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT()
            ]
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ]
        ),
        (
            [
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ]
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                EIGHT_BIT_STRUCT(),
            ]
        )
    ]
)
def test_BitCollection_properties_throw_on_reassingment(bitstructs):
    testBitStruct = BitCollection(bitstructs=bitstructs)
    # each assignment should throw
    try:
        testBitStruct.structs = 9
        assert False
    except AttributeError:
        assert True
    try:
        testBitStruct.name = "Jolly good show!"
        assert False
    except AttributeError:
        assert True
    try:
        testBitStruct.size = b"\x06"
        assert False
    except AttributeError:
        assert True
    try:
        testBitStruct.idx = set()
        assert False
    except AttributeError:
        assert True


@pytest.mark.parametrize(
    "bitstructs, expected", [
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
            ], 7
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], 4
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT()
            ], 7
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ], 6
        ),
        (
            [
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ], 5
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                EIGHT_BIT_STRUCT(),
            ], 8
        )
    ]
)
def test_BitCollection_iterates(bitstructs, expected):
    test_BitCollection = BitCollection(bitstructs=bitstructs)
    iterations = 0
    for iteration in test_BitCollection:
        iterations += 1
    assert iterations == expected


@pytest.mark.parametrize(
    "bitstructs, bindata, expected", [
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
            ], CHECKERBOARD_BITS,
            (
                # 8 bits
                2, 1, 10,
                # 10 bits
                2, 10, 6,
                # 15 bits
                84, 171,
                # 15 bits
                42, 85,
                # 20 bits
                10901, 1, 10,
                # 30 bits
                10582, 21, 342,
                # 30 bits
                10837, 21, 597
            )
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], CHECKERBOARD_BITS,
            (
                # 8 bits
                2, 1, 10,
                # 40 bit
                42, 6821, 11602, 21,
                # 40 bit
                85, 1370, 21165, 10,
                # 40 bit
                42, 6821, 11602, 21
            )
        ),
        (
            # too small
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], bin(255),
            False
        )
    ]
)
def test_BitCollection_from_binary_valid_assignment(bitstructs, bindata, expected):
    testBitCollection = BitCollection(bitstructs=bitstructs)
    try:
        testBitCollection.from_bin(bindata)
        assert_idx = 0
        for struct in testBitCollection:
            for field in struct:
                assert field.value == expected[assert_idx]
                assert_idx += 1
    except ValueError as err:
        assert str(err) == "Not enough bins to fill the BitCollection"


@pytest.mark.parametrize(
    "bitstructs, bytedata, expected", [
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
            ], CHECKERBOARD_BYTES,
            (
                # 8 bits
                2, 1, 10,
                # 10 bits
                2, 10, 6,
                # 15 bits
                84, 171,
                # 15 bits
                42, 85,
                # 20 bits
                10901, 1, 10,
                # 30 bits
                10582, 21, 342,
                # 30 bits
                10837, 21, 597
            )
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], CHECKERBOARD_BYTES,
            (
                # 8 bits
                2, 1, 10,
                # 40 bit
                42, 6821, 11602, 21,
                # 40 bit
                85, 1370, 21165, 10,
                # 40 bit
                42, 6821, 11602, 21
            )
        ),
        (
            # too small
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], bytearray(b"\xFF"),
            False
        )
    ]
)
def test_BitCollection_from_bytes_valid_assignment(bitstructs, bytedata, expected):
    testBitCollection = BitCollection(bitstructs=bitstructs)
    try:
        testBitCollection.from_bytes(bytedata)
        assert_idx = 0
        for struct in testBitCollection:
            for field in struct:
                assert field.value == expected[assert_idx]
                assert_idx += 1
    except ValueError as err:
        assert str(err) == "Not enough bytes to fill the BitCollection"


@pytest.mark.parametrize(
    "bitstructs, test_data, expected_int, expected_hex", [
        (
            # small
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
            ],
            CHECKERBOARD_BYTES,
            174422,
            "0x2a956"
        ),
        (
            # byte aligned
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                EIGHT_BIT_STRUCT()
            ],
            CHECKERBOARD_BYTES,
            47944936110839210,
            "0xaa55aa55aa55aa"
        ),
        (
            # HUGE
            [
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ],
            CHECKERBOARD_BYTES,
            863699185612310821477349097564821,
            "0x2a956a956a956a956a956a956a95"
        )
    ]
)
def test_BitCollection_converts_to_int_hex(bitstructs, test_data, expected_int, expected_hex):
    test_collection = BitCollection(bitstructs=bitstructs, name="TEST")
    # initialized should be 0
    assert int(test_collection) == 0
    assert hex(test_collection) == "0x0"

    test_collection.from_bytes(test_data)
    assert int(test_collection) == expected_int
    assert hex(test_collection) == expected_hex


@pytest.mark.parametrize(
    "bitstructs, test_data, expected_bytes", [
        (
            # small
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
            ],
            CHECKERBOARD_BYTES,
            b"\x02\xA9\x56"
        ),
        (
            # byte aligned
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                EIGHT_BIT_STRUCT()
            ],
            CHECKERBOARD_BYTES,
            b"\xAA\x55\xAA\x55\xAA\x55\xAA"
        ),
        (
            # HUGE
            [
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ],
            CHECKERBOARD_BYTES,
            b"\x2A\x95\x6A\x95\x6A\x95\x6A\x95\x6A\x95\x6A\x95\x6A\x95"
        )
    ]
)
def test_BitCollection_converts_to_bytes(bitstructs, test_data, expected_bytes):
    test_collection = BitCollection(bitstructs=bitstructs, name="TEST")
    # initialized should be 0
    assert bytes(test_collection) == b"\x00" * (len(expected_bytes))

    test_collection.from_bytes(test_data)
    assert bytes(test_collection) == expected_bytes


@pytest.mark.parametrize(
    "bitstructs, test_data, expected_str", [
        (
            # small
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
            ],
            CHECKERBOARD_BYTES,
            (
                # 8 bit
                2, 1, 10,
                # 10 bit
                2, 10, 6
            ),
        ),
        (
            # byte aligned
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                EIGHT_BIT_STRUCT()
            ],
            CHECKERBOARD_BYTES,
            (
                # 8 bit
                2, 1, 10,
                # 40 bit
                42, 6821, 11602, 21,
                # 8 bit
                2, 1, 10
            ),
        ),
        (
            # HUGE
            [
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ],
            CHECKERBOARD_BYTES,
            (
                # 40 bit
                85, 1370, 21165, 10,
                # 40 bit
                42, 6821, 11602, 21,
                # 30 bit
                10901, 13, 661
            ),
        )
    ]
)
def test_BitCollection_converts_to_str(bitstructs, test_data, expected_str):
    test_collection = BitCollection(bitstructs=bitstructs, name="TEST")
    empty_str = str(test_collection)
    assert f"{test_collection.name}:\n" in empty_str
    for struct in test_collection:
        print_width = max([len(field.name) for field in struct])
        for field in struct:
            padding = " " * (print_width - len(field.name) + 4)
            # initialized should be 0
            assert f"\t\t{field.name}:{padding}0\n" in empty_str

    test_collection.from_bytes(test_data)
    filled_str = str(test_collection)
    assert f"{test_collection.name}:\n" in filled_str
    for struct in test_collection:
        print_width = max([len(field.name) for field in struct])
        for field in struct:
            padding = " " * (print_width - len(field.name) + 4)
            # with data should now be expected number
            assert f"\t\t{field.name}:{padding}{field.value}\n" in filled_str


@pytest.mark.parametrize(
    "bitstructs, bytedata, expected", [
        (
            # alternating 1s and 0s
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
            ], CHECKERBOARD_BYTES,
            (
                # 8 bits
                2, 1, 10,
                # 10 bits
                2, 10, 6,
                # 15 bits
                84, 171,
                # 15 bits
                42, 85,
                # 20 bits
                10901, 1, 10,
                # 30 bits
                10582, 21, 342,
                # 30 bits
                10837, 21, 597
            )
        ),
        (
            # just enough bytes of all zeros
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], CHECKERBOARD_BYTES,
            (
                # 8 bits
                2, 1, 10,
                # 40 bit
                42, 6821, 11602, 21,
                # 40 bit
                85, 1370, 21165, 10,
                # 40 bit
                42, 6821, 11602, 21
            )
        ),
    ]
)
def test_BitCollection_to_dict(bitstructs, bytedata, expected):
    # test collection should be initialized as all zeros
    testBitCollection = BitCollection(bitstructs=bitstructs, name="TEST")
    # make dictionary
    testDict = testBitCollection.to_dict()

    # the dictionary is keyed with the name
    assert testBitCollection.name in testDict
    # each struct is represented in the dictionary (no overwrites)
    assert len(testBitCollection) == len(testDict[testBitCollection.name])
    # order is preserved
    for i in range(len(testBitCollection)):
        assert testBitCollection[i].name in testDict[testBitCollection.name][i]
        # each field has the expected value (which should be 0)
        for field in testBitCollection[i]:
            assert field.value == 0 == testDict[testBitCollection.name][i][testBitCollection[i].name][field.name]

    # fill BitStructionCollection with actual data
    testBitCollection.from_bytes(bytedata)
    # remake dictionary
    testDict = testBitCollection.to_dict()

    # the dictionary is keyed with the name
    assert testBitCollection.name in testDict
    # each struct is represented in the dictionary (no overwrites)
    assert len(testBitCollection) == len(testDict[testBitCollection.name])
    # order is preserved
    for i in range(len(testBitCollection)):
        assert testBitCollection[i].name in testDict[testBitCollection.name][i]
        # each field has the expected value
        for field in testBitCollection[i]:
            assert field.value == testDict[testBitCollection.name][i][testBitCollection[i].name][
                field.name]


@pytest.mark.parametrize(
    "bitstructs, expected", [
        (
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
            ], True
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
            ], True
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                TWENTY_BIT_STRUCT()
            ], True
        ),
        (
            [
                EIGHT_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ], True
        ),
        (
            # too small
            [
                FIFTEEN_BIT_STRUCT(),
                FOURTY_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT()
            ], False
        ),
        (
            # too big
            [
                EIGHT_BIT_STRUCT(),
                TEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                FIFTEEN_BIT_STRUCT(),
                TWENTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                THIRTY_BIT_STRUCT(),
                EIGHT_BIT_STRUCT(),
            ], False
        )
    ]
)
def test_FlitStruct_must_be_128_bits(bitstructs, expected):
    try:
        FlitStruct(bitstructs=bitstructs, name="")
        assert expected
    except ValueError as err:
        assert f"FlitStructs MUST be 128 bits, was" in str(err)
        assert expected is False
