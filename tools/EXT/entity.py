#!/usr/bin/env python
# encoding: utf-8


class Model:
    """
    json 转 实体类
    """
    def __init__(self, json):
        assert  type(json) == dict
        self.attr = []
        for key, value in json.iteritems():
            if type(value) == dict:
                model = Model(value)
                setattr(self, key, model)
                self.attr.append(key)
            else:
                setattr(self, key, Model.Value(value))
                self.attr.append(key)

    def __dir__(self):
        return self.attr

    class Value:
        def __init__(self, v):
            self.value = v

if __name__ == "__main__":
    json = {'whuifang': {'age': 19, 'name': 'whf'}, 'wshice': {'age': 18, 'name': 'wsc'}}
    model = Model(json)
    print model.wshice.age.value
