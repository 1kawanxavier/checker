from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django_ratelimit.decorators import ratelimit

from .forms import (
    CheckinForm,
    HospedeForm,
    ImovelForm,
    ItemGuiaImovelForm,
    ReservaImovelAdminForm,
)
from .models import (
    ReservaImovel,
    Checkin,
    Hospede,
    Imovel,
    ItemGuiaImovel,
)


def admin_required(user):
    return user.is_authenticated and user.is_staff


def checkin_foi_enviado(checkin):
    if checkin.aceita_termos or checkin.aceita_uso_imagem:
        return True

    for hospede in checkin.hospedes.all():
        if (
            hospede.nome_completo or
            hospede.documento or
            hospede.email or
            hospede.telefone or
            hospede.data_nascimento or
            hospede.cep or
            hospede.cidade or
            hospede.estado or
            hospede.numero or
            hospede.rua or
            hospede.complemento or
            hospede.foto_frente or
            hospede.foto_verso or
            hospede.selfie_rosto
        ):
            return True

    return False


@ratelimit(key='ip', rate='10/m', method=['GET', 'POST'], block=True)
def formulario_checkin(request, codigo_reserva):
    reserva = get_object_or_404(
        ReservaImovel.objects.select_related('imovel'),
        codigo_reserva=codigo_reserva
    )
    checkin, _ = Checkin.objects.get_or_create(reserva=reserva)
    imovel = reserva.imovel

    if checkin.status == 'aprovado':
        dados_estadia = []
        guia_imovel = []
        guia_area = []

        if imovel and imovel.ativo:
            itens_estadia = imovel.itens_guia.filter(
                guia='estadia',
                ativo=True
            ).order_by('ordem', 'id')

            itens_imovel = imovel.itens_guia.filter(
                guia='imovel',
                ativo=True
            ).order_by('ordem', 'id')

            itens_area = imovel.itens_guia.filter(
                guia='area',
                ativo=True
            ).order_by('ordem', 'id')

            for item in itens_estadia:
                dados_estadia.append({
                    'titulo': item.titulo,
                    'tipo': item.tipo_conteudo,
                    'conteudo': item.conteudo,
                    'imagem': item.imagem.url if item.imagem else None,
                })

            for item in itens_imovel:
                guia_imovel.append({
                    'titulo': item.titulo,
                    'tipo': item.tipo_conteudo,
                    'conteudo': item.conteudo,
                    'imagem': item.imagem.url if item.imagem else None,
                })

            for item in itens_area:
                guia_area.append({
                    'titulo': item.titulo,
                    'tipo': item.tipo_conteudo,
                    'conteudo': item.conteudo,
                    'imagem': item.imagem.url if item.imagem else None,
                })

        return render(request, 'checkin/aprovado.html', {
            'checkin': checkin,
            'reserva': reserva,
            'imovel': imovel,
            'nome_imovel_exibicao': reserva.nome_imovel_exibicao,
            'endereco_exibicao': reserva.endereco_exibicao,
            'dados_estadia': dados_estadia,
            'guia_imovel': guia_imovel,
            'guia_area': guia_area,
        })

    if checkin.status == 'rejeitado':
        return render(request, 'checkin/rejeitado.html', {
            'checkin': checkin,
            'reserva': reserva,
            'imovel': imovel,
            'nome_imovel_exibicao': reserva.nome_imovel_exibicao,
            'endereco_exibicao': reserva.endereco_exibicao,
        })

    hospedes_existentes = list(checkin.hospedes.order_by('id'))

    while len(hospedes_existentes) < reserva.quantidade_hospedes:
        tipo = 'titular' if len(hospedes_existentes) == 0 else 'acompanhante'
        novo_hospede = Hospede.objects.create(
            checkin=checkin,
            tipo_hospede=tipo,
            nome_completo=''
        )
        hospedes_existentes.append(novo_hospede)

    if request.method == 'POST':
        checkin_form = CheckinForm(request.POST, instance=checkin)
        hospede_forms = []
        hospedes_validos = True

        for i, hospede in enumerate(hospedes_existentes):
            form = HospedeForm(
                request.POST,
                request.FILES,
                instance=hospede,
                prefix=f'hospede_{i}'
            )
            hospede_forms.append(form)

            if not form.is_valid():
                hospedes_validos = False

        if checkin_form.is_valid() and hospedes_validos:
            checkin = checkin_form.save(commit=False)
            checkin.status = 'pendente'
            checkin.save()

            for form in hospede_forms:
                form.save()

            return redirect('form_checkin', codigo_reserva=reserva.codigo_reserva)

    else:
        if checkin.status == 'pendente' and checkin_foi_enviado(checkin):
            return render(request, 'checkin/sucesso.html', {
                'checkin': checkin,
                'reserva': reserva,
                'imovel': imovel,
                'nome_imovel_exibicao': reserva.nome_imovel_exibicao,
                'endereco_exibicao': reserva.endereco_exibicao,
            })

        checkin_form = CheckinForm(instance=checkin)
        hospede_forms = []

        for i, hospede in enumerate(hospedes_existentes):
            form = HospedeForm(
                instance=hospede,
                prefix=f'hospede_{i}'
            )
            hospede_forms.append(form)

    return render(request, 'checkin/form_checkin.html', {
        'checkin_form': checkin_form,
        'hospede_forms': hospede_forms,
        'checkin': checkin,
        'reserva': reserva,
        'imovel': imovel,
        'nome_imovel_exibicao': reserva.nome_imovel_exibicao,
        'endereco_exibicao': reserva.endereco_exibicao,
    })


