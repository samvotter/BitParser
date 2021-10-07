# Python imports
import operator


# todo potential good use cases for dataclasses
class Biterator:

    def __init__(self, data: bytes):
        """
        Brief:
            An iterator which returns the bits associated with each byte in a bytearray

        Params:
            data: an array of bytes
        """
        self.data = data
        self.size = len(data)
        self.index = 0

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        idx = self.index
        if idx >= self.size:
            raise StopIteration
        self.index += 1
        bin_val = bin(self.data[idx])[2:]
        return "0" * (8 - len(bin_val)) + bin_val

    @classmethod
    def generator(cls, byte_string):
        """
        Brief:
            A generator yielding the binary data associated with a bytearray
        """
        for byte_val in byte_string:
            bin_val = bin(byte_val)[2:]
            yield "0" * (8 - len(bin_val)) + bin_val


class BitField:

    def __init__(self, size: int, name: str = "", value: int = 0):
        self.__size = size
        self.__name = name
        self._value = value

    def __int__(self):
        return self.value

    def __index__(self):
        """
        Brief:
            Enables type conversions such as __hex__
        """
        return operator.index(int(self))

    def __str__(self):
        return f"{self.name}:\t{self.value}"

    def __bytes__(self):
        """
        Creates a bytearray of the appropriate size. Unclear what this might be used for.
        """
        intVal = int(self)
        bytes_needed, rem = divmod(self.size, 8)
        if rem:
            bytes_needed += 1
        return intVal.to_bytes(bytes_needed, 'big')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if len(bin(new_value)[2:]) > self.size:
            raise ValueError(f"{new_value} is too large for the field size: {self.size} bits")
        self._value = new_value

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        raise AttributeError("name field cannot be modified")

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, new_size):
        raise AttributeError("size field cannot be modified")

    def to_dict(self):
        return {self.name: self.value}

    def to_bin(self):
        """
        __bin__ cannot be overloaded in the same way as other methods. Treat this function as if you could.
        """
        binStr = bin(self.value)[2:]
        while len(binStr) < self.size:
            binStr = '0' + binStr
        return binStr


class BitStruct:

    def __init__(self, bitfields: list[BitField], name: str = ""):
        self.__fields = bitfields
        self.__name = name
        self.__size = sum([field.size for field in bitfields])
        self.__idx = 0

    def __str__(self):
        print_width = max([len(field.name) for field in self.fields])
        retStr = f"\t{self.name}:\n"
        for field in self.fields:
            padding = " " * (print_width - len(field.name) + 4)
            retStr += f"\t\t{field.name}:{padding}{field.value}\n"
        return retStr

    def __int__(self):
        binstr = self.to_bin()
        return int(binstr, 2)

    def __index__(self):
        """
        Brief:
            Enables type conversions such as __hex__
        """
        return operator.index(int(self))

    def __bytes__(self):
        """
        Creates a bytearray of the appropriate size. Unclear what this might be used for.
        """
        intVal = int(self)
        bytes_needed, rem = divmod(self.size, 8)
        if rem:
            bytes_needed += 1
        return intVal.to_bytes(bytes_needed, 'big')

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        idx = self.idx
        if idx >= len(self.fields):
            raise StopIteration
        self.__idx += 1
        return self.fields[idx]

    def __getitem__(self, item):
        return self.fields[item]

    @property
    def fields(self):
        return self.__fields

    @fields.setter
    def fields(self, new_val):
        raise AttributeError("Cannot modify BitStruct's fields")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_val):
        raise AttributeError("Cannot modify BitStruct's name")

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, new_val):
        raise AttributeError("Cannot modify BitStruct's size")

    @property
    def idx(self):
        return self.__idx

    @idx.setter
    def idx(self, new_value):
        raise AttributeError("Cannot modify BitStruct's index")

    def to_bin(self):
        retStr = ""
        for field in self.fields:
            binStr = bin(field.value)[2:]
            while len(binStr) < field.size:
                binStr = '0' + binStr
            retStr += binStr
        return retStr

    def to_dict(self):
        return {self.name: {field.name: field.value for field in self}}

    def from_bin(self, binstring: str = ""):
        """
        This class is meant to represent a struct of bit fields. It requires bits to populate.
        """
        if binstring.startswith("0b"):
            binstring = binstring[2:]

        if len(binstring) < self.size:
            raise ValueError("Not enough bins to fill the BitStruct")

        for field in self.fields:
            int_val = int(binstring[:field.size], 2)
            field.value = int_val
            binstring = binstring[field.size:]

    def from_bytes(self, bytestring: bytes):
        """
        Populates the bit struct from a bytearray
        """
        if len(bytestring) < self.size // 8:
            raise ValueError("Not enough bytes to fill the BitStruct")

        data = Biterator(bytestring)
        available_bins = next(data)

        for field in self.fields:
            while len(available_bins) < field.size:
                available_bins += next(data)
            int_val = int(available_bins[:field.size], 2)
            field.value = int_val
            available_bins = available_bins[field.size:]


