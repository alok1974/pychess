import re


from .. import constant as c


class Square:
    x_map = dict(
        [
            (i, 'abcdefgh'[i])
            for i in range(8)
        ]
    )
    y_map = dict(
        [
            (i, str(i + 1))
            for i in range(8)
        ]
    )

    __slots__ = (
        '_x',
        '_y',
        '_x_addr',
        '_y_addr',
    )

    def __init__(self, address):
        is_tuple, x_val, y_val = self._parse_address(address)
        if is_tuple:
            self._x = x_val
            self._y = y_val
            self._x_addr = self.x_map[self._x]
            self._y_addr = self.y_map[self._y]
        else:
            self._x_addr = x_val
            self._y_addr = y_val
            self._x = self._coord_from_address(x_val, map_to_use=self.x_map)
            self._y = self._coord_from_address(y_val, map_to_use=self.y_map)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def x_address(self):
        return self._x_addr

    @property
    def y_address(self):
        return self._y_addr

    @property
    def address(self):
        return f'{self.x_address}{self.y_address}'

    def _parse_address(self, address):
        is_tuple = True
        x_val = None
        y_val = None

        if isinstance(address, tuple):
            error_msg_1 = (
                'Expected address as tuple of length of 2, '
                f'recieved address={address}'
            )
            if len(address) != 2:
                raise ValueError(error_msg_1)

            x_val, y_val = address

            error_msg_2 = (
                'x and y should be a number from 0 to 7, '
                f'given x={x_val}, y={y_val}'
            )
            if x_val not in range(8) or y_val not in range(8):
                raise ValueError(error_msg_2)
        elif isinstance(address, str):
            error_msg_3 = (
                f'The given address={address} is invalid, '
                'it should be a string of the form '
                '\'<alpha><number>\' where <alpha> is one of '
                '\'abcdefgh\' and <number> is from 1 to 8, example '
                '\'a5\', \'h4\' etc.'
            )
            mo = re.match(c.GAME.ADDRESS_PATTERN, address)
            if mo is None:
                raise ValueError(error_msg_3)

            x_val, y_val = mo.groups()
            is_tuple = False
        else:
            error_msg_4 = (
                f'The given address={address} is invalid, '
                'it should either be a tuple like (0, 5) '
                'where each elements of tuple is a number from 0 to 7 or '
                'it should be a string of the form '
                '\'<alpha><number>\' where <alpha> is one of '
                '\'abcdefgh\' and <number> is from 1 to 8, example '
                '\'a5\', \'h4\' etc.'
            )
            raise ValueError(error_msg_4)

        return is_tuple, x_val, y_val

    def _coord_from_address(self, address, map_to_use):
        keys_for_addr = [k for k, v in map_to_use.items() if v == address]
        if not keys_for_addr:
            error_msg = f'Cannot find keys for address \'{address}\''
            raise ValueError(error_msg)

        assert(len(keys_for_addr) == 1)
        return keys_for_addr[0]

    def __hash__(self):
        return (10 * self.x) + self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __neq__(self, other):
        return self.x != other.x or self.y != other.y

    def __gt__(self, other):
        return hash(self) > hash(other)

    def __lt__(self, other):
        return hash(self) < hash(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __le__(self, other):
        return self.__eq__(other) or self.__le__(other)

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'<{class_name}: {self.address}>'
