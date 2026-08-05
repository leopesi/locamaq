from django.db import models


class Promotion(models.Model):
    """Promotional broadcast message."""

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='promotions',
    )
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensagem')
    image = models.ImageField('Imagem', upload_to='promotions/', blank=True, null=True)
    sent_at = models.DateTimeField('Enviado em', null=True, blank=True)
    recipients_count = models.PositiveIntegerField('Destinatários', default=0)
    send_log = models.TextField('Relatório de Envio', blank=True,
        help_text='Log detalhado de cada tentativa de envio')
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Promoção'
        verbose_name_plural = 'Promoções'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def send_status(self):
        if not self.sent_at:
            return 'pending'
        if self.recipients_count == 0:
            return 'failed'
        return 'sent'
