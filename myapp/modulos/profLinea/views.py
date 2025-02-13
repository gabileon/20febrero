from django.shortcuts import render, redirect
import datetime, random, sha
from myapp.modulos.formulacion.forms import crearProgramaForm
from myapp.modulos.presentacion.forms import ImageUploadForm
from myapp.modulos.formulacion.models import Linea, Evaluacion, Evaluaciones, Recurso, Analisis, AnalisisM, Log, Asignatura, Programa, MyWorkflow,  ClaseClase, Completitud
from myapp.modulos.jefeCarrera.models import Evento
from myapp.modulos.indicadores.models import ProgramasPorEstado
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from myapp.modulos.presentacion.models import CredentialsModel
from myapp import settings
from django.contrib.auth.models import User
from myapp.modulos.presentacion.models import UserProfile
from datetime import datetime, timedelta
from myapp.modulos.presentacion.forms import cambiarDatosForm
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
import httplib2
import os
from apiclient import errors
from myapp.modulos.jefeCarrera.forms import changePasswordForm
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive',
    redirect_uri='http://localhost:8000/oauth2callback/')

def revisarRol (request):
    user = User.objects.get(username=request.user.username)
    perfil = UserProfile.objects.get(user=user.id)
    bandera = None
    if perfil.rol_actual == 'PL':
        pass
    else:
        return redirect ('/errorLogin/')


def cambiarDatosProfeView(request):
	userTemp = User.objects.get(username=request.user.username)
	perfilTemp = UserProfile.objects.get(user=userTemp.id)
	if perfilTemp.rol_actual == 'PL':
		form = cambiarDatosForm()
		user = request.user
		profile = UserProfile.objects.get(user=user)
		if request.method == "POST":
			form = cambiarDatosForm(request.POST)
			if form.is_valid():
				name = form.cleaned_data['name']
				last_name = form.cleaned_data['last_name']
				password = form.cleaned_data['password']
				user.first_name = name
				user.last_name = last_name
				user.set_password(password)
				user.save()
				profile.fechaPrimerAcceso = datetime.now()- timedelta(hours=3)
				profile.save()
				return redirect ('/miperfilProfesor/')
		ctx = {'form': form, 'username': request.user.username}
		return render(request, 'profLinea/cambiarDatos.html', ctx)
	else:
		return redirect ('/errorLogin/')

def miperfilProfesorView(request):
    yo = User.objects.get(username=request.user.username)
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'PL':
	    userTemp = User.objects.get(username=request.user.username)
	    perfilTemp = UserProfile.objects.get(user=userTemp.id)
	    if request.method == 'POST':
	        form = ImageUploadForm(request.POST, request.FILES)
	        if form.is_valid():
	            foto = form.cleaned_data['image']
	            perfilTemp.foto = foto 
	            perfilTemp.save()
	            return redirect('/miperfilProfesor/')
	    ctx = {'user': userTemp, 'perfil': perfilTemp, 'username': request.user.username, 'yo': yo}
	    return render(request, 'profLinea/perfilConf.html', ctx)

