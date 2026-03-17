from django.contrib import admin

from .models import (
    Imovel,
    ItemGuiaImovel,
    ReservaImovel,
    Checkin,
    Hospede,
)


class HospedeInline(admin.TabularInline):
    model = Hospede
    extra = 0

    fields = (
        'tipo_hospede',
        'nome_completo',
        'estrangeiro',
        'documento',
        'email',
        'telefone',
        'data_nascimento',
    )


class ItemGuiaImovelInline(admin.StackedInline):
    model = ItemGuiaImovel
    extra = 1

    fields = (
        'guia',
        'titulo',
        'tipo_conteudo',
        'conteudo',
        'imagem',
        'ordem',
        'ativo',
    )

    ordering = ('guia', 'ordem', 'id')


@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):

    list_display = (
        'nome_apartamento',
        'nome_rua',
        'ativo',
        'criado_em',
        'atualizado_em',
    )

    search_fields = (
        'nome_apartamento',
        'nome_rua',
        'endereco_completo',
    )

    list_filter = (
        'ativo',
        'criado_em',
        'atualizado_em',
    )

    ordering = ('nome_apartamento', 'id')

    inlines = [ItemGuiaImovelInline]

    fieldsets = (

        ('Informações do Imóvel', {
            'fields': (
                'nome_apartamento',
                'nome_rua',
                'endereco_completo',
                'imagem_apartamento',
            )
        }),

        ('Aviso Importante', {
            'fields': ('aviso_importante',)
        }),

        ('Controle', {
            'fields': ('ativo',)
        }),
    )


@admin.register(ItemGuiaImovel)
class ItemGuiaImovelAdmin(admin.ModelAdmin):

    list_display = (
        'titulo',
        'guia',
        'imovel',
        'tipo_conteudo',
        'ordem',
        'ativo',
    )

    list_filter = (
        'guia',
        'tipo_conteudo',
        'ativo',
    )

    search_fields = (
        'titulo',
        'conteudo',
        'imovel__nome_apartamento',
        'imovel__nome_rua',
    )

    ordering = ('guia', 'ordem', 'id')


@admin.register(ReservaImovel)
class ReservaImovelAdmin(admin.ModelAdmin):

    list_display = (
        'codigo_reserva',
        'imovel',
        'nome_imovel_resolvido',
        'endereco_resolvido',
        'data_checkin',
        'data_checkout',
        'quantidade_hospedes',
        'criado_em',
    )

    search_fields = (
        'codigo_reserva',
        'nome_imovel',
        'endereco',
        'imovel__nome_apartamento',
        'imovel__nome_rua',
        'imovel__endereco_completo',
    )

    list_filter = (
        'data_checkin',
        'data_checkout',
        'criado_em',
        'imovel',
    )

    ordering = ('-data_checkin',)

    fields = (
        'imovel',
        'codigo_reserva',
        'nome_imovel',
        'endereco',
        'data_checkin',
        'data_checkout',
        'quantidade_hospedes',
    )

    def nome_imovel_resolvido(self, obj):
        return obj.nome_imovel_exibicao

    nome_imovel_resolvido.short_description = 'Nome imóvel'

    def endereco_resolvido(self, obj):
        return obj.endereco_exibicao

    endereco_resolvido.short_description = 'Endereço'


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):

    list_display = (
        'reserva',
        'status',
        'aceita_termos',
        'aceita_uso_imagem',
        'criado_em',
        'atualizado_em',
    )

    list_filter = (
        'status',
        'criado_em',
        'atualizado_em',
    )

    search_fields = (
        'reserva__codigo_reserva',
        'reserva__nome_imovel',
        'reserva__imovel__nome_apartamento',
    )

    ordering = ('-criado_em',)

    inlines = [HospedeInline]


@admin.register(Hospede)
class HospedeAdmin(admin.ModelAdmin):

    list_display = (
        'nome_completo',
        'tipo_hospede',
        'checkin',
        'estrangeiro',
        'documento',
        'telefone',
        'email',
        'criado_em',
    )

    list_filter = (
        'tipo_hospede',
        'estrangeiro',
        'criado_em',
    )

    search_fields = (
        'nome_completo',
        'documento',
        'email',
        'checkin__reserva__codigo_reserva',
        'checkin__reserva__imovel__nome_apartamento',
    )

    ordering = ('-criado_em',)