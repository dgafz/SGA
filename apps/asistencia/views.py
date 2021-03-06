# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, DeleteView
from django.views.generic.edit import FormView, FormMixin, UpdateView
from django.views.generic.detail import DetailView

from .models import Horario, Aula, Docente, CargaAcademica, AsistenciaAlumno, AsistenciaDocente

from django.contrib.messages.views import SuccessMessageMixin

from apps.users.models import User
from apps.notas.models import Asignatura

from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from .forms import DniForm, HorarioForm, AulaForm, DocenteForm, AsistenciaAlumnoForm

from datetime import datetime
from braces.views import LoginRequiredMixin


class AsistenciaDocenteView(LoginRequiredMixin, FormView):
    template_name = 'asistencia/asistencia_docente.html'
    login_url = reverse_lazy('users_app:login')
    form_class = DniForm

    def form_valid(self, form):
        # guardar asistencia
        dni = form.cleaned_data['dni']
        docente = Docente.objects.get(user__username=dni)

        return HttpResponseRedirect(
            reverse(
                'asistencia_app:asistencia_docente_detalle',
                kwargs={'pk': docente.pk},
            )
        )


class AsistenciaDocenteDetalle(LoginRequiredMixin, FormMixin, DetailView):
    model = Docente
    form_class = DniForm
    template_name = 'asistencia/asistencia_docente_detalle.html'
    login_url = reverse_lazy('users_app:login')

    def get_success_url(self):
        return reverse_lazy(
            'asistencia_app:asistencia_docente_detalle',
            kwargs={'pk': self.object.pk},
        )

    def get_context_data(self, **kwargs):
        context = super(AsistenciaDocenteDetalle, self).get_context_data(**kwargs)
        # self.get_form() es form_class enviamos el formulario {{ form }}
        context['form'] = self.get_form()
        # self.object es el objecto docente que psa pro url
        carga = CargaAcademica.objects.carga_docente(self.object.user)
        context['carga_academica'] = carga
        return context

    def post(self, request, *args, **kwargs):
        # get_object() es el parametro matricula q se psa por url
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # si el formulrio es valido cambiamos el valur de la url
        # con en el nuevo docente
        dni = form.cleaned_data['dni']
        self.object = Docente.objects.get(user__username=dni)
        return super(AsistenciaDocenteDetalle, self).form_valid(form)


class AsistenciaAlumnoView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    form_class = AsistenciaAlumnoForm
    template_name = 'asistencia/asistencia_alumno.html'
    success_url = reverse_lazy('notas_app:panel_docente')
    success_message = "Se guardo correctamente la asistencia de los alumnos...!!"

    def get_form_kwargs(self):
        kwargs = super(AsistenciaAlumnoView, self).get_form_kwargs()
        kwargs.update({
            'grupo': self.kwargs.get('grupo', 0),
            'pk': self.kwargs.get('pk', 0),
            'user': self.request.user,
        })
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        docente = Docente.objects.get(user=user)
        matriculas = form.cleaned_data['alumnos']
        fecha = datetime.now()
        asignatura_pk = self.kwargs.get('pk', 0)
        asignatura = Asignatura.objects.get(pk=asignatura_pk)
        for alumno in matriculas:
            asistencia = AsistenciaAlumno(
                docente=docente,
                matricula=alumno,
                asignatura=asignatura,
                estado=True,
                fecha=fecha,
            )
            asistencia.save()
        return super(AsistenciaAlumnoView, self).form_valid(form)


class PanelAulaView(LoginRequiredMixin, TemplateView):
    template_name = 'aula/panel_aula.html'
    login_url = reverse_lazy('users_app:login')

    def get_context_data(self, **kwargs):
        context = super(PanelAulaView, self).get_context_data(**kwargs)
        context['aulas'] = Aula.objects.all().order_by('nro_aula')
        context['cantidad'] = context['aulas'].count()
        return context


class DetalleAula(LoginRequiredMixin, DetailView):
    template_name = 'aula/detalle_aula.html'
    login_url = reverse_lazy('users_app:login')
    model = Aula


