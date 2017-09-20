# -*- coding: utf-8 -*-
from django import forms
from .models import *
from localflavor.br import forms as fm


class UserForm(forms.ModelForm):
	choices = (
		(1,'Sim'),
		(0,'Nao'),
 	)

	MODALIDADE_CHOICES = (
	('EST', u'Estudante'),
	('PRO', u'Profissional')
,)

	have_article = forms.TypedChoiceField(label='Vai submeter trabalho?',
						 choices=choices, widget=forms.RadioSelect, coerce=int
					)
	## MUDANÇAS FEITAS POR MIM(KÁSSIO)##
		#atribui as classes para cada campo do formulário
		#assim todos os campos estão estilizados com o tema do bootstrap
	#adicionei o parametro com a Classe form-control
	password = forms.CharField(label=("Senha"), widget=forms.PasswordInput(attrs={'placeholder' : 'Digite sua senha.', 'class' : 'form-control'}))
	#adicionei o parametro com a Classe form-control
	name = forms.CharField(label='Nome Completo', widget=forms.TextInput(attrs={'class' : 'form-control'}))
	#adicionei o parametro com a Classe form-control
	instituicao = forms.CharField(label='Instituicao', widget=forms.TextInput(attrs={'class' : 'form-control'}))
	#adicionei o parametro com a Classe form-control
	cpf = fm.BRCPFField(label='CPF', widget=forms.TextInput(attrs={'class' : 'form-control'}))
	#adicionei o parametro com a Classe form-control
	phone = forms.CharField(label='Telefone', widget=forms.TextInput(attrs={'class' : 'form-control'}))
	instituicao = forms.CharField(label='Instituição',required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
	local_de_atuacao = forms.CharField(label='Local de Atuação',required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
	profissao = forms.CharField(label='Profissão',required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
	curso = forms.CharField(label='Curso',required=False, widget=forms.TextInput(attrs={'class' : 'form-control'}))
	#adicionei essa linha de EMAIL
	email = forms.EmailField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
	modalidade = forms.ChoiceField(label='Modalidade de Inscrição', choices=MODALIDADE_CHOICES,
	 				widget=forms.Select(attrs={'onchange':'choiceFunc()'}))

	class Meta:
		model = UserProfile
		fields = ('name', 'pronome_tratamento', 'cpf','email','phone','modalidade','instituicao', 'curso','profissao', 'local_de_atuacao','password','have_article')

class AdminForm(forms.ModelForm):

	password = forms.CharField(label=("Senha"), widget=forms.PasswordInput(attrs={'placeholder' : 'Digite sua senha.'}))
	name = forms.CharField(label='Nome')
	phone = forms.CharField(label='Telefone')
	class Meta:
		model = UserProfile
		fields = ('name','email','phone','password',)

class ReceiptForm(forms.Form):
	image_file = forms.ImageField()

class ArticleForm(forms.ModelForm):
	title = forms.CharField(label=("Titulo do artigo"))
	document = forms.FileField(label="Arquivo")
	string = "Digite o nome dos autores separados por ponto e virgula em ordem de importância.\
 Até 5 (cinco) nomes: 1 autor e 4 colaboradores."
	autores = forms.CharField(label="Autores", widget=forms.Textarea( attrs={'placeholder': string}))

	class Meta:
		model = Article
		fields = ('title', 'area', 'autores', 'document',)

class ShortCourseForm(forms.ModelForm):
	class Meta:
		model = Minicurso
		fields = ('name','description','professor','begin','duration','short_course_cover')

class ArticleAnalisyForm(forms.Form):
	choices = (
		(1,'Sim'),
		(0,'Nao'),
 	)

	revision = forms.CharField(widget=forms.Textarea)
	accepted = forms.TypedChoiceField(label='Aceito ?',
						 choices=choices, widget=forms.RadioSelect, coerce=int
					)

class TalkRegisterForm(forms.ModelForm):
	class Meta:
		model = Talk
		fields = ('talk_name','talk_speaker','talk_description','talk_begin', 'talk_local', 'talk_speaker_lattes', 'talk_speaker_photo')
