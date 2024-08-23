import json
import os
from typing import List

from pydantic import BaseModel


class InstagramChange(BaseModel):
    field: str
    value: dict


class InstagramEvent(BaseModel):
    id: str
    time: int
    changes: List[InstagramChange]


class InstagramWebhook(BaseModel):
    entry: List[InstagramEvent]
    object: str

    def change_types(self):
        return list(set([change.field for event in self.entry for change in event.changes]))

    def get_changes(self):
        return [change for event in self.entry for change in event.changes]


if __name__ == '__main__':
    def test_parsing(current_file):
        print(f'--- Parsing {current_file} ---')
        f = open(current_file)
        data = json.load(f)
        obj = InstagramWebhook(**data)
        print(obj)
        print(obj.change_types())
        f.close()
        print(' ')
        print(obj.get_changes())
        print(' ')


    directory = '../../samples'

    for filename in os.listdir(directory):
        to_read_f = os.path.join(directory, filename)
        if os.path.isfile(to_read_f) and to_read_f.endswith('.json'):
            test_parsing(to_read_f)
