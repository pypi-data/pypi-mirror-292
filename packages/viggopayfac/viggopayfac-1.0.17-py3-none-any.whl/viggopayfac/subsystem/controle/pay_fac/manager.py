import flask
import json
import requests
import os
from datetime import datetime
from viggocore.common.subsystem import operation, manager
from viggocore.common import exception
from viggopayfac.subsystem.controle.configuracao_pay_fac.resource \
    import ConfiguracaoPayFacTipo as c_payfac_tipo
from viggopayfac.subsystem.controle.pay_fac.transaction_hash \
    import TransactionHash


# classes das chamadas a api da PayFac envolvendo Conta
class CriarConta(operation.List):

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        url = self.manager.get_endpoint('/v1/accounts', ambiente)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_id_cnpj(**kwargs)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class GetConta(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_id(**kwargs)
        url = self.manager.get_endpoint(f'/v1/accounts/{account_id}', ambiente)
        return self.manager.executar_requisicao(
            'GET', url, ambiente=ambiente, transaction_hash=transaction_hash)


class AddChavePix(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url_for_hash = f'post:/v1/accounts/{account_id}/aliases:'
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}/aliases', ambiente)
        transaction_hash = self.manager._get_transaction_hash_url(
            url=url_for_hash)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class ListChavesPix(operation.List):

    def pre(self, **kwargs):
        chamada_interna = kwargs.get('chamada_interna', False)
        # valida se o usuario do token está ligado a conta
        if chamada_interna is False:
            self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}/aliases', ambiente)
        return self.manager.executar_requisicao(
            'GET', url, ambiente=ambiente)


class AtualizarConta(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}', ambiente)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_id_cnpj(**kwargs)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class DeletarChavePix(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        alias = self.manager.get_field('alias', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}/aliases/{alias}', ambiente)
        transaction_hash = self.manager._get_transaction_hash_url(
            f'delete:/v1/accounts/{account_id}/aliases/{alias}')
        return self.manager.executar_requisicao(
            'DELETE', url, ambiente=ambiente, transaction_hash=transaction_hash)


class InativarConta(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}', ambiente)
        return self.manager.executar_requisicao(
            'DELETE', url, ambiente=ambiente)


class GerarQrcode(operation.List):

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        url = self.manager.get_endpoint('/v1/payments', ambiente)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_four_fields_2(**kwargs)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class GerarQrcodeCobranca(operation.List):

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        url = self.manager.get_endpoint('/v1/payments', ambiente)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_four_fields_2(**kwargs)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class RealizarTransferenciaInterna(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        url = self.manager.get_endpoint('/v1/payments', ambiente)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente)


