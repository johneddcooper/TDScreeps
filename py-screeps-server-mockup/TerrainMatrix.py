TYPES = ['plain', 'wall', 'swamp']

class Matrix:

    def __init__(self):
        self.data = dict()
    

    def get(self, x, y):
        if 0<=x<50 and 0<=y<50:
            return 'plain' if (x,y) not in self.data.keys() else self.data[(x,y)]
        raise Exception(f'value ({x},{y}) is out of bounds')
    def add(self, x, y, value):
        if 0<=x<50 and 0<=y<50:
            if value in TYPES:
                self.data[(x,y)]=value
            else:
                raise Exception(f'invalid value {value}')
        else:
            raise Exception(f'value ({x},{y}) is out of bounds')

    # Serialize / unserialize, just use JSON?
    def serialize(self):
        s = ''
        for y in range (0,50):
            for x in range(0,50):
                s += str(TYPES.index(self.get(x,y)))
        return s

def test_init_empty_matrix():
    assert len(Matrix().data) == 0

def test_add_valid_item():
    m = Matrix()
    m.add(0,0,'wall')
    assert len(m.data) == 1
    assert (0,0) in m.data.keys()
    assert m.data[(0,0)] == 'wall'

def test_add_invalid_item():
    m = Matrix()
    try:
        m.add(0,0,'zebra')
    except:
        assert True == True
    else:
        assert False == True, 'Error not thrown on invalid value'
    assert len(m.data) == 0

def test_get_valid_item():
    m = Matrix()
    m.add(0,0,'wall')
    assert m.get(0,0) == 'wall'

def test_get_invalid_item_returns_plain():
    m = Matrix()
    assert m.get(0,0) == 'plain'

def test_get_out_of_bounds_returns_error():
    m = Matrix()
    try:
        m.get(-1,-1, 'wall')
    except:
        pass
    else:
        assert False == True, "Error not thrown on out of bounds get"
    try:
        m.get(50,50, 'wall')
    except:
        pass
    else:
        assert False == True, "Error not thrown on out of bounds get"


def test_set_out_of_bounds_returns_error():
    m = Matrix()
    try:
        m.set(-1,-1, 'wall')
    except:
        pass
    else:
        assert False == True, "Error not thrown on out of bounds set"
    try:
        m.set(50,50, 'wall')
    except:
        pass
    else:
        assert False == True, "Error not thrown on out of bounds set"

def test_serializing_empty_matrix_all_plains():
    m = Matrix()
    s = m.serialize()
    assert s == '0'*2500

def test_serializing_populated_matrix():
    m = Matrix()
    m.add(0,0,'wall')
    m.add(0,1,'swamp')
    m.add(49,49,'wall')
    s = m.serialize()
    assert len(s) == 2500
    assert s[0] == str(TYPES.index('wall'))
    assert s[50] == str(TYPES.index('swamp'))
    assert s[2499] == str(TYPES.index('wall'))