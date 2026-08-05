from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse

from apps.rentals.models import Rental


@login_required
def generate_pdf(request, rental_id):
    """Generate a PDF receipt for a rental."""
    rental = get_object_or_404(Rental, pk=rental_id, tenant=request.tenant)
    items = rental.items.select_related('equipment').all()

    html_content = render_to_string('documents/receipt_pdf.html', {
        'rental': rental,
        'items': items,
        'tenant': request.tenant,
    })

    try:
        from weasyprint import HTML
        pdf_file = HTML(string=html_content).write_pdf()

        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprovante_locacao_{rental.pk}.pdf"'
        return response
    except ImportError:
        # Fallback if weasyprint not installed
        return HttpResponse(html_content)