class EstornarTransferenciaInterna(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        transaction_id = self.manager.get_field('transaction_id', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/payments/{transaction_id}', ambiente)
        return self.manager.executar_requisicao(
            'DELETE', url, ambiente=ambiente)


class GetTransacao(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        params = kwargs.pop('parametros', {})
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        transaction_id = self.manager.get_field('transaction_id', **kwargs)
        url = self.manager.get_endpoint(
            f'/v2/accounts/{account_id}/transactions/{transaction_id}',
            ambiente)
        url_for_hash = (f'get:/v2/accounts/{account_id}' +
                        f'/transactions/{transaction_id}')
        transaction_hash = self.manager._get_transaction_hash_url(
            url=url_for_hash)
        return self.manager.executar_requisicao(
            'GET', url, ambiente=ambiente, transaction_hash=transaction_hash,
            params=params)


class GetTransacoes(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        params = kwargs.pop('parametros', {})
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v2/accounts/{account_id}/transactions',
            ambiente)
        url_for_hash = (f'get:/v2/accounts/{account_id}/transactions')
        transaction_hash = self.manager._get_transaction_hash_url(
            url=url_for_hash)
        return self.manager.executar_requisicao(
            'GET', url, ambiente=ambiente, transaction_hash=transaction_hash,
            params=params)


class GetExtrato(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        params = kwargs.pop('parametros', {})
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}/statement',
            ambiente)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_id(**kwargs)
        # url_for_hash = (f'get:/v3/accounts/{account_id}/statement')
        # transaction_hash = self.manager._get_transaction_hash_url(
        #     url=url_for_hash)
        return self.manager.executar_requisicao(
            'GET', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash, params=params)


class GetSaldo(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v2/accounts/{account_id}/balance',
            ambiente)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_id(**kwargs)
        return self.manager.executar_requisicao(
            'GET', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class ListMotivosDevolucao(operation.List):

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        country = self.manager.get_field('country', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/instant-payments/{country}/return-codes',
            ambiente)
        return self.manager.executar_requisicao(
            'GET', url, json=kwargs, ambiente=ambiente)


class RealizarDevolucaoPagamento(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        transaction_id = self.manager.get_field('transaction_id', **kwargs)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_four_fields_3(**kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}/instant-payments/' +
            f'{transaction_id}/returns',
            ambiente)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class ConsultarAliasDestinatario(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        country = self.manager.get_field('country', **kwargs)
        alias_destinatario = self.manager.get_field(
            'alias_destinatario', **kwargs)
        url = self.manager.get_endpoint(
            f'/v2/accounts/{account_id}/aliases/{country}/' +
            f'{alias_destinatario}',
            ambiente)
        return self.manager.executar_requisicao(
            'GET', url, ambiente=ambiente)


class CashoutViaPix(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}/withdraw',
            ambiente)
        kwargs, transaction_hash = self.manager\
            ._get_transaction_hash_four_fields(**kwargs)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente,
            transaction_hash=transaction_hash)


class CashoutPixViaCsm(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        url = self.manager.get_endpoint(
            '/v1/instant-payment-non-priority',
            ambiente)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente)


class CashoutViaTed(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        account_id = self.manager.get_account_id(**kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{account_id}/withdraw',
            ambiente)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente)


class ListLimitesDaContaDaAgencia(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        branch = self.manager.get_field('branch', **kwargs)
        account = self.manager.get_field('account', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{branch}/{account}/limits',
            ambiente)
        return self.manager.executar_requisicao(
            'GET', url, ambiente=ambiente)


class AjustarLimite(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        branch = self.manager.get_field('branch', **kwargs)
        account = self.manager.get_field('account', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{branch}/{account}/limits',
            ambiente)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente)


class DefinirInicioPeriodoNoturno(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        branch = self.manager.get_field('branch', **kwargs)
        account = self.manager.get_field('account', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{branch}/{account}/limits',
            ambiente)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente)


class AddFavorecido(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        branch = self.manager.get_field('branch', **kwargs)
        account = self.manager.get_field('account', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{branch}/{account}/limits', ambiente)
        return self.manager.executar_requisicao(
            'POST', url, json=kwargs, ambiente=ambiente)


class ListarLimitesDaAgencia(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        branch = self.manager.get_field('branch', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{branch}/limits', ambiente)
        return self.manager.executar_requisicao(
            'GET', url, json=kwargs, ambiente=ambiente)


class ObterLimiteContaFiltradoPorTipo(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        branch = self.manager.get_field('branch', **kwargs)
        account = self.manager.get_field('account', **kwargs)
        limitType = self.manager.get_field('limitType', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{branch}/{account}/limits/{limitType}',
            ambiente)
        return self.manager.executar_requisicao(
            'GET', url, json=kwargs, ambiente=ambiente)


class RemoverFavorecido(operation.List):

    def pre(self, **kwargs):
        # valida se o usuario do token está ligado a conta
        self.manager.validar_token(**kwargs)
        return True

    def do(self, session, **kwargs):
        ambiente = kwargs.pop('api_payfac', None)
        branch = self.manager.get_field('branch', **kwargs)
        account = self.manager.get_field('account', **kwargs)
        favored_id = self.manager.get_field('favored_id', **kwargs)
        url = self.manager.get_endpoint(
            f'/v1/accounts/{branch}/{account}/limits/{favored_id}',
            ambiente)
        return self.manager.executar_requisicao(
            'DELETE', url, ambiente=ambiente)


class Manager(manager.Manager):
    BASE_URL_PROD = 'https://mtls-mp.prd.flagship.maas.link'
    BASE_URL_HOMO = 'https://mtls-mp.hml.flagship.maas.link'

    base_folder = os.environ.get('VIGGOCORE_FILE_DIR', None)

    CERT = {
        c_payfac_tipo.PRODUCAO: (
            base_folder + '/matera/ClientProd.pem',
            base_folder + '/matera/ClientProd.key'),
        c_payfac_tipo.HOMOLOGACAO: (
            base_folder + '/matera/ClientHomo.pem',
            base_folder + '/matera/ClientHomo.key')
    }

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        # rotas de conta e chave PIX
        self.criar_conta = CriarConta(self)
        self.get_conta = GetConta(self)
        self.add_chave_pix = AddChavePix(self)
        self.list_chaves_pix = ListChavesPix(self)
        self.atualizar_conta = AtualizarConta(self)
        self.deletar_chave_pix = DeletarChavePix(self)
        self.inativar_conta = InativarConta(self)
        # rotas de gerar QR Code
        self.gerar_qrcode = GerarQrcode(self)
        self.gerar_qrcode_cobranca = GerarQrcodeCobranca(self)
        # rotas de transferência interna
        self.realizar_transferencia_interna = \
            RealizarTransferenciaInterna(self)
        self.estornar_transferencia_interna = \
            EstornarTransferenciaInterna(self)
        # rotas de consultas
        self.get_transacao = GetTransacao(self)
        self.get_transacoes = GetTransacoes(self)
        self.get_extrato = GetExtrato(self)
        self.get_saldo = GetSaldo(self)
        # rotas de devoluções
        self.list_motivos_devolucao = ListMotivosDevolucao(self)
        self.realizar_devolucao_pagamento = RealizarDevolucaoPagamento(self)
        # rotas de cash out
        self.consultar_alias_destinatario = ConsultarAliasDestinatario(self)
        self.cashout_via_pix = CashoutViaPix(self)
        self.cashout_pix_via_csm = CashoutPixViaCsm(self)
        self.cashout_via_ted = CashoutViaTed(self)
        # rotas de limites de conta
        self.list_limites_da_conta_da_agencia = \
            ListLimitesDaContaDaAgencia(self)
        self.ajustar_limite = AjustarLimite(self)
        self.definir_inicio_periodo_noturno = DefinirInicioPeriodoNoturno(self)
        self.add_favorecido = AddFavorecido(self)
        self.listar_limites_da_agencia = ListarLimitesDaAgencia(self)
        self.obter_limite_conta_filtrado_por_tipo = \
            ObterLimiteContaFiltradoPorTipo(self)
        self.remover_favorecido = RemoverFavorecido(self)

    def _get_transaction_hash_id(self, **kwargs):
        id = kwargs.pop('id', None)
        transaction_hash = TransactionHash(id=id).get_hash_id()
        return (kwargs, transaction_hash)

    def _get_transaction_hash_id_cnpj(self, **kwargs):
        id = kwargs.pop('id', None)
        cnpj = kwargs.pop('cnpj', None)
        transaction_hash = TransactionHash(id=id, cnpj=cnpj).get_hash_id_cnpj()
        return (kwargs, transaction_hash)

    def _get_transaction_hash_account_id(self, **kwargs):
        account_id = kwargs.pop('account_id', None)
        transaction_hash = TransactionHash(account_id=account_id)\
            .get_hash_account_id()
        return (kwargs, transaction_hash)

    def _get_transaction_hash_url(self, url):
        transaction_hash = TransactionHash(url=url).get_hash_url()
        return transaction_hash

    def _get_transaction_hash_four_fields(self, **kwargs):
        total_amount = kwargs.pop('total_amount', None)
        total_amount = int(float(total_amount))
        account_id = kwargs.pop('account_id', None)
        psp_id = kwargs.pop('psp_id', None)
        tax_id = kwargs.pop('tax_id', None)
        transaction_hash = TransactionHash(
            total_amount=total_amount, account_id=account_id,
            psp_id=psp_id, tax_id=tax_id
            ).get_hash_four_fields()
        return (kwargs, transaction_hash)

    def _get_transaction_hash_four_fields_2(self, **kwargs):
        total_amount = kwargs.pop('total_amount', None)
        total_amount = int(float(total_amount))
        account_id = kwargs.pop('account_id', None)
        alias = kwargs.pop('alias', None)
        recipient_amount = kwargs.pop('recipient_amount', None)
        recipient_amount = int(float(recipient_amount))
        transaction_hash = TransactionHash(
            total_amount=total_amount, account_id=account_id,
            alias=alias, recipient_amount=recipient_amount
            ).get_hash_four_fields_2()
        return (kwargs, transaction_hash)

    def _get_transaction_hash_four_fields_3(self, **kwargs):
        total_amount = kwargs.pop('total_amount', None)
        total_amount = int(float(total_amount))
        account_id = kwargs.pop('account_id', None)
        transaction_id = kwargs.pop('transaction_id', None)
        reason_code = kwargs.pop('reason_code', None)
        transaction_hash = TransactionHash(
            total_amount=total_amount, account_id=account_id,
            transaction_id=transaction_id, reason_code=reason_code
            ).get_hash_four_fields_3()
        return (kwargs, transaction_hash)

    def _gerar_authorization(self, config, data, ambiente: c_payfac_tipo):
        url_base = ('https://mtls-mp.{ambiente}.flagship.maas.link/' +
                    'auth/realms/Matera/protocol/openid-connect/token')
        urls = {
            c_payfac_tipo.HOMOLOGACAO: 'hml',
            c_payfac_tipo.PRODUCAO: 'prd'}

        url = url_base.format(ambiente=urls.get(ambiente))

        body = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'grant_type': 'client_credentials'
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(url, data=body, headers=headers,
                                 cert=self.CERT[ambiente])

        if response.status_code == 200:
            response = self.montar_response_dict(response)
            data['Authorization'] = 'Bearer ' + response.get(
                'access_token', '')
            self.api.configuracao_pay_facs().update(
                id=config.id, **{'authorization': data['Authorization'],
                                 'authorization_dh': datetime.now()})
            return data
        else:
            raise exception.BadRequest(
                'Não foi possível gerar a autorização.')

    def get_authorization(self, ambiente: c_payfac_tipo):
        config = self.api.configuracao_pay_facs().\
            get_configuracao_payfac(tipo=ambiente)
        data = {'Authorization': config.authorization}

        if config.authorization_dh is not None:
            result = (datetime.now() - config.authorization_dh).seconds / 60
            if result > 4:
                data = self._gerar_authorization(config, data, ambiente)
        else:
            data = self._gerar_authorization(config, data, ambiente)

        return data

    def get_field(self, field_name, **kwargs):
        field = kwargs.get(field_name, None)
        if field is None:
            raise exception.BadRequest(f'O campo {field_name} é obrigatório.')
        return field

    def get_account_id(self, **kwargs):
        account_id = kwargs.get('account_id', None)
        if account_id is None:
            raise exception.BadRequest('O campo account_id é obrigatório.')
        return account_id

    def get_endpoint(self, resource, ambiente=None):
        urls = {
            c_payfac_tipo.HOMOLOGACAO: self.BASE_URL_HOMO + resource,
            c_payfac_tipo.PRODUCAO: self.BASE_URL_PROD + resource}
        return urls.get(ambiente, '')

    def executar_requisicao(self, method, endpoint, ambiente,
                            params={}, json={},
                            headers={'Content-Type': 'application/json',
                                     'Accept': 'application/json'},
                            data={}, sem_authorization=True,
                            transaction_hash=None):

        if sem_authorization is True:
            headers.update(self.get_authorization(ambiente=ambiente))

        if transaction_hash is not None:
            headers.update(transaction_hash)

        if method == 'GET':
            return requests.get(
                endpoint, params=params, json=json, headers=headers, data=data,
                cert=self.CERT[ambiente])
        elif method == 'POST':
            return requests.post(
                endpoint, params=params, json=json, headers=headers, data=data,
                cert=self.CERT[ambiente])
        elif method == 'PUT':
            return requests.put(
                endpoint, params=params, json=json, headers=headers, data=data,
                cert=self.CERT[ambiente])
        elif method == 'DELETE':
            return requests.delete(endpoint, headers=headers,
                                   cert=self.CERT[ambiente])
        else:
            raise exception.OperationBadRequest(
                'Método de requisição não permitido.')

    def montar_response_dict(self, response):
        try:
            response_dict = json.loads(response.text)
        except Exception:
            response_dict = {'error': response.text}
        return response_dict

    def validar_token(self, **kwargs):
        # verifica se foi enviado um account_id
        # (que é o matera_id do domain_account) e usa-o para pegar o domain
        account_id = kwargs.get('account_id', None)
        if account_id is None:
            raise exception.BadRequest('O account_id é obrigatório.')
        # lista os domínios com aquele account_id
        domain_accounts, _ = self.api.domain_accounts().list(
            matera_id=account_id)

        # verifica se não conseguiu encontrar um domínio
        if len(domain_accounts) != 1:
            raise exception.BadRequest(
                'Nenhuma conta encontrada no sistema.')
        domain_id = domain_accounts[0].id

        # verifica se foi passado o token
        token_id = flask.request.headers.get('token', None)
        if token_id is None:
            raise exception.BadRequest('O token é obrigatório.')
        try:
            token = self.api.tokens().get(id=token_id)
        except Exception:
            print('TOKEN: ' + token_id)
            raise exception.BadRequest('O token é inválido.')

        # pega o usuário ligado ao token e verifica se ele está
        # ligado ao domínio passado
        try:
            user = self.api.users().get(id=token.user_id)
        except Exception:
            print('USER_ID: ' + token.user_id)
            raise exception.BadRequest(
                'O user não foi encontrado para validar a ' +
                'permissão de acesso.')

        if user.domain_id != domain_id:
            raise exception.BadRequest(
                'Você não tem permissão de efetuar ações nesta conta.')
