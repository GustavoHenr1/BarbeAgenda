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


def telefone(erros, valor, campo="Telefone", obrigatorio_=True):
    v = texto(valor)
    if not v:
        if obrigatorio_:
            erros.append(f"O campo {campo} é obrigatório.")
        return
    digitos = re.sub(r"\D", "", v)
    if len(digitos) not in (10, 11):
        erros.append(f"{campo} inválido. Use DDD + número, ex.: (11) 91234-5678.")


def email(erros, valor):
    v = texto(valor)
    if v and not _RE_EMAIL.match(v):
        erros.append("E-mail inválido.")


def formatar_telefone(valor):
    d = re.sub(r"\D", "", valor or "")
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return texto(valor)
