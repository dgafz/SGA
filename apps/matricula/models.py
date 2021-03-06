# -*- encoding: utf-8 -*-
from django.db import models
from apps.notas.models import Modulo, Asignatura
from django.conf import settings
from django.template.defaultfilters import slugify
from datetime import date
from django.core.validators import RegexValidator


class Carrera(models.Model):
    nombre = models.CharField('nombre', max_length=50)
    siglas = models.CharField('abrebiatura', max_length=4)
    titulo = models.CharField('licenciatura', max_length=50)

    class Meta:
        verbose_name_plural = 'Carreras'

    def __unicode__(self):
        return str(self.nombre)


class Programacion(models.Model):

    vacantes = models.PositiveIntegerField()
    inicio = models.DateField()
    fin = models.DateField()
    semestre = models.CharField(max_length=20, unique=True)
    finalizado = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Programaciones'
        ordering = ['semestre']

    def __unicode__(self):
        return self.semestre


class Alumno(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    carrera_profesional = models.ForeignKey(Carrera)
    slug = models.SlugField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.user.get_full_name())
        super(Alumno, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.user.get_full_name()


class ManagerMatricula(models.Manager):

    def matricula_pendiente(self):
        hoy = date.today()
        return self.filter(
            programacion__inicio__lte=hoy,
            programacion__fin__gte=hoy,
            completado=False,
        )
        
    def ultimo_modulo(self, user):
        #listamos todas las matriculas del alumno 121314
        matriculas = self.filter(alumno__user__username=user)
        #retornamos el ultimo modulo
        return matriculas[0].modulo.nombre

    def alumnos_por_curso(self, kwasignatura):
        mod = Modulo.objects.recuperar_modulo(kwasignatura)
        print '================= hola 2 =========================='
        alumnos = self.filter(modulo=mod)
        #retornamos la lista de alumnos que pertenbecen a ese modulo
        return alumnos 


class Turno(models.Model):
    grupo = models.CharField(max_length=1)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __unicode__(self):
        return "%s - %s" % (str(self.hora_inicio), str(self.hora_fin))


class Matricula(models.Model):

    alumno = models.ForeignKey(Alumno)
    modulo = models.ForeignKey(Modulo)
    turno = models.ForeignKey(Turno)
    fecha_matricula = models.DateTimeField()
    estado_matricula = models.BooleanField(default=False)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=600,)
    completado = models.BooleanField(default=False)
    programacion = models.ForeignKey(Programacion)
    tipo_descuento = models.ForeignKey(
        'pagos.Descuento', blank=True, null=True, default=1)

    objects = ManagerMatricula()

    def save(self, *args, **kwargs):
        if self.modulo and self.estado_matricula==False:
            self.saldo = self.modulo.costo
        super(Matricula, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.alumno)


class CursosCargo(models.Model):
    matricula = models.ForeignKey(Matricula)
    aisgnatura = models.ForeignKey(Asignatura)
