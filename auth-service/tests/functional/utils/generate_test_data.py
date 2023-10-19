import typing

import faker
from pydantic import BaseModel

fake = faker.Faker()


def gtd(model, *fields, del_none_attrs=True, return_as_dict=True, **set_attrs):
    def fake_int():
        return fake.random.randint(10, 10000)

    def fake_str():
        return fake.word()+fake.word()+fake.word()  # хз как указать длину, указал как костыль

    def get_handler(type_obj):
        return {int: fake_int, str: fake_str}.get(type_obj)

    def delete_none_attrs(model):
        for field, value in model.dict().items():
            if not value:
                delattr(model, field)

        return model

    for model_field in model.__annotations__.items():
        if model_field[0] in fields and not isinstance(model_field[1], BaseModel) \
                and not isinstance(model_field[1], typing._SpecialForm):
            setattr(model, model_field[0], get_handler(model_field[1])())

    for attr, value in set_attrs.items():
        setattr(model, attr, value)

    if del_none_attrs:
        model = delete_none_attrs(model)

    if return_as_dict:
        model = model.dict()

    return model