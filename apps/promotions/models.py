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
