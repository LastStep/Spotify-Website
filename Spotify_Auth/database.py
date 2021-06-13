from typing import Union
from django.db import models, IntegrityError
from django.db.models.query import QuerySet


class DataBase(models.Model):

    def __init__(self, model):
        self.model: models.Model = model
        self.model_instance: models.Model = None

    
    def get_instance(self, filters: dict) -> dict:
        return self.model.objects.get(**filters)


    def save_data(self):
        self.model_instance.save()


    def get_data(
        self, 
        filters: dict, 
        fields: tuple[str] = (), 
        order: tuple[str] = (), 
        as_list: bool = False,
        flat: bool = False
    ) -> Union[QuerySet[dict], QuerySet[tuple], QuerySet[list]]:

        query_set = self.model.objects.filter(**filters).order_by(*order)
        if as_list:
            return query_set.values_list(*fields, flat=flat)
        return query_set.values(*fields)

    
    # Adds Data in the instance
    def add_data(self, **data: dict):
        self.model_instance = self.model(**data)

    
    # Inserts Data in the DataBase
    def insert_data(self, **data: dict):
        self.model.objects.create(**data)

    
    def update_data(self, filters: dict, data: dict):
        self.model.objects.filter(**filters).update(**data)

    
    def update_or_create(self, filters: dict, data: dict):
        try:
            self.model.objects.update_or_create(**data, **filters, defaults=data)
        except IntegrityError:
            self.update_data(filters=filters, data=data)
        

    def delete_data(self, **filters: dict):
        self.model.objects.filter(**filters).delete()

    
    def count_objects(self, filters: dict) -> int:
        return self.model.objects.filter(**filters).count()