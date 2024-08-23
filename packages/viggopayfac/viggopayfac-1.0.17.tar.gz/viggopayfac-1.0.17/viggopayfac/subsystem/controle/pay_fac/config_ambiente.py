from viggopayfac.subsystem.controle.configuracao_pay_fac.resource \
    import ConfiguracaoPayFacTipo as cpf_tipo
from viggocore.common import exception
import os


def get_api_payfac():
    ambiente = os.getenv('VIGGOPAYFAC_AMBIENTE_API', None)
    if ambiente is None:
        raise exception.BadRequest(
            'A variável VIGGOPAYFAC_AMBIENTE_API não foi encontrada no .env')
    if ambiente == 'PRODUCAO':
        return cpf_tipo.PRODUCAO
    elif ambiente == 'HOMOLOGACAO':
        return cpf_tipo.HOMOLOGACAO
    else:
        raise exception.BadRequest(
            'O valor da variável VIGGOPAYFAC_AMBIENTE_API deve ' +
            'ser PRODUCAO ou HOMOLOGACAO.')


def get_secret_key():
    ambiente = os.getenv('VIGGOPAYFAC_AMBIENTE_API', None)
    if ambiente is None:
        raise exception.BadRequest(
            'A variável VIGGOPAYFAC_AMBIENTE_API não foi encontrada no .env')
    if ambiente == 'PRODUCAO':
        return 'B3430FF3-1E93-41B8-A882-B087BBAA1613'
    elif ambiente == 'HOMOLOGACAO':
        return '54B9D213-B30C-4E3B-A759-AEEB554513BB'
    else:
        raise exception.BadRequest(
            'O valor da variável VIGGOPAYFAC_AMBIENTE_API deve ' +
            'ser PRODUCAO ou HOMOLOGACAO.')
