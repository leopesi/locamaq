from django.db import models


class Document(models.Model):
    """Generated PDF document for a rental."""

    rental = models.ForeignKey(
        'rentals.Rental',
        on_delete=models.CASCADE,
        related_name='documents',
    )
    file = models.FileField('Arquivo PDF', upload_to='documents/pdfs/')
    generated_at = models.DateTimeField('Gerado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-generated_at']

    def __str__(self):
        return f'Comprovante - Locação #{self.rental_id}'
