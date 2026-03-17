import re
import requests

from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from validate_docbr import CPF

from .models import (
    Checkin,
    Hospede,
    Imovel,
    ItemGuiaImovel,
    ReservaImovel,
)


class CheckinForm(forms.ModelForm):
    class Meta:
        model = Checkin
        fields = [
            'aceita_termos',
            'aceita_uso_imagem',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['aceita_termos'].required = True
        self.fields['aceita_uso_imagem'].required = True

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class HospedeForm(forms.ModelForm):
    class Meta:
        model = Hospede
        fields = [
            'tipo_hospede',
            'nome_completo',
            'estrangeiro',
            'documento',
            'email',
            'telefone',
            'data_nascimento',
            'cep',
            'cidade',
            'estado',
            'numero',
            'rua',
            'complemento',
            'foto_frente',
            'foto_verso',
            'selfie_rosto',
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        obrigatorios = [
            'nome_completo',
            'documento',
            'email',
            'telefone',
            'data_nascimento',
            'foto_frente',
            'foto_verso',
            'selfie_rosto',
        ]

        for campo in obrigatorios:
            self.fields[campo].required = True

        for _, field in self.fields.items():
            field.widget.attrs['class'] = (
                field.widget.attrs.get('class', '') + ' form-control'
            ).strip()

        campos_endereco = ['cep', 'cidade', 'estado', 'numero', 'rua']
        for campo in campos_endereco:
            self.fields[campo].required = False

    def clean_nome_completo(self):
        nome = (self.cleaned_data.get('nome_completo') or '').strip()

        if len(nome) < 5:
            raise forms.ValidationError('Digite o nome completo do hóspede.')

        return nome

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Digite um e-mail válido.')

        return email

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone') or ''
        telefone_limpo = re.sub(r'\D', '', telefone)

        if len(telefone_limpo) < 8 or len(telefone_limpo) > 15:
            raise forms.ValidationError('Telefone inválido.')

        return telefone_limpo

    def clean_documento(self):
        documento = (self.cleaned_data.get('documento') or '').strip()
        estrangeiro = self.cleaned_data.get('estrangeiro')

        if not documento:
            raise forms.ValidationError('Este campo é obrigatório.')

        if estrangeiro:
            documento_limpo = re.sub(r'[^A-Za-z0-9\-\./ ]', '', documento).strip()

            if len(documento_limpo) < 4:
                raise forms.ValidationError('Informe um documento válido.')

            return documento_limpo

        documento_limpo = re.sub(r'\D', '', documento)

        cpf_validator = CPF()
        if not cpf_validator.validate(documento_limpo):
            raise forms.ValidationError('CPF inválido.')

        return documento_limpo

    def clean_cep(self):
        cep = self.cleaned_data.get('cep') or ''
        cep_limpo = re.sub(r'\D', '', cep)

        if not cep_limpo:
            return ''

        if len(cep_limpo) != 8:
            raise forms.ValidationError('CEP inválido.')

        try:
            response = requests.get(
                f'https://viacep.com.br/ws/{cep_limpo}/json/',
                timeout=5
            )
            data = response.json()

            if data.get('erro'):
                raise forms.ValidationError('CEP não encontrado.')
        except requests.RequestException:
            raise forms.ValidationError('Erro ao validar o CEP.')

        return cep_limpo

    def _validar_imagem(self, arquivo, nome_campo):
        if not arquivo:
            raise forms.ValidationError('Este arquivo é obrigatório.')

        tamanho_maximo = 5 * 1024 * 1024
        if arquivo.size > tamanho_maximo:
            raise forms.ValidationError('A imagem deve ter no máximo 5MB.')

        nome = (arquivo.name or '').lower()
        extensoes_permitidas = ('.jpg', '.jpeg', '.png', '.webp')
        if not nome.endswith(extensoes_permitidas):
            raise forms.ValidationError(
                f'{nome_campo}: envie apenas JPG, JPEG, PNG ou WEBP.'
            )

        content_type = getattr(arquivo, 'content_type', '')
        tipos_permitidos = ['image/jpeg', 'image/png', 'image/webp']
        if content_type and content_type not in tipos_permitidos:
            raise forms.ValidationError(
                f'{nome_campo}: tipo de arquivo não permitido.'
            )

        return arquivo

    def clean_foto_frente(self):
        arquivo = self.cleaned_data.get('foto_frente')
        return self._validar_imagem(arquivo, 'Foto da frente do documento')

    def clean_foto_verso(self):
        arquivo = self.cleaned_data.get('foto_verso')
        return self._validar_imagem(arquivo, 'Foto do verso do documento')

    def clean_selfie_rosto(self):
        arquivo = self.cleaned_data.get('selfie_rosto')
        return self._validar_imagem(arquivo, 'Selfie do rosto')


class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        fields = [
            'nome_apartamento',
            'nome_rua',
            'endereco_completo',
            'imagem_apartamento',
            'aviso_importante',
            'ativo',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ItemGuiaImovelForm(forms.ModelForm):
    class Meta:
        model = ItemGuiaImovel
        fields = [
            'guia',
            'titulo',
            'tipo_conteudo',
            'conteudo',
            'imagem',
            'ordem',
            'ativo',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ReservaImovelAdminForm(forms.ModelForm):
    class Meta:
        model = ReservaImovel
        fields = [
            'imovel',
            'codigo_reserva',
            'nome_imovel',
            'endereco',
            'data_checkin',
            'data_checkout',
            'quantidade_hospedes',
        ]
        widgets = {
            'data_checkin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_checkout': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'