def principalPLView(request):
	userTemp = User.objects.get(username=request.user.username)
	perfilTemp = UserProfile.objects.get(user=userTemp.id)
	if perfilTemp.rol_actual == 'PL':
		yo = User.objects.get(username=request.user.username)
		profile = UserProfile.objects.get(user=yo)
		if profile.fechaPrimerAcceso is None:
			return redirect('/cambiarDatosProfe/')
		programasApro = Programa.objects.filter(state='fin').filter(profesorEncargado=request.user).count()
		programas = Programa.objects.filter(state='aprobacionLinea').filter(~Q(profesorEncargado=yo))
		obtenerProgNo = []
		programasEval = Programa.objects.filter(state='analisisEvaluacionesAsociadas').filter(~Q(profesorEncargado=yo))
		estado = 5

		######### Evaluacion #############

		# finales = []
		# for p in programasEval:
		# 	analisism = Evaluacion.objects.get(programa=p.id)
		# 	try:
		# 		votantes = Evaluaciones.objects.filter(evaluacion = analisism).filter(~Q(votante=request.user))
		# 	except:
		# 		votantes = 0
		# 	if votantes !=0:
		# 		finales.append(p)
		# if len(finales) == 0:
		# 	finales = programasEval

		# evaluaciones = len(finale
		programasEval = Programa.objects.filter(state='analisisEvaluacionesAsociadas').filter(~Q(profesorEncargado=request.user))
		estado = 5
		yo = User.objects.get(username = request.user.username)
		finales = []
		votantesTemp = []
		bandera = False
		evaluacionTemp = None
		for p in programasEval:
			##3 obtemngo la evaluacion asociada de cada uno
			evaluacionTemp = Evaluacion.objects.get(programa=p.id)
			
			# ontengo los votos
			evaluacionesTemp = 	Evaluaciones.objects.filter(evaluacion=evaluacionTemp)
			if not evaluacionesTemp:
			
				finales.append(p)
				####### obtengo los votantes
			else:
				for e in evaluacionesTemp:
					if e.cord==False:
						votantesTemp.append(e.votante)
				for v in votantesTemp:
					if v==yo :
						bandera = True
				if bandera ==False:
					finales.append(p)



		######### ANALISIS #############

		# analisisA = []
		# for p in programas:
		# 	analisism = AnalisisM.objects.get(programa=p.id)
		# 	try:
		# 		votantes = Analisis.objects.filter(analisis = analisism).filter(~Q(votante=request.user))
		# 	except:
		# 		votantes = 0
		# 	if votantes !=0:
		# 		analisisA.append(p)
		# if len(finales) == 0:
		# 	analisisA = programas

		programasEval = Programa.objects.filter(state='aprobacionLinea').filter(~Q(profesorEncargado=request.user))
		estado = 5
		yo = User.objects.get(username = request.user.username)
		finales2 = []
		votantesTemp = []
		bandera2 = False
		analisisTemp = None
		for p in programasEval:
			##3 obtemngo la evaluacion asociada de cada uno
			analisisTemp = AnalisisM.objects.get(programa=p.id)
			
			# ontengo los votos
			analisissTemp = 	Analisis.objects.filter(analisis=analisisTemp)
			if not analisissTemp:
		
				finales2.append(p)
				####### obtengo los votantes
			else:
				for e in analisissTemp:
					if e.cord==False:
						votantesTemp.append(e.votante)
	
				for v in votantesTemp:
					if v==yo :
						bandera2 = True
				if bandera2 ==False:
					finales2.append(p)


		analisisNum = len(finales2)

		############################
		form = crearProgramaForm()

		username = request.user.username
		programas = Programa.objects.filter(profesorEncargado=request.user.id).order_by('-fechaUltimaModificacion')
		otrosProgramas = Programa.objects.filter(~Q(profesorEncargado=request.user))

		try:
			storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
			credential = storage.get()
			http= httplib2.Http()
			http= credential.authorize(http)
			drive_service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
		except:
			return redirect('/errorGoogle/')
		if request.method == "POST":
			userTemp = User.objects.get(username=request.user.username)
			perfilTemp = UserProfile.objects.get(user=userTemp.id)
			p = Programa()
			#p.to_formulacion()
			form = crearProgramaForm(request.POST)
			if form.is_valid():
				asignatura = form.cleaned_data['asignatura']
				semestre = form.cleaned_data['semestre']
				ano = form.cleaned_data['ano']
					### se crea programa
				asignaturaM = Asignatura.objects.get(id=asignatura)
				print asignaturaM.linea.id
				p.asignatura = asignaturaM
				p.linea= p.asignatura.linea
				p.semestre = semestre
				p.ano = ano
				p.fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
				p.profesorEncargado = request.user
				titulo = "Programa " + asignaturaM.nombreAsig + " " + semestre + " " + ano
				
				if (perfilTemp.carpetaProgramas == "NO CREADA"):
					### CREAMOS UNA CARPETA ###
					body = {
						'title': 'Programas de Asignatura - '+request.user.first_name + " " + request.user.last_name,
						'mimeType': "application/vnd.google-apps.folder"
					}
					### se crea carpeta ###

					folder = drive_service.files().insert(body = body).execute()
					id_folder = folder.get('id')
					perfilTemp.carpetaProgramas = id_folder
					perfilTemp.save()

				body = {
					'title':'%s'%(titulo),
					'mimeType': "application/vnd.google-apps.document",
					'parents' : [{'id' : perfilTemp.carpetaProgramas}]
					}						
				try:
					file = drive_service.files().insert(body=body).execute()
					url = file.get('alternateLink')
			 		p.url = url
			 		p.to_formulacion()
			 		# logEstado(userTemp, p, p.state.title)
			 		p.to_datosAsig()
			 		# logEstado(userTemp, p, p.state.title)
			 		p.id_file = file['id']
			 		p.save()	 		
				except:
		 			return redirect('/errorGoogle/')
		 		logEstado(userTemp, p, p.state.title)
		else:
			form = crearProgramaForm()
					#GEt
		ctx = { 'userTemp': userTemp, 'evaluaciones': len(finales), 'yo': yo, 'username' : username,'estado': estado, 'form': form, 'programas': programas, 'porAnalizar': analisisNum, 'otros': otrosProgramas, 'aprobados': programasApro}
		return render(request, 'profLinea/principalPL.html', ctx)
	else:
		return redirect('/errorLogin/')

