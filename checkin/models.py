from django.db import models


class Imovel(models.Model):
    nome_apartamento = models.CharField(max_length=200)
    nome_rua = models.CharField(max_length=200)
    endereco_completo = models.CharField(max_length=255)

    imagem_apartamento = models.ImageField(
        upload_to='apartamentos/',
        blank=True,
        null=True
    )

    aviso_importante = models.TextField(
        blank=True,
        help_text='Texto do card de avisos importantes no topo da página aprovada.'
    )

    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Imóvel'
        verbose_name_plural = 'Imóveis'
        ordering = ['nome_apartamento', 'id']

    def __str__(self):
        return self.nome_apartamento


class ItemGuiaImovel(models.Model):
    GUIA_CHOICES = [
        ('estadia', 'Sua Estadia'),
        ('imovel', 'Guia do Imóvel'),
        ('area', 'Guia da Área'),
    ]

    TIPO_CONTEUDO_CHOICES = [
        ('texto', 'Texto'),
        ('imagem', 'Imagem'),
    ]

    imovel = models.ForeignKey(
        Imovel,
        on_delete=models.CASCADE,
        related_name='itens_guia'
    )

    guia = models.CharField(max_length=20, choices=GUIA_CHOICES)
    titulo = models.CharField(max_length=200)

    tipo_conteudo = models.CharField(
        max_length=20,
        choices=TIPO_CONTEUDO_CHOICES,
        default='texto'
    )

    conteudo = models.TextField(blank=True)

    imagem = models.ImageField(
        upload_to='guias/',
        blank=True,
        null=True
    )

    ordem = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Item da guia do imóvel'
        verbose_name_plural = 'Itens das guias do imóvel'
        ordering = ['guia', 'ordem', 'id']

    def __str__(self):
        return f"{self.imovel.nome_apartamento} - {self.get_guia_display()} - {self.titulo}"


class ReservaImovel(models.Model):
    imovel = models.ForeignKey(
        Imovel,
        on_delete=models.CASCADE,
        related_name='reservas'
    )

    codigo_reserva = models.CharField(
        max_length=50,
        unique=True
    )

    nome_imovel = models.CharField(
        max_length=200,
        blank=True,
        help_text='Opcional. Se ficar vazio, usa o nome do imóvel.'
    )

    endereco = models.CharField(
        max_length=255,
        blank=True,
        help_text='Opcional. Se ficar vazio, usa o endereço do imóvel.'
    )

    data_checkin = models.DateTimeField()
    data_checkout = models.DateTimeField()
    quantidade_hospedes = models.PositiveIntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva do imóvel'
        verbose_name_plural = 'Reservas dos imóveis'
        ordering = ['-data_checkin', 'id']

    def __str__(self):
        return f"{self.codigo_reserva} - {self.nome_imovel_exibicao}"

    @property
    def nome_imovel_exibicao(self):
        return self.nome_imovel or self.imovel.nome_apartamento

    @property
    def endereco_exibicao(self):
        return self.endereco or self.imovel.endereco_completo


class Checkin(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]

    reserva = models.OneToOneField(
        ReservaImovel,
        on_delete=models.CASCADE,
        related_name='checkin'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente'
    )

    aceita_termos = models.BooleanField(default=False)
    aceita_uso_imagem = models.BooleanField(default=False)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Check-in'
        verbose_name_plural = 'Check-ins'
        ordering = ['-criado_em', 'id']

    def __str__(self):
        return f"Check-in {self.reserva.codigo_reserva}"


class Hospede(models.Model):
    TIPO_HOSPEDE_CHOICES = [
        ('titular', 'Titular'),
        ('acompanhante', 'Acompanhante'),
    ]

    checkin = models.ForeignKey(
        Checkin,
        on_delete=models.CASCADE,
        related_name='hospedes'
    )

    tipo_hospede = models.CharField(
        max_length=20,
        choices=TIPO_HOSPEDE_CHOICES,
        default='acompanhante'
    )

    nome_completo = models.CharField(max_length=200)
    estrangeiro = models.BooleanField(default=False)

    documento = models.CharField(
        max_length=50,
        blank=True,
        help_text='CPF para brasileiros ou passaporte/RNE/outro documento para estrangeiros.'
    )

    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)

    cep = models.CharField(max_length=9, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    rua = models.CharField(max_length=200, blank=True)
    complemento = models.CharField(max_length=200, blank=True)

    foto_frente = models.ImageField(upload_to='documentos/', blank=True, null=True)
    foto_verso = models.ImageField(upload_to='documentos/', blank=True, null=True)
    selfie_rosto = models.ImageField(upload_to='documentos/', blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hóspede'
        verbose_name_plural = 'Hóspedes'
        ordering = ['id']

    def __str__(self):
        return f"{self.nome_completo} - {self.checkin.reserva.codigo_reserva}"

    @property
    def label_documento(self):
        if self.estrangeiro:
            return 'Documento'
        return 'CPF'