## validators.py
from schematics.models import Model
from schematics.types import URLType, StringType


class ProductItem(Model):
    title = StringType(required=True)
    price = StringType(required=True)
    image_url = URLType()
    url = URLType(required=True)