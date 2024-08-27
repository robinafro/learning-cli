from settings import DB_DIRECTORY
import os, json, uuid

def get_db_path(db_name):
    if not os.path.exists(DB_DIRECTORY):
        os.makedirs(DB_DIRECTORY)

    return os.path.join(DB_DIRECTORY, db_name + '.json')

def read(db_name, default={}):
    db_path = get_db_path(db_name)
    if not os.path.exists(db_path):
        with open(db_path, 'w') as f:
            json.dump(default, f)
        return default
    with open(db_path, 'r') as f:
        return json.load(f)
    
def save(db_name, data):
    db_path = get_db_path(db_name)
    with open(db_path, 'w') as f:
        json.dump(data, f)

class Model:
    def __init__(self, **kwargs):
        self.verify(**kwargs)
        self.set_data(**kwargs)
    
    def set_data(self, **kwargs):
        for key, value in self.Meta.fields.items():
            data = kwargs.get(key, value.default)
            if data is None:
                continue
            field = self.Meta.fields.get(key)
            self.__dict__.update({key: field.deserialize(data)})
        
        # if id doesnt exist (or empty), generate a new one
        if 'id' not in self.__dict__:
            self.__dict__.update({'id': str(uuid.uuid4())})

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}> {json.dumps(self.serialize(), indent=4)}"

    def verify(self, **kwargs):
        for key, value in kwargs.items():
            field = self.Meta.fields.get(key)
            assert field, f'Invalid field: {key}'
            field.verify(value)

    def serialize(self):
        def recursive_serialize(value):
            if isinstance(value, Model):
                return value.serialize()
            elif isinstance(value, list):
                return [recursive_serialize(item) for item in value]
            elif isinstance(value, dict):
                return {key: recursive_serialize(val) for key, val in value.items()}
            else:
                return value
        
        return {key: recursive_serialize(value) for key, value in self.__dict__.items() if key in self.Meta.fields}


    class Meta:
        fields = {}

class Field:
    def __init__(self, default=None):
        if default is not None:
            self.verify_value(default)

        self.default = default
    
    def verify_value(self, value):
        return True

    def verify_default(self):
        return getattr(self, 'default', None) is not None
    
    def verify(self, value):
        if value is None and self.verify_default():
            return
        elif not self.verify_value(value):
            raise ValueError(f'Invalid value: {value}')
        else:
            return True

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value
    
class StringField(Field):
    def verify_value(self, value):
        return isinstance(value, str)
    
class NumberField(Field):
    def verify_value(self, value):
        return isinstance(value, (int, float))
        
class BooleanField(Field):
    def verify_value(self, value):
        return isinstance(value, bool)

class OneToManyField(Field):
    def __init__(self, model):
        self.model = model
        self.default = None

    def verify_value(self, value):
        return all(isinstance(item, self.model) for item in value)

    def verify_default(self):
        return False

    def verify(self, value):
        if value is None:
            return

        if not self.verify_value(value):
            raise ValueError(f'Invalid value: {value}')

    def serialize(self, value):
        assert self.verify_value(value), f'Invalid value: {value}'
        
        return [item.serialize() if isinstance(item, Model) else item for item in value]

    def deserialize(self, data):
        return [self.model(**item) if isinstance(item, dict) else item for item in data]

    def __str__(self):
        return f'<ModelField: {self.model.__name__}>'