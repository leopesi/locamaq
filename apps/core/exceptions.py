"""
LocaMaq — Custom exceptions.
"""


class LocaMaqException(Exception):
    """Base exception for LocaMaq."""
    def __init__(self, message='Erro interno do sistema.', code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class EquipmentUnavailableError(LocaMaqException):
    """Raised when trying to rent an unavailable equipment."""
    def __init__(self, equipment_code=''):
        super().__init__(
            message=f'Equipamento {equipment_code} não está disponível para locação.',
            code='EQUIPMENT_UNAVAILABLE'
        )


class CustomerBlockedError(LocaMaqException):
    """Raised when trying to create rental for blocked customer."""
    def __init__(self, customer_name=''):
        super().__init__(
            message=f'Cliente "{customer_name}" está bloqueado e não pode realizar locações.',
            code='CUSTOMER_BLOCKED'
        )


class RentalAlreadyReturnedError(LocaMaqException):
    """Raised when trying to return an already returned rental."""
    def __init__(self, rental_id=None):
        super().__init__(
            message=f'Locação #{rental_id} já foi devolvida.',
            code='RENTAL_ALREADY_RETURNED'
        )


class IntegrationError(LocaMaqException):
    """Raised when an external integration fails."""
    def __init__(self, service='', detail=''):
        super().__init__(
            message=f'Erro na integração com {service}: {detail}',
            code='INTEGRATION_ERROR'
        )