def sucesso(request):
    return render(request, 'checkin/sucesso.html')


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_painel_reservas')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_painel_reservas')

        messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'checkin/admin_login.html')


@login_required
@user_passes_test(admin_required)
def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')


@login_required
@user_passes_test(admin_required)
def admin_painel_reservas(request):
    status = request.GET.get('status')

    reservas = ReservaImovel.objects.select_related(
        'checkin',
        'imovel'
    ).order_by('-data_checkin')

    if status:
        reservas = reservas.filter(checkin__status=status)

    total_reservas = reservas.count()
    total_com_checkin = reservas.filter(checkin__isnull=False).count()

    return render(request, 'checkin/admin_painel_reservas.html', {
        'reservas': reservas,
        'status_atual': status,
        'total_reservas': total_reservas,
        'total_com_checkin': total_com_checkin,
    })


@login_required
@user_passes_test(admin_required)
def admin_detalhe_reserva(request, codigo_reserva):
    reserva = get_object_or_404(
        ReservaImovel.objects.select_related('checkin', 'imovel'),
        codigo_reserva=codigo_reserva
    )

    checkin, _ = Checkin.objects.get_or_create(reserva=reserva)
    hospedes = checkin.hospedes.all().order_by('id')
    imovel = reserva.imovel

    link_checkin = request.build_absolute_uri(
        reverse('form_checkin', args=[reserva.codigo_reserva])
    )

    return render(request, 'checkin/admin_detalhe_reserva.html', {
        'reserva': reserva,
        'checkin': checkin,
        'hospedes': hospedes,
        'imovel': imovel,
        'nome_imovel_exibicao': reserva.nome_imovel_exibicao,
        'endereco_exibicao': reserva.endereco_exibicao,
        'link_checkin': link_checkin,
    })


@login_required
@user_passes_test(admin_required)
def admin_aprovar_reserva(request, codigo_reserva):
    reserva = get_object_or_404(ReservaImovel, codigo_reserva=codigo_reserva)
    checkin, _ = Checkin.objects.get_or_create(reserva=reserva)

    checkin.status = 'aprovado'
    checkin.save()

    messages.success(request, 'Reserva aprovada com sucesso.')
    return redirect('admin_detalhe_reserva', codigo_reserva=codigo_reserva)


