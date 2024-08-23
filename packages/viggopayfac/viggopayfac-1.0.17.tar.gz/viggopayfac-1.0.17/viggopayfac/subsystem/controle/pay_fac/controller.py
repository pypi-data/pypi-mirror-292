import flask
import json
import uuid

from viggocore.common import exception, utils, controller
from viggopayfac.subsystem.controle.pay_fac.config_ambiente \
    import get_api_payfac


class Controller(controller.CommonController):
    API_PAYFAC = get_api_payfac()

    def __init__(self, manager, resource_wrap, collection_wrap):
        super(Controller, self).__init__(
            manager, resource_wrap, collection_wrap)

    def montar_response_dict(self, response):
        try:
            response_dict = json.loads(response.text)
        except Exception:
            response_dict = {'error': response.text}

        return response_dict

    def _get_response_to_return(self, response_dict):
        if 'data' in response_dict.keys():
            return response_dict.get('data', None)
        elif 'error' in response_dict.keys():
            return response_dict
        else:
            return 'RESPOSTA NÃO MAPEADA!'

    def get_conta(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.get_conta(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def add_chave_pix(self):
        data = flask.request.get_json()
        account_id = data.get('account_id', None)

        alias = {
            "account_id": account_id,
            "externalIdentifier": uuid.uuid4().hex,
            "alias": {
                "type": "EVP"
            }
        }
        alias['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.add_chave_pix(**alias)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def list_chaves_pix(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            # remove esse campo para garantir que o mesmo só possa ser
            # passado na requisição ao manager pelo próprio backend
            data.pop('chamada_interna', None)
            response = self.manager.list_chaves_pix(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def get_transacoes(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC
        transaction_id = data.get('transaction_id', None)

        try:
            if transaction_id is None:
                response = self.manager.get_transacoes(**data)
            else:
                response = self.manager.get_transacao(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def get_ultima_transacao(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.get_transacoes(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        transactions = response_final.get('transactions', [])
        if len(transactions) == 0:
            return flask.Response(response='Nenhuma transação foi encontrada.',
                                  status=404)
        else:
            ultima_transacao = transactions[0]

        return flask.Response(response=utils.to_json(ultima_transacao),
                              status=response.status_code,
                              mimetype="application/json")

    def get_extrato(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.get_extrato(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def get_saldo(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.get_saldo(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def cashout_via_pix(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        data['total_amount'] = data.get('totalAmount', None)
        recipient = data.get('withdrawInfo', {}).get('instantPayment', {})\
            .get('recipient', {})
        data['psp_id'] = recipient.get('pspId', None)
        data['tax_id'] = recipient.get('taxIdentifier', {}).get('taxId', None)
        data['externalIdentifier'] = uuid.uuid4().hex

        try:
            response = self.manager.cashout_via_pix(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def gerar_qrcode(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        data['total_amount'] = data.get('totalAmount', None)
        recipient = data.get('withdrawInfo', {}).get('instantPayment', {})\
            .get('recipient', {})
        data['psp_id'] = recipient.get('pspId', None)
        data['tax_id'] = recipient.get('taxIdentifier', {}).get('taxId', None)
        data['externalIdentifier'] = uuid.uuid4().hex

        try:
            response = self.manager.gerar_qrcode(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def consultar_alias_destinatario(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.consultar_alias_destinatario(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def gerar_qrcode_cobranca(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        data['total_amount'] = data.get('totalAmount', None)
        recipient = data.get('withdrawInfo', {}).get('instantPayment', {})\
            .get('recipient', {})
        data['psp_id'] = recipient.get('pspId', None)
        data['tax_id'] = recipient.get('taxIdentifier', {}).get('taxId', None)

        try:
            response = self.manager.gerar_qrcode_cobranca(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def list_motivos_devolucao(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.list_motivos_devolucao(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def realizar_devolucao_pagamento(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.realizar_devolucao_pagamento(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")

    def deletar_chave_pix(self):
        data = flask.request.get_json()
        data['api_payfac'] = self.API_PAYFAC

        try:
            response = self.manager.deletar_chave_pix(**data)
        except exception.ViggoCoreException as exc:
            return flask.Response(response=exc.message,
                                  status=exc.status)
        if response.status_code in [200, 202]:
            return flask.Response(status=response.status_code,
                                  mimetype="application/json")

        response_dict = self.montar_response_dict(response)
        response_final = self._get_response_to_return(response_dict)

        return flask.Response(response=utils.to_json(response_final),
                              status=response.status_code,
                              mimetype="application/json")
