# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
from .forms import *
from .models import *
from django.shortcuts import redirect
from django.core.mail import EmailMessage, BadHeaderError
from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_permission
from rolepermissions.permissions import grant_permission, revoke_permission
import os
from django.conf import settings
from django.contrib.auth import hashers as hs
from django.utils.crypto import get_random_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
import ntplib
import time

from weasyprint import HTML

registered = 0
confirmed = 0
paid = 0

def pdf_gen(request):
	actual_user = get_object_or_404(UserProfile, id = request.session['member_id'])
	if has_permission(actual_user,'retrieve_any_student'):
		allS = UserProfile.objects.filter(groups__name='student')
		students = []
		for i in allS:
			if i.is_active:
				students.append(i)

		html_string = render_to_string('site_functions/pdf_template.html', {'stds': students})
		html = HTML(string=html_string)
		html.write_pdf(target='/tmp/participantes_sempgan5.pdf')
		fs = FileSystemStorage('/tmp')
		with fs.open('participantes_sempgan5.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="participantes_sempgan5.pdf"'
			return response
		return response
	else:
		raise Http404

def lista_presenca(request):
	actual_user = get_object_or_404(UserProfile, id = request.session['member_id'])
	if has_permission(actual_user,'retrieve_any_student'):
		allS = UserProfile.objects.filter(groups__name='student')
		students = []
		for i in allS:
			if i.is_active:
				students.append(i)
		students.sort(key=lambda x: x.name, reverse=False)
		html_string = render_to_string('site_functions/lista_presenca.html', {'stds': students})
		html = HTML(string=html_string)
		html.write_pdf(target='/tmp/lista_presenca_sempgan5.pdf')
		fs = FileSystemStorage('/tmp')
		with fs.open('lista_presenca_sempgan5.pdf') as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="lista_presenca_sempgan5.pdf"'
			return response
		return response
	else:
		raise Http404

def recover_password(request):
	if request.method == "POST":
		try:
			user = UserProfile.objects.get(email=request.POST.get('email', False))
		except UserProfile.DoesNotExist:
			return render(request, 'site_functions/recover_password.html', {'message': 'Usuário não cadastrado.'})
		else:
			user.confirmation_code = get_random_string(length=16)
			user.save()
			msg = u'Prezado ' + user.pronome_tratamento + ' ' + user.name + ',\n\nPara recuperar sua senha, clique no link abaixo: \n\n dominio/new_pass/' + str(user.confirmation_code) + "/" + str(user.id) + " \
\n\nAtenciosamente,  \
\nComissão Executiva do V SEMPGAN.\n \
\nPara mais informações, entre em contato conosco através do site [colocar link]."
			send_email('Recuperar senha',msg,user.email)
			message = "Em breve você receberá um email para prosseguir com a alteração de senha."
			return render(request, 'site_functions/recover_password.html', {'message': message})
	else:
		return render(request, 'site_functions/recover_password.html', {'message': "Digite seu email abaixo."})


def new_pass(request, confirmation_code, user_id):
	try:
		user = get_object_or_404(UserProfile, id=user_id)
	except:
		return redirect(home)
	else:
		if user.confirmation_code == confirmation_code:
			return redirect(alterate, user_id=user.id)
		else:
			return HttpResponse("Link inválido. Gere novamente.")



def alterate(request, user_id):
	user = get_object_or_404(UserProfile, id=user_id)
	if request.method == "POST":
		print("post")
		if request.POST.get('pass1', False) == request.POST.get('pass2', False):
			user.password = hs.make_password(request.POST.get('pass1', False))
			user.confirmation_code = get_random_string(length=16)
			user.save()
			return redirect(user_login)
		else:
			return render(request, 'site_functions/new_pass.html', {'message': "As senhas digitadas não combinam. Tente novamente.", 'usr':user.id})
	else:
		return render(request, 'site_functions/new_pass.html', {'message': "Digite sua nova senha.", 'usr':user.id})


def home(request):
	#testado e funcionando
	#scs = Minicurso.objects.all()
	talks = Talk.objects.all()
	return render(request, 'site_functions/home.html', {'log':request.session, 'talks':talks})

def register(request):
	#testado e funcionando
	limit_users = 170
	esgoted = 0 #cadastro online
	registereds = 0
	for x in UserProfile.objects.all():
		if not has_permission(x, 'add_new_admins'):
			registereds += 1
	mns = Minicurso.objects.all()

	if registereds >=limit_users: esgoted = 1 #vagas esgotadas

	client = ntplib.NTPClient()
	response = client.request('pool.ntp.org')
	time_ = time.localtime(response.tx_time)
	if not (time_.tm_year == 2017 and time_.tm_mon == 10 and time_.tm_mday <= 15 and time_.tm_mday >= 9):
		esgoted = 0 #fora do prazo de inscrições

	message = False
	if request.method == "POST":
		new_user = UserForm(request.POST)
		if new_user.is_valid():
			user = new_user.save()
			user.password = hs.make_password(request.POST.get('password', False))
			user.confirmation_code = get_random_string(length=16)
			user.is_active = True #setar para false ao subir o site
			user.save()
			assign_role(user, 'student')
			msg = u'Prezado ' + user.pronome_tratamento + ' ' + user.name + ',\n\nPara confirmar a sua inscrição no V Seminário do Programa de Pós-graduação em Alimentos e Nutrição clique no link abaixo: \n\n dominio/confirm/' + str(user.confirmation_code) + "/" + str(user.id) + " \
\n\nAtenciosamente,  \
\nComissão Executiva do V SEMPGAN.\n \
\nPara mais informações, entre em contato conosco através do site [colocar link]."
			send_email('Confirmação de inscrição',msg,user.email)
			message = "Você foi cadastrado(a). Em breve receberá um email para confirmação de cadastro. Clique no link recebido para confirmar e acessar sua conta."
			return render(request, 'site_functions/register.html', {'form': new_user, 'log':request.session, 'status': esgoted, 'msg':message})
	else:
		new_user = UserForm()
	return render(request, 'site_functions/register.html', {'form': new_user, 'log':request.session,  'status': esgoted, 'msg':message})

def confirm(request, confirmation_code, user_id):
	try:
		user = get_object_or_404(UserProfile, id=user_id)
		if user.confirmation_code == confirmation_code:
			user.is_active = True;
			user.save()
			return redirect(user_login)
		else:
			return HttpResponse('Codigo de confirmação inválido')
	except:
		return redirect(home)

def admin_register(request):
	actual_user = get_object_or_404(UserProfile, id = request.session['member_id'])
	if request.method == "POST":
		new_admin = AdminForm(request.POST)
		if new_admin.is_valid() and has_permission(actual_user, 'add_new_admins'):
			user = new_admin.save()
			user.password = hs.make_password(request.POST.get('password', False))
			user.confirmation_code = get_random_string(length=16)
			user.save()
			msg = u'Para confirmar a seu cadastro clique no link \n dominio/confirm/' + str(user.confirmation_code) + "/" + str(user.id)
			send_email('Confirmação de inscrição',msg,user.email)
			assign_role(user, 'admin')
			return redirect(list_admins)
	else:
		new_admin = AdminForm()
	return render(request, 'site_functions/register_admin.html', {'form': new_admin, 'log':request.session})

def user_login(request):
	#testado e funcionando
	if request.method == "POST":
		try:
			user = UserProfile.objects.get(email=request.POST.get('email', False))
		except UserProfile.DoesNotExist:
			return render(request, 'site_functions/login.html', {'message': 'Usuário não cadastrado.'})
		else:
			if hs.check_password(request.POST.get('psw', False), user.password):
				if user.is_active:
					request.session['is_logged'] = True
					request.session['member_id'] = user.id
					if has_permission(user, 'add_new_admins'):
						request.session['is_admin'] = True
						return redirect(list_students, page=1)
					return redirect(user_detail,user_id=user.id)
				else:
					return render(request, 'site_functions/login.html', {'message': 'Usuario não está ativo.'})
			else:
				return render(request, 'site_functions/login.html', {'message': 'Senha incorreta. Tente novamente.'})
	return render(request, 'site_functions/login.html', {'message': 'Entre com seu email e senha.'})

def user_logout(request):
	#testado e funcionando
	try:
		del request.session['member_id']
	except KeyError:
		pass
	try:
		del request.session['is_logged']
	except KeyError:
		pass
	try:
		del request.session['is_admin']
	except KeyError:
		pass
	return redirect(home)

def schedule(request):
	talks = Talk.objects.all()
	short = Minicurso.objects.all()
	return render(request, 'site_functions/cronograma.html', {'talks':talks, 'shorts':short, 'log': request.session})

def user_detail(request, user_id):
	#testado e funcionando
	if int(user_id) == int(request.session['member_id']):
		user = get_object_or_404(UserProfile, id = request.session['member_id'])
		print(user.comprovante)
		articles = Article.objects.all().filter(user=user.id)
		return render(request, 'site_functions/user_details.html', {'user': user, 'log':request.session})
	else:
		user = get_object_or_404(UserProfile, id = request.session['member_id'])
		if has_permission(user,'retrieve_any_student'):
			user_retrieve = get_object_or_404(UserProfile, id=user_id)
			receipt_form = ReceiptForm()
			article_form = ArticleForm()
			scs = user_retrieve.minicursos
			articles_retrieve = Article.objects.all().filter(user=user_retrieve.id)
			return render(request, 'site_functions/user_details.html', {'user': user_retrieve, 'log':request.session})

def list_students(request,page):
	#testado e funcionando
	registered = 0
	confirmed = 0
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if has_permission(user, 'list_all_students'):
		for x in UserProfile.objects.all():
			if not has_permission(x, 'add_new_admins'):
				registered += 1
				if x.is_active:
					confirmed += 1
		Users = UserProfile.objects.filter(groups__name='student')
		paginator = Paginator(Users,10)
		try:
			users = paginator.page(page)
		except PageNotAnInteger:
			users = paginator.page(1)
		except:
			users = paginator.page(paginator.num_pages)
		return render(request, 'site_functions/inscritos.html', {'users': users,
					'log': request.session, 'max':registered, 'ok':confirmed})
	else:
		return redirect(home)

def del_student(request,user_id):
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if has_permission(user, 'list_all_students'):
		user_d = get_object_or_404(UserProfile, id=user_id)
		"""if not has_permission(user_d, 'add_new_admins'):
			registered -= 1
			if user_d.is_active:
				confirmed -= 1
			if user_d.had_paid:
				paid -= 1"""
		user_d.delete()

		return redirect(list_students,page=1)
	else:
		return redirect(home)

def list_admins(request):
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if has_permission(user, 'list_all_students'):
		admins = UserProfile.objects.filter(groups__name='admin')
		return render(request, 'site_functions/administrators.html', {'admins': admins,
					'log': request.session})
	else:
		return redirect(home)
"""
def list_short_courses(request):
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if has_permission(user, 'edit_short_course'):
		scs = Minicurso.objects.all()
		values = []
		for i in scs:
			values.append([i,UserProfile.objects.all().filter(minicursos=i.id).count()])
		return render(request, 'site_functions/short_courses.html', {'scs': values,
					'log': request.session})
	else:
		return redirect(home)

def list_users_by_sc(request, short_course_id):
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if has_permission(user, 'edit_short_course'):
		sc_usrs = UserProfile.objects.all().filter(minicursos=short_course_id)
		paid = []
		active = []
		for i in sc_usrs:
			if i.had_paid:
				paid.append(i)
			if i.is_active:
				active.append(i)
		return render(request, 'site_functions/inscritos.html', {'ok':len(active),'paid': len(paid),'max':len(sc_usrs),'users': sc_usrs,
					'log': request.session})
	else:
		return redirect(home)
"""
def list_talks(request):
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if has_permission(user, 'edit_short_course'):
		talks = Talk.objects.all()
		talk_form = TalkRegisterForm()
		return render(request, 'site_functions/talks.html', {'talks': talks,
					'log': request.session, 'talk_form': talk_form})
	else:
		return redirect(home)
"""
def mark_payment(request, user_id):
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if has_permission(user, 'mark_payment'):
		user_p = get_object_or_404(UserProfile, id=user_id)
		user_p.had_paid = True
		user_p.save()
		msg = u"Prezado "+ user_p.pronome_tratamento + " " + user_p.name + ", a sua inscrição \
no III Simpósio de Pós-graduação em Alimentos e Nutrição foi confirmada. \
\n\nAtenciosamente,  \
\nComissão Executiva do III SIPPAN.\n \
\nPara mais informações, entre em contato conosco através do site [colocar link]."
		send_email('Confirmação de pagamento',msg,user_p.email)
		return redirect(user_detail,user_id)

def accept_article(request, user_id, article_id):
	user = get_object_or_404(UserProfile, id=request.session['member_id'])
	if request.method == 'POST':
		if has_permission(user, 'revision_article'):
			article_form = ArticleAnalisyForm(request.POST)
			if article_form.is_valid():
				user_p = get_object_or_404(UserProfile, id=user_id)
				article_p = get_object_or_404(Article, id=article_id)
				article_p.accepted = article_form.cleaned_data['accepted']
				article_p.revision = article_form.cleaned_data['revision']
				article_p.save()
				msg = u'Prezado '+ user.pronome_tratamento + ' ' + user.name + ', informamos o parecer final da avaliação do seu trabalho \
intitulado ' + article_p.title + '.\n\nParecer: '
				if (article_form.cleaned_data['accepted'] == 1):
					msg += u'ACEITO\n'
				elif(article_form.cleaned_data['accepted'] == 0):
					msg += u"REJEITADO\n"
				if article_p.revision:
					msg += u"Comentários dos avaliadores: " + article_p.revision + "\n\n"
				msg += "Dados do trabalho \nTítulo: " + article_p.title
				msg += "\nÁrea: A DEFINIR"
				msg += "\nAutores: " + article_p.autores

				msg += "\n\nAtenciosamente,  \
\nComissão Executiva do III SIPPAN.\n \
\nPara mais informações, entre em contato conosco através do site [colocar link]."
				send_email('Avaliação do artigo - 3º Sipan',msg,user_p.email)

				return redirect(user_detail,user_id=user.id)
		else:
			return redirect(home)
	else:
		article_form = article_form = ArticleAnalisyForm()
		return render(request, 'site_functions/article_revision.html', {'form': article_form,
					'log': request.session})


def register_short_course(request):
	if request.method == 'POST':
		new_short_course = ShortCourseForm(request.POST, request.FILES)
		if new_short_course.is_valid():
			new_short_course.save()
			return redirect(list_short_courses)
	else:
		user = UserProfile.objects.get(pk=request.session['member_id'])
		if has_permission(user, 'create_short_course'):
			new_short_course = ShortCourseForm()
			return render(request, 'site_functions/register_short.html', {'form': new_short_course, 'log':request.session})
		else:
			return redirect(home)

def short_course_detail(request, short_course_id):
	short_course = get_object_or_404(Minicurso, id = short_course_id)
	user = get_object_or_404(UserProfile, id = request.session['member_id'])
	return render(request, 'site_functions/short_course_details.html', {'short_course':short_course,
			'log':request.session, 'user':user})
"""
def talk_detail(request, talk_id):
	talk = get_object_or_404(Talk, id = talk_id)
	print(talk.talk_name)
	user = get_object_or_404(UserProfile, id = request.session['member_id'])
	return render(request, 'site_functions/talk_details.html', {'talk':talk,
			'log':request.session, 'user':user})
"""
def edit_short_course(request, short_course_id):
	sc_form = get_object_or_404(Minicurso, id=short_course_id)
	if request.method == 'POST':
		user = get_object_or_404(UserProfile, id = request.session['member_id'])
		if has_permission(user, 'edit_short_course'):
			form = ShortCourseForm(request.POST,request.FILES, instance=sc_form)
			short_course = get_object_or_404(Minicurso, id = short_course_id)
			if form.is_valid():
				short_course.name = form.cleaned_data['name']
				short_course.description = form.cleaned_data['description']
				short_course.professor = form.cleaned_data['professor']
				short_course.begin = form.cleaned_data['begin']
				short_course.duration = form.cleaned_data['duration']
				short_course.short_course_cover = form.cleaned_data['short_course_cover']
				short_course.save()
				return redirect(list_short_courses)
	else:
		user = get_object_or_404(UserProfile, id = request.session['member_id'])
		if has_permission(user, 'edit_short_course'):
			short_course = get_object_or_404(Minicurso, id = short_course_id)
			form = ShortCourseForm(instance=sc_form)
			return render(request, 'site_functions/edit_short_course.html',
			{'short_course':short_course, 'log':request.session, 'user':user, 'form':form})
"""
def edit_talk(request, talk_id):
	talk_form = get_object_or_404(Talk, id=talk_id)
	if request.method == 'POST':
		user = get_object_or_404(UserProfile, id = request.session['member_id'])
		if has_permission(user, 'edit_talk'):
			form = TalkRegisterForm(request.POST, request.FILES, instance=talk_form)
			talk = get_object_or_404(Talk, id = talk_id)
			if form.is_valid():
				talk.talk_name = form.cleaned_data['talk_name']
				talk.talk_description = form.cleaned_data['talk_description']
				talk.talk_speaker = form.cleaned_data['talk_speaker']
				talk.talk_begin = form.cleaned_data['talk_begin']
				talk.talk_local = form.cleaned_data['talk_local']
				talk.talk_speaker_lattes = form.cleaned_data['talk_speaker_lattes']
				talk.talk_speaker_photo = form.cleaned_data['talk_speaker_photo']
				talk.save()
				print(talk.talk_name)
				return redirect(list_talks)
	else:
		user = get_object_or_404(UserProfile, id = request.session['member_id'])
		print("test")
		if has_permission(user, 'edit_talk'):
			talk = get_object_or_404(Talk, id = talk_id)
			form = TalkRegisterForm(instance=talk_form)
			return render(request, 'site_functions/edit_talk.html',
			{'talk':talk, 'log':request.session, 'user':user, 'form':form})

def register_talk(request):
	if request.method == 'POST':
		new_talk_form = TalkRegisterForm(request.POST, request.FILES)
		if new_talk_form.is_valid():
			new_talk_form.save()
			return redirect(list_talks)
		else:
			return HttpResponse('Algum campo não está válido')
	else:
		user = UserProfile.objects.get(pk=request.session['member_id'])
		if has_permission(user, 'create_short_course'):
			new_talk_form = TalkRegisterForm()
			return render(request, 'site_functions/register_talk.html', {'form': new_talk_form, 'log':request.session})
		else:
			return redirect(home)
"""
def upload_receipt(request, user_id):
	if request.method == 'POST':
		if int(user_id) == int(request.session['member_id']):
			receipt = ReceiptForm(request.POST, request.FILES)
			if receipt.is_valid():
				user = get_object_or_404(UserProfile, pk=user_id)
				user.comprovante = receipt.cleaned_data['image_file']
				user.save()
				return redirect(user_detail, user_id)
	else:
		receipt = ReceiptForm()
	return render(request, 'site_functions/upload_receipt.html', {'form': receipt})

def upload_article(request, user_id):
	#testado e funcionando
	if request.method == 'POST':
		if int(user_id) == int(request.session['member_id']):
			article_form = ArticleForm(request.POST, request.FILES)
			if article_form.is_valid():
				Art = Article()
				Art.user = get_object_or_404(UserProfile, id = request.session['member_id'])
				Art.title = request.POST['title']
				Art.document = request.FILES['document']
				Art.autores = request.POST['autores']
				Art.save()
				return redirect(user_detail,Art.user.id)
	else:
		article_form = ArticleForm()
	return	render(request, 'site_functions/upload_article.html', {'form': article_form, 'log': request.session})
"""
def send_email(subject, message, to_email):
	if subject and message and to_email:
		try:
			email = EmailMessage(subject, message, to=[to_email])
			email.send()
		except BadHeaderError:
			return HttpResponse('Header invalido')
		return
	else:
		return HttpResponse("Tenha certeza que todos os parametros sao validos")

def download(request, path):
	file_path = os.path.join(settings.MEDIA_ROOT, path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type='application/' + path.split('.')[-1])
			response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
			return response
	else:
		raise Http404
