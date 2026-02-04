import os
from django.conf import settings

SEQ_PATH = os.path.join(settings.BASE_DIR, "controle_orcamento.txt")


def ler_numero_orcamento():
    """
    Apenas lê o número atual (não incrementa)
    """

    if not os.path.exists(SEQ_PATH):
        with open(SEQ_PATH, "w") as f:
            f.write("1")

    with open(SEQ_PATH, "r") as f:
        numero = int(f.read().strip())

    return numero


def gerar_proximo_orcamento():
    """
    Lê e incrementa
    """

    numero = ler_numero_orcamento()

    with open(SEQ_PATH, "w") as f:
        f.write(str(numero + 1))

    return numero