class BitCollection:
    """
    A BitCollection is defined as an ordered collection of BitStructs
    """

    def __init__(self, bitstructs: list[BitStruct], name: str = ""):
        self.__structs = bitstructs
        self.__name = name
        self.__size = sum([struct.size for struct in self.structs])
        self.__idx = 0

    def __iter__(self):
        self.__idx = 0
        return self

    def __next__(self):
        idx = self.idx
        if idx >= len(self.structs):
            raise StopIteration
        self.__idx += 1
        return self.structs[idx]

    def __str__(self):
        retStr = f"{self.name}:\n"
        for struct in self.structs:
            retStr += str(struct)
        return retStr

    def __int__(self):
        binstr = self.to_bin()
        return int(binstr, 2)

    def __bytes__(self):
        intVal = int(self)
        bytes_needed, rem = divmod(self.size, 8)
        if rem:
            bytes_needed += 1
        # int.to_bytes requires a byteorder param
        return intVal.to_bytes(bytes_needed, byteorder='big')

    def __index__(self):
        """
        Brief:
            Enables type conversions such as __hex__
        """
        return operator.index(int(self))

    def __len__(self):
        return len(self.structs)

    def __getitem__(self, item):
        return self.structs[item]

    @property
    def structs(self):
        return self.__structs

    @structs.setter
    def structs(self, new_value):
        raise AttributeError(f"Cannot modify BitCollection's substructs")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_value):
        raise AttributeError("Cannot modify BitCollection's name")

    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, new_value):
        raise AttributeError("Cannot modify BitCollection's size")

    @property
    def idx(self):
        return self.__idx

    @idx.setter
    def idx(self, new_value):
        raise AttributeError("Cannot modify BitCollection's index")

    def to_bin(self):
        binstr = ""
        for struct in self.structs:
            binstr += struct.to_bin()
        return binstr

    def to_dict(self):
        """
        Creates a dictionary representation of the struct.

        It's possible that a BitCollection might contain multiple structs
        of the same name.
        """
        return {
            self.name: [
                struct.to_dict() for struct in self
            ]
        }

    def from_bin(self, binstring: str):
        """
        Because this is a collection of bit structs it does make sense that someone
        might want to populate it with bits rather than bytes.
        """
        if binstring.startswith("0b"):
            binstring = binstring[2:]

        if len(binstring) < self.size:
            raise ValueError("Not enough bins to fill the BitCollection")

        for struct in self.structs:
            struct.from_bin(binstring[:struct.size])
            binstring = binstring[struct.size:]

    def from_bytes(self, bytestring: bytes):
        if len(bytestring) < self.size // 8:
            raise ValueError("Not enough bytes to fill the BitCollection")

        data = Biterator(bytestring)
        available_bins = next(data)

        for struct in self.structs:
            while len(available_bins) < struct.size:
                available_bins += next(data)
            struct.from_bin(available_bins[:struct.size])
            available_bins = available_bins[struct.size:]


class FlitStruct(BitCollection):

    def __init__(self, bitstructs: list[BitStruct], name: str = ""):
        super().__init__(bitstructs=bitstructs, name=name)
        if self.size != 128:
            raise ValueError(f"FlitStructs MUST be 128 bits, was {self.size}")
