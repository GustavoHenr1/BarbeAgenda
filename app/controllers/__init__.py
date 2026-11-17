"""Camada CONTROLLER (MVC): recebe as requisições, chama os models e escolhe a view."""
from . import (
    agendamento_controller,
    auth_controller,
    cliente_controller,
    dashboard_controller,
    profissional_controller,
    servico_controller,
)

BLUEPRINTS = [
    auth_controller.bp,
    dashboard_controller.bp,
    cliente_controller.bp,
    profissional_controller.bp,
    servico_controller.bp,
    agendamento_controller.bp,
]
