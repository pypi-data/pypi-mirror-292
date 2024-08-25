from collections.abc import Sequence


class FrozenByteList(Sequence):
    def __init__(self, input_bytes, getter=None):
        self._data = input_bytes
        self.getter = getter
        self.element_count = int.from_bytes(input_bytes[:4], 'big')

    @classmethod
    def create(cls, byte_strings: list):
        num_elements = len(byte_strings)
        offsets = [0]
        for byte_string in byte_strings:
            offsets.append(offsets[-1] + len(byte_string))
        serialized_data = bytearray()
        serialized_data += num_elements.to_bytes(4, 'big')
        for offset in offsets:
            serialized_data += offset.to_bytes(4, 'big')
        for byte_string in byte_strings:
            serialized_data += byte_string
        return cls(bytes(serialized_data))

    def __len__(self):
        return self.element_count

    def get_offset(self, i: int):
        return int.from_bytes(
            self._data[4+i*4:4+((i+1)*4)], 'big')

    def __getitem__(self, index: int):
        if index < 0 or index >= self.element_count:
            raise IndexError('Invalid index %d' % index)
        start = self.get_offset(index)
        end = self.get_offset(index+1)
        data_start = self.element_count * 4 + 8
        element = self._data[data_start+start:data_start+end]
        if self.getter is None:
            return element
        return self.getter(element)

    def data(self):
        return self._data


def cached_binary_searcher(arr, cache_depth=8):
    cache = {}

    def binary_search(target):
        left = 0
        right = len(arr) - 1
        depth = 0
        while left <= right:
            mid = (left + right) // 2
            if depth < cache_depth:
                depth += 1
                current = cache.get(mid)
                if current is None:
                    current = arr[mid]
                    cache[mid] = current
            else:
                current = arr[mid]
            if current == target:
                return mid
            elif current < target:
                left = mid + 1
            else:
                right = mid - 1
        return None
    return binary_search


class ShapeUnifier():
    def __init__(self, records):
        self.data_shape = self.determine_shape(records)

    def __call__(self, record):
        return self.apply_shape(record, self.data_shape)

    @staticmethod
    def determine_shape(records):
        def promote_type(t1, t2):
            """Promote types: int < float < str"""
            if t1 == t2:
                return t1
            if {t1, t2} == {int, float}:
                return float
            return str

        def analyze_element(element, current_shape):
            if isinstance(element, list) or isinstance(element, tuple):
                current_type = list if isinstance(element, list) else tuple
                shape = current_shape or (current_type, [None] * len(element))
                for i, sub_elem in enumerate(element):
                    if i >= len(shape[1]):
                        shape[1].append(None)
                    shape[1][i] = analyze_element(sub_elem, shape[1][i])
                return shape
            return promote_type(current_shape, type(element)) if current_shape else type(element)

        shape = None
        for record in records:
            if not isinstance(record, (list, tuple)):
                record = (record,)
            shape = analyze_element(record, shape)

        return shape

    @staticmethod
    def apply_shape(record, shape):
        def default_value(t):
            if isinstance(t, type):
                return t()

        def convert_type(value, target_type):
            try:
                return target_type(value)
            except (ValueError, TypeError):
                return default_value(target_type)

        def shape_element(element, target_shape):
            if isinstance(target_shape, tuple):
                target_type, sub_shapes = target_shape
                element = list(element) if isinstance(element, (list, tuple)) else [element]
                shaped_elements = [
                    shape_element(element[i] if i < len(element) else default_value(sub_shapes[i]), sub_shapes[i])
                    for i in range(len(sub_shapes))
                ]
                return shaped_elements if target_type == list else tuple(shaped_elements)
            return convert_type(element, target_shape)

        if not isinstance(record, (list, tuple)):
            record = [record]
        return shape_element(record, shape)
