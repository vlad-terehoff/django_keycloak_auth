from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    user = models.ForeignKey(User, verbose_name="Исполнитель", related_name="tasks", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Наименование",
                            max_length=200)
    data_start = models.DateField(verbose_name='Дата создания', auto_now_add=True)
    data_finish = models.DateField(verbose_name='Дата окончания')
    is_active = models.BooleanField(verbose_name='Задача активна?', default=False)

    def __str__(self):
        return self.name
