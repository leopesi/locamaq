from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse

from apps.rentals.models import Rental


@login_required
def generate_pdf(request, rental_id):
    """Generate a printable receipt for a rental (HTML optimized for print)."""
    rental = get_object_or_404(Rental, pk=rental_id, tenant=request.tenant)
    items = rental.items.select_related('equipment').all()

    html_content = render_to_string('documents/receipt_pdf.html', {
        'rental': rental,
        'items': items,
        'tenant': request.tenant,
    })

    # Try WeasyPrint first
    try:
        from weasyprint import HTML
        pdf_file = HTML(string=html_content).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="comprovante_locacao_{rental.pk}.pdf"'
        return response
    except Exception:
        # Fallback: render HTML optimized for browser print (Ctrl+P)
        return HttpResponse(html_content)
