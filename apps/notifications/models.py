from django.db import models


class NotificationLog(models.Model):
    """Log of WhatsApp messages sent."""

    class Status(models.TextChoices):
        SENT = 'sent', 'Enviado'
        FAILED = 'failed', 'Falhou'
        PENDING = 'pending', 'Pendente'

    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='notification_logs',
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        related_name='notification_logs',
    )
    phone = models.CharField('Telefone', max_length=20)
    message = models.TextField('Mensagem')
    status = models.CharField('Status', max_length=10, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField('Enviado em', null=True, blank=True)
    error = models.TextField('Erro', blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} - {self.status}'
