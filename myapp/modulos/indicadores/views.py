from django.shortcuts import render
from chartit import DataPool, Chart
from myapp.modulos.indicadores.models import MonthlyWeatherByCity, ProgramasPorEstado
from myapp.modulos.formulacion.models import Programa
from django.shortcuts import render_to_response, get_object_or_404
from datetime import datetime

def weather_chart_view(request):
  username = request.user.username
  info = ProgramasPorEstado.objects.all().delete()
  ## voy por estado 
  ## AGREGO TODOS ##

  form = Programa.objects.filter(state="formulacionPrograma").count()
  new1= ProgramasPorEstado.objects.create(estado="Formulacion Programa por Linea", cantidad=form)
  new1.save()
  datos = Programa.objects.filter(state="definicionDatosAsignatura").count()
  new2= ProgramasPorEstado.objects.create(estado="Definicion Datos Asignatura", cantidad=datos)
  new2.save()
  general = Programa.objects.filter(state="definicionGeneral").count()
  new3= ProgramasPorEstado.objects.create(estado="Definiciones Generales", cantidad=general)
  new3.save()
  definicionConstribucion = Programa.objects.filter(state="definicionConstribucion").count()
  new4= ProgramasPorEstado.objects.create(estado="Definicion de Constribucion al Perfil de Egreso", cantidad=definicionConstribucion)
  new4.save()
  definicionRdA = Programa.objects.filter(state="definicionRdA").count()
  new5= ProgramasPorEstado.objects.create(estado="Definicion Resultados de Aprendizaje", cantidad=definicionRdA)
  new5.save()
  definicionEstrategias = Programa.objects.filter(state="definicionEstrategias").count()
  new6= ProgramasPorEstado.objects.create(estado="Estrategias de Ensenanza y de Aprendizaje", cantidad=definicionEstrategias)
  new6.save()
  definicionClaseClase = Programa.objects.filter(state="definicionClaseClase").count()
  new7= ProgramasPorEstado.objects.create(estado="Definicion de Clase a Clase", cantidad=definicionClaseClase)
  new7.save()
  analisisEvaluacionesAsociadas = Programa.objects.filter(state="analisisEvaluacionesAsociadas").count()
  new8= ProgramasPorEstado.objects.create(estado="Analisis de evaluaciones asociadas", cantidad=analisisEvaluacionesAsociadas)
  new8.save()
  verificacionCoherenciaCompletitud = Programa.objects.filter(state="verificacionCoherenciaCompletitud").count()
  new9= ProgramasPorEstado.objects.create(estado="Verificacion Coherencia y Completitud", cantidad=verificacionCoherenciaCompletitud)
  new9.save()
  definicionAspecAdmin = Programa.objects.filter(state="definicionAspecAdmin").count()
  new10= ProgramasPorEstado.objects.create(estado="Definicion de Aspectos Administrativos", cantidad=definicionAspecAdmin)
  new10.save()
  definicionRecursos = Programa.objects.filter(state="definicionRecursos").count()
  new11= ProgramasPorEstado.objects.create(estado="Definicion de Recursos de Aprendizaje", cantidad=definicionRecursos)
  new11.save()
  definicionAspectosFinales = Programa.objects.filter(state="definicionAspectosFinales").count()
  new12= ProgramasPorEstado.objects.create(estado="Definicion de Aspectos Finales", cantidad=definicionAspectosFinales)
  new12.save()
  aprobacionLinea = Programa.objects.filter(state="aprobacionLinea").count()
  new13= ProgramasPorEstado.objects.create(estado="Aprobacion Linea", cantidad=aprobacionLinea)
  new13.save()
  fastTrack = Programa.objects.filter(state="fastTrack").count()
  new14= ProgramasPorEstado.objects.create(estado="Fast Track", cantidad=fastTrack)
  new14.save()
  analisisProgramaJC = Programa.objects.filter(state="analisisProgramaJC").count()
  new15= ProgramasPorEstado.objects.create(estado="Analisis Programa por JC", cantidad=analisisProgramaJC)
  new15.save()
  indicacionModificacion = Programa.objects.filter(state="indicacionModificacion").count()
  new16= ProgramasPorEstado.objects.create(estado="Existen Indicaciones de Modificacion", cantidad=indicacionModificacion)
  new16.save()
  aprobacionProgramaJC = Programa.objects.filter(state="aprobacionProgramaJC").count()
  new17= ProgramasPorEstado.objects.create(estado="Aprobacion Programa por JC", cantidad=aprobacionProgramaJC)
  new17.save()
  finN = Programa.objects.filter(state="fin").count()
  new18= ProgramasPorEstado.objects.create(estado="Aprobados", cantidad=finN)
  new18.save()


  ds = DataPool(
  series=
  [{'options': {
  'source': ProgramasPorEstado.objects.all()},
  'terms': [
          'estado',
           'cantidad']}
           ])
  cht = Chart(
       datasource = ds, 
       series_options = 
          [{'options':{
            'type': 'column',
            'stacking':True},
          'terms':{
            'estado': [
              'cantidad'                ]
            }}],
  chart_options = 
       {'title': {
             'text': 'Programas por Estados'},
       'xAxis': {
              'title': {
                'text': 'Estados'}}})

     #Step 3: Send the chart object to the template.
  return render(request, 'indicadores/prueba.html', {'weatherchart': cht, 'username':username})


def vista_adm(request):
  user = User.objects.get(username=request.user.username)
  ctx = {'user': userTemp}
  return render(request, 'indicadores/vistaAdmin.html', ctx)


def profesores(request):
  profesores = Profesor.objects.all()
  ctx = {'profesores': programas}
  return render(request, 'indicadores/profesores.html', ctx)

def jefeCarrera(request):
  
  form = RegisterForm()
  if request.method == "POST":
    form = RegisterForm(request.POST)
    if form.is_valid():
      username = form.cleaned_data['username']
      name = form.cleaned_data['name']
      last_name = form.cleaned_data['last_name']
      email = form.cleaned_data['email']
      password_one = form.cleaned_data['password_one']
      password_two = form.cleaned_data['password_two']
      newUser = User.objects.create_user(username=username, first_name=name, last_name=last_name, email=email, password=password_one)
      newUser.save()
      newUserProfile = UserProfile.objects.create(user=newUser, rol_CL='JC')
      newUserProfile.save()
      return redirect('/login')
    else:
      ctx = {'form':form}
      return render(request,'presentacion/sign_up.html',ctx)
  ctx = {'form':form}
  return render(request,'presentacion/sign_up.html',ctx)



