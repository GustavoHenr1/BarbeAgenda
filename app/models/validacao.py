"""Funções de validação reutilizadas pelos models."""
import re

_RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def texto(valor):
    return (valor or "").strip()


def obrigatorio(erros, valor, campo):
    if not texto(valor):
        erros.append(f"O campo {campo} é obrigatório.")


def tamanho_max(erros, valor, maximo, campo):
    if len(texto(valor)) > maximo:
        erros.append(f"O campo {campo} deve ter no máximo {maximo} caracteres.")


def _digitos_telefone(valor):
    """Somente os dígitos, sem o código do país (+55) se ele tiver sido digitado."""
    d = re.sub(r"\D", "", valor or "")
    if len(d) in (12, 13) and d.startswith("55"):
        d = d[2:]
    return d


def telefone(erros, valor, campo="Telefone", obrigatorio_=True):
    v = texto(valor)
    if not v:
        if obrigatorio_:
            erros.append(f"O campo {campo} é obrigatório.")
        return
    digitos = _digitos_telefone(v)
    if len(digitos) not in (10, 11):
        erros.append(f"{campo} inválido. Use DDD + número, ex.: (11) 91234-5678.")


def email(erros, valor, obrigatorio_=False):
    v = texto(valor)
    if not v:
        if obrigatorio_:
            erros.append("O campo E-mail é obrigatório.")
        return
    if not _RE_EMAIL.match(v):
        erros.append("E-mail inválido.")


def formatar_telefone(valor):
    d = _digitos_telefone(valor)
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return texto(valor)