def misProgramasAprobadosView(request, id_user):
	yo = User.objects.get(username=request.user.username)
	try:
		programas = Programa.objects.filter(profesorEncargado=id_user).filter(state='fin')
	except:
		programas = []
	return render(request, 'profLinea/misProgramas.html', {'username': request.user.username, 'programas': programas, 'yo':yo})

def logEstado (userTemp, programa, state):

	l= Log()
	l.encargado = userTemp
	l.programa = programa
	l.state = state
	l.fecha = datetime.now() - timedelta(hours=3)
	l.save()	

def eliminarProgramaView(request, id_programa):
	userTemp = User.objects.get(username=request.user.username)
	perfilTemp = UserProfile.objects.get(user=userTemp.id)
	if perfilTemp.rol_actual == 'PL':
		try:
			storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
			credential = storage.get()
			http= httplib2.Http()
			http= credential.authorize(http)
			service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
		except:
			return redirect('/errorGoogle/')
		programa= Programa.objects.get(id=id_programa)
		try:
			service.files().delete(fileId=programa.id_file).execute()
		except:
			return redirect('/errorGoogle/')
	
		try:
			programa.evaluacion.delete()
			programa.analisism.delete()
			programa.rda.delete()
			programa.constribucion.delete()
			programa.estrategias.delete()
			programa.claseclase.delete()
			programa.administrativo.delete()
			programa.recursosapren.delete()
		except:
			pass
		programa.delete()
		return redirect('/principalPL/')
	else:
		return redirect('/errorLogin/')

def repositorioView(request):
    yo = User.objects.get(username=request.user.username)
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'PL':
        recursos = Recurso.objects.all()
        paginator = Paginator(recursos, 12)
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        username = request.user.username
        ctx = {'contacts': contacts, 'username': username, 'yo':yo}
        return render(request, 'profLinea/recursos.html', ctx)
    else:
        return redirect('/errorLogin/')

def fechasView(request):
	hoy = datetime.now()
	yo = User.objects.get(username=request.user.username)
	userTemp = User.objects.get(username=request.user.username)
	perfilTemp = UserProfile.objects.get(user=userTemp.id)
	if perfilTemp.rol_actual == 'PL':
		eventos = Evento.objects.all().filter(tipoEvento = 'profesor').filter(start__range=(hoy - timedelta(days=1), hoy + timedelta(days=200)))
		eventosGenerales = Evento.objects.all().filter(tipoEvento = 'general').filter(start__range=(hoy - timedelta(days=1), hoy + timedelta(days=200)))
		username = request.user.username
		ctx = {'eventos': eventos, 'eventosGenerales': eventosGenerales, 'username': username, 'yo': yo}
		return render(request, 'profLinea/eventosProfe.html', ctx)
	else:
		return redirect('/errorLogin/')

def changePasswordProfView(request, id_user):
    yo = User.objects.get(username=request.user.username)
    u = User.objects.get(id=id_user)
    form = changePasswordForm()
    if request.method == "POST":
        form = changePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            password = form.cleaned_data['password']
            if u is not None and u.check_password(old_password):
                u.set_password(password)
                u.save()
                return HttpResponseRedirect("/miperfilProfesor/")
    ctx = {'form':form, 'user':u, 'username': request.user.username, 'yo': yo}
    return render(request, 'presentacion/changePasswordProf.html', ctx)