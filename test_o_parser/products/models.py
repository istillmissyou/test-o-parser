from django.db.models import Model, PositiveIntegerField, TextField


class Product(Model):
    name = TextField()
    description = TextField(null=True)
    new_price = PositiveIntegerField(null=True)
    old_price = PositiveIntegerField(null=True)
    image_url = TextField(null=True)
    url = TextField(null=True)
    product_code = PositiveIntegerField()

    def __str__(self):
        return self.name