@login_required
@user_passes_test(admin_required)
def admin_rejeitar_reserva(request, codigo_reserva):
    reserva = get_object_or_404(ReservaImovel, codigo_reserva=codigo_reserva)
    checkin, _ = Checkin.objects.get_or_create(reserva=reserva)

    checkin.status = 'rejeitado'
    checkin.save()

    messages.success(request, 'Reserva rejeitada com sucesso.')
    return redirect('admin_detalhe_reserva', codigo_reserva=codigo_reserva)


@login_required
@user_passes_test(admin_required)
def admin_painel_imoveis(request):
    imoveis = Imovel.objects.all().order_by('nome_apartamento')

    return render(request, 'checkin/admin_painel_imoveis.html', {
        'imoveis': imoveis,
    })


@login_required
@user_passes_test(admin_required)
def admin_novo_imovel(request):
    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES)
        if form.is_valid():
            imovel = form.save()
            messages.success(request, 'Imóvel cadastrado com sucesso.')
            return redirect('admin_detalhe_imovel', imovel_id=imovel.id)
    else:
        form = ImovelForm()

    return render(request, 'checkin/admin_imovel_form.html', {
        'form': form,
        'titulo': 'Novo imóvel',
    })


@login_required
@user_passes_test(admin_required)
def admin_editar_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)

    if request.method == 'POST':
        form = ImovelForm(request.POST, request.FILES, instance=imovel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imóvel atualizado com sucesso.')
            return redirect('admin_detalhe_imovel', imovel_id=imovel.id)
    else:
        form = ImovelForm(instance=imovel)

    return render(request, 'checkin/admin_imovel_form.html', {
        'form': form,
        'titulo': 'Editar imóvel',
        'imovel': imovel,
    })


@login_required
@user_passes_test(admin_required)
def admin_detalhe_imovel(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)
    itens = imovel.itens_guia.all().order_by('guia', 'ordem', 'id')
    reservas = imovel.reservas.all().order_by('-data_checkin')

    return render(request, 'checkin/admin_imovel_detalhe.html', {
        'imovel': imovel,
        'itens': itens,
        'reservas': reservas,
    })


@login_required
@user_passes_test(admin_required)
def admin_novo_item_guia(request, imovel_id):
    imovel = get_object_or_404(Imovel, id=imovel_id)

    if request.method == 'POST':
        form = ItemGuiaImovelForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.imovel = imovel
            item.save()
            messages.success(request, 'Item da guia cadastrado com sucesso.')
            return redirect('admin_detalhe_imovel', imovel_id=imovel.id)
    else:
        form = ItemGuiaImovelForm()

    return render(request, 'checkin/admin_item_guia_form.html', {
        'form': form,
        'imovel': imovel,
        'titulo': 'Novo item da guia',
    })


@login_required
@user_passes_test(admin_required)
def admin_editar_item_guia(request, item_id):
    item = get_object_or_404(ItemGuiaImovel, id=item_id)

    if request.method == 'POST':
        form = ItemGuiaImovelForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item da guia atualizado com sucesso.')
            return redirect('admin_detalhe_imovel', imovel_id=item.imovel.id)
    else:
        form = ItemGuiaImovelForm(instance=item)

    return render(request, 'checkin/admin_item_guia_form.html', {
        'form': form,
        'imovel': item.imovel,
        'item': item,
        'titulo': 'Editar item da guia',
    })


@login_required
@user_passes_test(admin_required)
def admin_nova_reserva(request):
    if request.method == 'POST':
        form = ReservaImovelAdminForm(request.POST)
        if form.is_valid():
            reserva = form.save()
            messages.success(request, 'Reserva cadastrada com sucesso.')
            return redirect('admin_detalhe_reserva', codigo_reserva=reserva.codigo_reserva)
    else:
        form = ReservaImovelAdminForm()

    return render(request, 'checkin/admin_reserva_form.html', {
        'form': form,
        'titulo': 'Nova reserva',
    })