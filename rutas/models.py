from django.contrib.auth.models import User
from django.db import models


class Resena(models.Model):
    """Una reseña que un usuario deja sobre un lugar."""

    # El lugar vive en datos.py, así que guardamos su "id" (por ejemplo "alegre") como texto
    lugar_id = models.CharField(max_length=50)
    # Quién escribió la reseña. Si se borra el usuario, se borran sus reseñas.
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    calificacion = models.IntegerField()   # de 1 a 5
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now=True)   # se actualiza sola cada vez que se guarda

    def __str__(self):
        return self.lugar_id + " - " + self.usuario.username + " - " + str(self.calificacion)