class AgregarAula(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = AulaForm
    template_name = 'aula/agregar_aula.html'
    success_url = reverse_lazy('asistencia_app:panel_aula')
    login_url = reverse_lazy('users_app:login')
    success_message = "se creo correctamente"


class ModificarAula(LoginRequiredMixin, UpdateView):
    model = Aula
    template_name = 'aula/modificar_aula.html'
    login_url = reverse_lazy('users_app:login')
    success_url = reverse_lazy('asistencia_app:panel_aula')
    form_class = AulaForm


class EliminarAula(LoginRequiredMixin, DeleteView):
    template_name = 'aula/eliminar_aula.html'
    model = Aula
    success_url = reverse_lazy('asistencia_app:panel_aula')
    login_url = reverse_lazy('users_app:login')


class PanelHorarioView(LoginRequiredMixin, TemplateView):
    template_name = 'horario/panel_horario.html'
    login_url = reverse_lazy('users_app:login')

    def get_context_data(self, **kwargs):
        context = super(PanelHorarioView, self).get_context_data(**kwargs)
        context['horarios'] = Horario.objects.all().order_by('dia')
        context['cantidad'] = context['horarios'].count()
        return context


class DetalleHorario(LoginRequiredMixin, DetailView):
    template_name = 'horario/detalle_horario.html'
    login_url = reverse_lazy('users_app:login')
    model = Horario


class AgregarHorario(LoginRequiredMixin, CreateView):
    form_class = HorarioForm
    template_name = 'horario/agregar_horario.html'
    login_url = reverse_lazy('users_app:login')
    success_url = reverse_lazy('asistencia_app:panel_horario')


class ModificarHorario(LoginRequiredMixin, UpdateView):
    model = Horario
    template_name = 'horario/modificar_horario.html'
    login_url = reverse_lazy('users_app:login')
    success_url = reverse_lazy('asistencia_app:panel_horario')
    form_class = HorarioForm


class EliminarHorario(LoginRequiredMixin, DeleteView):
    template_name = 'horario/eliminar_horario.html'
    login_url = reverse_lazy('users_app:login')
    model = Horario
    success_url = reverse_lazy('asistencia_app:panel_horario')


class PanelDocenteView(LoginRequiredMixin, TemplateView):
    template_name = 'docente/panel_docente.html'
    login_url = reverse_lazy('users_app:login')

    def get_context_data(self, **kwargs):
        context = super(PanelDocenteView, self).get_context_data(**kwargs)
        context['docentes'] = Docente.objects.all()
        context['cantidad'] = context['docentes'].count()
        return context


class AgregarDocente(LoginRequiredMixin, FormView):
    template_name = 'docente/agregar_docente.html'
    login_url = reverse_lazy('users_app:login')
    form_class = DocenteForm
    success_url = reverse_lazy('asistencia_app:panel_aula')

    def form_valid(self, form):
        dni = form.cleaned_data['username']
        nombres = form.cleaned_data['first_name']
        apellidos = form.cleaned_data['last_name']
        telefono = form.cleaned_data['phone']
        email = form.cleaned_data['email']
        sexo = form.cleaned_data['gender']
        avatar = form.cleaned_data['avatar']
        direccion = form.cleaned_data['address']
        fecha_nacimineto = form.cleaned_data['date_birth']
        tipo_user = '2'
        password = form.cleaned_data['password1']

        user = User.objects.create_user(
            username=dni,
            first_name=nombres,
            last_name=apellidos,
            phone=telefono,
            email=email,
            gender=sexo,
            avatar=avatar,
            address=direccion,
            date_birth=fecha_nacimineto,
            type_user=tipo_user,
            password=password,
        )
        user.save()

        tipo_docente = form.cleaned_data['tipo_docente']
        especialidad = form.cleaned_data['especialidad']
        titulo = form.cleaned_data['titulo']

        Docente.objects.create(
            user=user,
            tipo_docente=tipo_docente,
            especialidad=especialidad,
            titulo=titulo,
        )
        return super(AgregarDocente, self).form_valid(form)
