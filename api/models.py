from django.db import models

# Create your models here.


class RequestUnitsMetrobusStatus(models.Model):

    token = models.CharField(max_length=500)

    is_completed = models.BooleanField(default=False)

    request_error = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Estado de la peticion"
        verbose_name_plural = "Estados del las peticiones"

    def __str__(self):
        return f"Completada :{self.is_completed}, error {self.request_error} , {self.token}"


class UnitsMetrobusStatus(models.Model):

    unit_id = models.IntegerField()

    position_latitude = models.FloatField()

    position_longitude = models.FloatField()

    date_updated = models.DateTimeField()

    load_at = models.DateTimeField(auto_now_add=True)

    address = models.CharField(max_length=300)

    district = models.CharField(max_length=100)

    token = models.CharField(max_length=500)

    class Meta:
        verbose_name = "Estado de la unidad"
        verbose_name_plural = "Estados de las unidades"

    def __str__(self):
        """Return role."""
        return f"La unidad {self.unit_id} se encuentra en {self.address}"
