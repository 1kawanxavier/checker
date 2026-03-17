from django.urls import path

from .views import (

    # CHECK-IN
    formulario_checkin,

    # LOGIN ADMIN
    admin_login_view,
    admin_logout_view,

    # RESERVAS
    admin_painel_reservas,
    admin_detalhe_reserva,
    admin_aprovar_reserva,
    admin_rejeitar_reserva,

    # IMÓVEIS
    admin_painel_imoveis,
    admin_novo_imovel,
    admin_editar_imovel,
    admin_detalhe_imovel,

    # ITENS DA GUIA
    admin_novo_item_guia,
    admin_editar_item_guia,

    # RESERVA ADMIN
    admin_nova_reserva,
)


urlpatterns = [

    # ========================================
    # CHECK-IN DO HÓSPEDE
    # ========================================

    path(
        'checkin/<str:codigo_reserva>/',
        formulario_checkin,
        name='form_checkin'
    ),

    # ========================================
    # LOGIN ADMIN
    # ========================================

    path(
        'admin-login/',
        admin_login_view,
        name='admin_login'
    ),

    path(
        'admin-logout/',
        admin_logout_view,
        name='admin_logout'
    ),

    # ========================================
    # PAINEL ADMIN - RESERVAS
    # ========================================

    path(
        'painel-admin/',
        admin_painel_reservas,
        name='admin_painel_reservas'
    ),

    path(
        'painel-admin/reserva/nova/',
        admin_nova_reserva,
        name='admin_nova_reserva'
    ),

    path(
        'painel-admin/reserva/<str:codigo_reserva>/',
        admin_detalhe_reserva,
        name='admin_detalhe_reserva'
    ),

    path(
        'painel-admin/reserva/<str:codigo_reserva>/aprovar/',
        admin_aprovar_reserva,
        name='admin_aprovar_reserva'
    ),

    path(
        'painel-admin/reserva/<str:codigo_reserva>/rejeitar/',
        admin_rejeitar_reserva,
        name='admin_rejeitar_reserva'
    ),

    # ========================================
    # PAINEL ADMIN - IMÓVEIS
    # ========================================

    path(
        'painel-admin/imoveis/',
        admin_painel_imoveis,
        name='admin_painel_imoveis'
    ),

    path(
        'painel-admin/imoveis/novo/',
        admin_novo_imovel,
        name='admin_novo_imovel'
    ),

    path(
        'painel-admin/imoveis/<int:imovel_id>/',
        admin_detalhe_imovel,
        name='admin_detalhe_imovel'
    ),

    path(
        'painel-admin/imoveis/<int:imovel_id>/editar/',
        admin_editar_imovel,
        name='admin_editar_imovel'
    ),

    # ========================================
    # ITENS DA GUIA DO IMÓVEL
    # ========================================

    path(
        'painel-admin/imoveis/<int:imovel_id>/itens/novo/',
        admin_novo_item_guia,
        name='admin_novo_item_guia'
    ),

    path(
        'painel-admin/itens/<int:item_id>/editar/',
        admin_editar_item_guia,
        name='admin_editar_item_guia'
    ),
]