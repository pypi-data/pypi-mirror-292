import hashlib
import hmac
from viggocore.common import exception
from viggopayfac.subsystem.controle.pay_fac.config_ambiente \
    import get_secret_key


class TransactionHash():

    SECRET_KEY = get_secret_key()

    def __init__(self, id=None, cnpj=None, account_id=None, url=None,
                 total_amount=None, psp_id=None, tax_id=None, alias=None,
                 recipient_amount=None, transaction_id=None, reason_code=None):
        self.id = id
        self.cnpj = cnpj
        self.account_id = account_id
        self.url = url
        self.total_amount = total_amount
        self.psp_id = psp_id
        self.tax_id = tax_id
        self.alias = alias
        self.recipient_amount = recipient_amount
        self.transaction_id = transaction_id
        self.reason_code = reason_code

    def gerar_hash(self, msg):
        b_message = bytes(msg, 'utf-8')
        b_key = bytes(self.SECRET_KEY, 'utf-8')

        h = hmac.new(b_key, b_message, hashlib.sha256)

        return {'Transaction-Hash': h.hexdigest()}

    def get_hash_id(self):
        if None in [self.id]:
            raise exception.PreconditionFailed(
                'É necessário preencher o id.')

        return self.gerar_hash(self.id)

    def get_hash_id_cnpj(self):
        if None in [self.id, self.cnpj]:
            raise exception.PreconditionFailed(
                'É necessário preencher o id e o cnpj.')

        return self.gerar_hash(f'{self.id}{self.cnpj}')

    def get_hash_account_id(self):
        if None in [self.account_id]:
            raise exception.PreconditionFailed(
                'É necessário preencher o account_id.')

        return self.gerar_hash(self.account_id)

    def get_hash_url(self):
        if None in [self.url]:
            raise exception.PreconditionFailed(
                'É necessário preencher url.')

        return self.gerar_hash(self.url)

    def get_hash_four_fields(self):
        if None in [self.total_amount, self.account_id, self.psp_id,
                    self.tax_id]:
            raise exception.PreconditionFailed(
                'É necessário preencher os campos: total_amount, ' +
                'account_id, psp_id e tax_id.')
        msg = (f'{self.total_amount}{self.account_id}{self.psp_id}' +
               f'{self.tax_id}')
        return self.gerar_hash(msg)

    def get_hash_four_fields_2(self):
        if None in [self.total_amount, self.account_id, self.alias,
                    self.recipient_amount]:
            raise exception.PreconditionFailed(
                'É necessário preencher os campos: total_amount, ' +
                'account_id, alias e recipient_amount.')
        msg = (f'{self.alias}{self.total_amount}{self.account_id}' +
               f'{self.recipient_amount}')
        return self.gerar_hash(msg)

    def get_hash_four_fields_3(self):
        if None in [self.total_amount, self.account_id, self.transaction_id,
                    self.reason_code]:
            raise exception.PreconditionFailed(
                'É necessário preencher os campos: total_amount, ' +
                'account_id, transaction_id e reason_code.')
        msg = (f'{int(self.total_amount)}{self.account_id}' +
               f'{self.transaction_id}{self.reason_code}')
        return self.gerar_hash(msg)
