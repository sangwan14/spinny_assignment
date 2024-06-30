from django.contrib.auth.models import User
from django.db import models

class Cuboid(models.Model):
    length = models.FloatField()
    breadth = models.FloatField()
    height = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def area(self):
        return 2 * (self.length * self.breadth + self.breadth * self.height + self.height * self.length)

    @property
    def volume(self):
        return self.length * self.breadth * self.height
