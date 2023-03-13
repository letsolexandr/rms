from typing import Text, Dict, Union
import os
import base64
import tempfile
import pathlib
import logging



from apps.core.ua_sign.EUSignCP_20230202.Interface.EUSignCP import *

logger = logging.getLogger(__name__)

# КОДИ ПОМИЛОК
ERROR_LOAD_LIBRARY = 2  # Помилка при завантаженні бібіліотеки
ERROR_SIGN = 1  # Помилка при перевірці підпису
ERROR_FILE_NON_EXIST = 3  # Файл відсутній

# TODO додати підтримку '.xml'
ASICE = '.asice'
ASICS = '.asics'
PADES = '.pdf'
CADES = '.p7s'

AVAILABLE_EXTENSIONS = [ASICE, ASICS, PADES, CADES]

def varify_internal_recursive(data_path: Union[None, os.PathLike] = None,  sign_data: Union[Text, None] = None, sign_data_byte=None,edrpou=None):
    """Застосовується для перевірки няявності підпису КЕП  організації (представника організації)"""
    results = []
    res = verify_internal(data_path=data_path, sign_data=sign_data, sign_data_byte=sign_data_byte)
        
    if res.get('code') == 0:
        results.append(res)
        ##Отримуємо дані за ЄДРПОУ та  анаявністю РНОКПП
        if res.get('cert').get('pszSubjEDRPOUCode') == str(edrpou) and res.get('cert').get('pszSubjDRFOCode'):
            del res['data']
            return res

    ##Якщо дані необхідного підпису не знайдені заглиблюємось в підпис
    if res.get('code') == 0 and res.get('data'):
        while True:
            res = verify_internal(sign_data_byte=res.get('data'))
            if res.get('code') != 0:
                if len(results):
                    return results[0]
            results.append(res)
            ##Отримуємо дані за ЄДРПОУ та  анаявністю РНОКПП
            if res.get('cert').get('pszSubjEDRPOUCode') == str(edrpou) and res.get('cert').get('pszSubjDRFOCode'):
                del res['data']
                return res
            if res.get('code') != 0:
                if len(results):
                    return results[0]
    else:
        return res

        

def verify_internal(data_path: Union[None, os.PathLike] = None,  sign_data: Union[Text, None] = None, sign_data_byte=None) -> Dict:
    """
    Перевіряє внутрішній підпис файлу (підпис, іпідписаний файл в одному фалі)
    :param data_path:
    :return:
    """
    EULoad()
    pIface:EUGetInterface = EUGetInterface()
    try:
        pIface.Initialize()
        pIface.SetOCSPResponseExpireTime(30)
    except Exception as e:
        logger.error("Initialize failed" + str(e))
        return {'code_message': e, 'code': 2}
    try:
        if not sign_data and not sign_data_byte:
            ddd=[]
            pIface.GetFileSignsCount(data_path,ddd)
            data = open(data_path, 'rb').read()
        elif sign_data:
            data = base64.b64decode(sign_data)
        elif sign_data_byte:
            data = sign_data_byte
        d = []
        S = {}
 
        
        pIface.VerifyDataInternal(None, data, len(data), d, S)
        return {'cert': S, 'data': d[0], 'code': 0, 'code_message': 'Успішно'}
    except RuntimeError as e:
        logger.error(e)
        error_data = e.args[0]
        error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
        logger.error(error_data)
        return {'code_message': error_data['ErrorDesc'], 'code': 1}


def verify_external(data_path: os.PathLike, sign_path: Union[None, os.PathLike] = None,
                    sign_data: Union[Text, None] = None) -> Dict:
    """
    Перевіряє зовнішній підпис файлу (підпис  та  документ в окремих файлах)
    :param data_path Повний шлях до документа
    :param sign_path Повний шлях до підпису
    :param sign_data Підпис в base64
    :return:
    """
    try:
        logger.debug("load library")
        EULoad()
        logger.debug("EUGetInterface")
        pIface = EUGetInterface()
        pIface.SetOCSPResponseExpireTime(30)
        logger.debug("Initialize")
        if not pIface.IsInitialized():
            pIface.Initialize()
    except Exception as e:
        logger.error("Initialize failed" + str(e))
        EUUnload()
        return {'code_message': e, 'code': ERROR_LOAD_LIBRARY}
   
    try:
        data = open(data_path, 'rb').read()
        S = {}
        if sign_path:
            sign = open(sign_path, 'rb').read()
            pIface.VerifyData(data, len(data), None, sign, len(sign), S)
            signer_info = get_signer_info(sign)
        elif sign_data:
            sign = sign_data
            logger.debug('VerifyData')
            pIface.VerifyData(data, len(data), sign, None, len(sign), S)
            signer_info = get_signer_info(base64.b64decode(sign))
        else:
            raise Exception('mising required params:"sign_path" or "sign_data" ')
        S.update(signer_info.get('cert_info'))
        return {'cert': S, 'code': 0, 'code_message': 'Успішно'}
    except RuntimeError as e:
        logger.error(e)
        error_data = e.args[0]
        error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
        logger.error(error_data)
        return {'code_message': error_data['ErrorDesc'], 'code': 1}
    finally:
        EUUnload()


def sign_external(data_path: os.PathLike, key_path: os.PathLike, pwd: str, sign_data_path: os.PathLike) -> Dict:
    """
    Накдадає КЕП на файл, кеп і оригінальний файл оремими файлами
    :param data_path: абсолютний шлях до файлу який потрібно підписати
    :param key_path: абсолютний шлях до файлу ключа
    :param sign_data_path: абсолютний шлях, за яким буде збережено файл підпису
    :return: В разу успіху {'code': 0, 'code_message': 'Успішно'},
    якщо в процесі виконання буде помилка {'code_message': str(e), 'code': 1}
    """
    try:
        logger.debug("load library")
        EULoad()
        logger.debug("EUGetInterface")
        pIface = EUGetInterface()
        pIface.SetOCSPResponseExpireTime(30)
        logger.debug("Initialize")
        pIface.Initialize()
    except Exception as e:
        logger.error("Initialize failed" + str(e))
        return {'code_message': str(e), 'code': ERROR_LOAD_LIBRARY}
    try:
        with open(data_path, 'rb') as data:
            b_data = data.read()
            lSign = []
            pIface.ReadPrivateKeyFile(key_path, pwd, None)
            pIface.SignData(b_data, len(b_data), None, lSign)
            with open(sign_data_path, 'wb') as sign_file:
                sign_file.write(lSign[0])

            return {'code': 0, 'code_message': 'Успішно'}
    except Exception as e:
        logger.error(e)
        pIface.Finalize()
        # EUUnload()
        return {'code_message': str(e), 'code': 1}


def decrypt_data(pszEnvelopedData: str, key_path: os.PathLike, pwd: str) -> Dict:
    """
    Розкодовує закондвний набір даних підписаний відкритим сертифікатом
    :param pszEnvelopedData: закодований набір даних
    :param key_path: абсолютний шлях до файлу ключа
    :param pwd: пароль
    :return: В разу успіху {'code': 0, 'code_message': 'Успішно'},
    якщо в процесі виконання буде помилка {'code_message': str(e), 'code': 1}
    """
    try:
        logger.debug("load library")
        EULoad()
        logger.debug("EUGetInterface")
        pIface = EUGetInterface()
        pIface.SetOCSPResponseExpireTime(30)
        logger.debug("Initialize")
        pIface.Initialize()
    except Exception as e:
        logger.error("Initialize failed" + str(e))
        # EUUnload()
        return {'code_message': str(e), 'code': ERROR_LOAD_LIBRARY}
    try:
        ppbData = []
        pIface.ReadPrivateKeyFile(key_path, pwd, None)
        pIface.DevelopData(pszEnvelopedData, None, len(
            pszEnvelopedData), ppbData, None)
        return {'code': 0, 'code_message': 'Успішно', 'data': ppbData[0]}
    except Exception as e:
        logger.error(e)
        pIface.Finalize()
        # EUUnload()
        return {'code_message': str(e), 'code': 1}
    finally:
        pIface.Finalize()
        # EUUnload()


def get_signer_info(sign_data) -> Dict:
    try:
        logger.debug("load library")
        EULoad()
        logger.debug("EUGetInterface")
        pIface = EUGetInterface()
        pIface.SetOCSPResponseExpireTime(30)
        logger.debug("Initialize")
        pIface.Initialize()
    except Exception as e:
        logger.error("Initialize failed" + str(e))
        return {'code_message': str(e), 'code': ERROR_LOAD_LIBRARY}

    try:
        logger.debug('GetSignerInfo')
        S = {}
        d = []
        pIface.GetSignerInfo(dwSignIndex=0, pszSign=None, pbSign=sign_data,  dwSignLength=len(
            sign_data), ppInfo=S, ppbCertificate=d)
        #pIface.Finalize()
        return {'cert_info': S, 'code': 0, 'code_message': 'Успішно', "cert_data": d[0]}
    except RuntimeError as e:
        error_data = e.args[0]
        error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
        #pIface.Finalize()
        return {'code_message': error_data['ErrorDesc'], 'code': 1}
    except Exception as ee:
        raise ee


def get_file_signs_count(data_path: os.PathLike) -> int:
    """
    Перевіряє кількість підписів у файлі
    :param data_path:
    :return int Кількість підписів, або 0 якщо відсутні:
    """
    EULoad()
    pIface = EUGetInterface()
    pIface.SetOCSPResponseExpireTime(30)
    try:
        pIface.Initialize()
    except Exception as e:
        logger.error("Initialize failed" + str(e))
        return 0
    try:
        d = [0]
        encoded_path = data_path.encode()  # Для підтримки кирилиці в назві файлу
        pIface.GetFileSignsCount(encoded_path,  d)
        return d[0]
    except RuntimeError as e:
        error_data = e.args[0]
        error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
        logger.error(error_data)
        pIface.Finalize()
        return 0
    except Exception as ee:
        raise ee


def is_sign_exists(data_path: os.PathLike) -> Dict:
    """
    Перевіряє наявні підписів та підписаних даних у файлі
    :param data_path:
    :return dict 0-наявні підписи і дані, 1- Наявний,лише підпис,
     2-файл не містить підписів(помилка), 3-посилання на файл недійсне (файл відсутній):
    """
    if not os.path.exists(data_path):
        return {'code_message': "Посилання на файл недійсне (файл відсутній)", 'code': 3}
    d = []
    EULoad()
    pIface = EUGetInterface()
    pIface.SetOCSPResponseExpireTime(30)
    try:
        pIface.Initialize()
        encoded_path = data_path.encode()  # Для підтримки кирилиці в назві файлу
        pIface.IsDataInSignedFileAvailable(encoded_path,  d)
        pIface.Finalize()
        EUUnload()
        if d[0]:
            return {'code_message': "Наявні підписи і дані", 'code': 0}
        else:
            return {'code_message': "Наявний,лише підпис", 'code': 1}
    except RuntimeError:
        pIface.Finalize()
        EUUnload()
        return {'code_message': "Файл не містить підписів(помилка)", 'code': 2}


class UASign:
    loaded = False

    @classmethod
    def load_library(cls):
        try:
            logger.debug("load library")
            EULoad()
            logger.debug("EUGetInterface")
            cls.pIface = EUGetInterface()
            cls.pIface.SetOCSPResponseExpireTime(30)
            logger.debug("Initialize")
            cls.pIface.Initialize()
            cls.loaded = True
            return {'code_message': 'Бібілотеку успішло ініційовано', 'code': 0}
        except Exception as e:
            logger.error("Initialize failed" + str(e))
            return {'code_message': e, 'code': ERROR_LOAD_LIBRARY}

    @classmethod
    def verify(cls, data_path: os.PathLike, sign_path: Union[None, os.PathLike] = None,
               sign_data: Union[Text, None] = None):
        data_path = data_path
        if not os.path.exists(data_path):
            return {'code_message': "Посилання на файл недійсне (файл відсутній)", 'code': 3}

        if not cls.loaded:
            res = cls.load_library()
            if res.get('code') != 0:
                return res

        if data_path and (sign_path or sign_data):
            return cls.verify_p7s(data_path=data_path, sign_path=sign_path, sign_data=sign_data)

        if cls.get_file_extention(data_path) in [CADES]:
            return cls.verify_p7s(data_path=data_path)

        if cls.get_file_extention(data_path) in [ASICE, ASICS]:
            return cls.verify_asic(data_path=data_path)

        if cls.get_file_extention(data_path) in [PADES]:
            return cls.verify_pdf(data_path=data_path)

        # if cls.get_file_extention(data_path) in ['.xml']:
        #     return cls.verify_xml(data_path=data_path)

    @classmethod
    def verify_p7s(cls, data_path: os.PathLike, sign_path: Union[None, os.PathLike] = None,
                   sign_data: Union[Text, None] = None):

        if cls.is_sign_exists(data_path).get('code') in [0, 1]:
            return cls.verify_internal_p7s(data_path=data_path)

        elif cls.is_sign_exists(sign_path).get('code') in [0, 1] or sign_data:
            return cls.verify_external_p7s(data_path=data_path, sign_path=sign_path,
                                           sign_data=sign_data)
        else:
            return cls.is_sign_exists(data_path)

    @classmethod
    def is_sign_exists(cls, data_path: os.PathLike) -> Dict:
        """
        Перевіряє наявні підписів та підписаних даних у файлі
        :param data_path:
        :return dict 0-наявні підписи і дані, 1- Наявний,лише підпис,
        2-файл не містить підписів(помилка), 3-посилання на файл недійсне (файл відсутній):
        """
        if not data_path or not os.path.exists(data_path):
            return {'code_message': "Посилання на файл недійсне (файл відсутній)", 'code': 3}
        d = []
        try:
            # Для підтримки кирилиці в назві файлу, застосовується виключно для функції IsDataInSignedFileAvailable
            encoded_path = data_path.encode()
            cls.pIface.IsDataInSignedFileAvailable(encoded_path,  d)
            if d[0]:
                return {'code_message': "Наявні підписи і дані", 'code': 0}
            else:
                return {'code_message': "Наявний,лише підпис", 'code': 1}
        except RuntimeError:
            return {'code_message': "Файл не містить підписів(помилка)", 'code': 2}

    @classmethod
    def verify_internal_p7s(cls, data_path: os.PathLike):
        logger.info('verify_internal_p7s')
        try:
            S = {}
            d = []
            data = None
            if data_path:
                with open(data_path.encode(), 'rb') as sign_file:
                    data = sign_file.read()
            cls.pIface.VerifyDataInternal(None, data, len(data), d, S)
            signer_info = cls.get_signer_info(data)
            S.update(signer_info.get('cert_info'))
            return {'cert': S, 'data': d[0], 'code': 0, 'code_message': 'Успішно'}
        except RuntimeError as e:
            logger.error(e)
            error_data = e.args[0]
            error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
            logger.error(error_data)
            return {'code_message': error_data['ErrorDesc'], 'code': 1}

    @classmethod
    def verify_asic(cls, data_path: Union[None, os.PathLike] = None,
                    data: Union[Text, None] = None):
        logger.info('verify_asic')
        try:
            S = {}
            if data_path:
                with open(data_path.encode(), 'rb') as sign_file:
                    data = sign_file.read()

            cls.pIface.ASiCVerifyData(0, data, len(data), S)
            signer_info = cls.get_signer_info(
                sign_data=data, sign_file_type=ASICE)
            S.update(signer_info.get('cert_info'))
            return {'cert': S, 'code': 0, 'code_message': 'Успішно'}
        except RuntimeError as e:
            logger.error(e)
            error_data = e.args[0]
            error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
            logger.error(error_data)
            return {'code_message': error_data['ErrorDesc'], 'code': 1}

    @classmethod
    def verify_pdf(cls, data_path: Union[None, os.PathLike] = None,
                   data: Union[Text, None] = None):
        logger.info('PDFVerifyData')
        if not cls.loaded:
            res = cls.load_library()
            if res.get('code') != 0:
                return res
        try:
            S = {}
            data = None
            if data_path:
                with open(data_path.encode(), 'rb') as sign_file:
                    data = sign_file.read()

            cls.pIface.PDFVerifyData(0, data, len(data), S)
            signer_info = cls.get_signer_info(
                sign_data=data, sign_file_type='.pdf')
            S.update(signer_info.get('cert_info'))
            return {'cert': S, 'code': 0, 'code_message': 'Успішно'}
        except RuntimeError as e:
            logger.error(e)
            error_data = e.args[0]
            error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
            logger.error(error_data)
            return {'code_message': error_data['ErrorDesc'], 'code': 1}

    # @classmethod
    # def verify_xml(cls, data_path: Union[None, os.PathLike] = None,
    #                data: Union[Text, None] = None):
    #     logger.info('XAdESVerifyData')
    #     try:
    #         S = {}
    #         data = None
    #         if data_path:
    #             with open(data_path.encode(), 'rb') as sign_file:
    #                 data = sign_file.read()
    #         cls.pIface.XAdESVerifyData(None, None, 0, data, len(data), S)
    #         ##signer_info = get_signer_info(sign)
    #         # S.update(signer_info.get('cert_info'))
    #         logger.info(S)
    #         return {'cert': S, 'code': 0, 'code_message': 'Успішно'}
    #     except RuntimeError as e:
    #         logger.error(e)
    #         error_data = e.args[0]
    #         error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
    #         logger.error(error_data)
    #         return {'code_message': error_data['ErrorDesc'], 'code': 1}

    @classmethod
    def get_file_extention(cls, data_path: os.PathLike):
        return pathlib.Path(data_path).suffix

    @classmethod
    def extract_data(cls, data_path: os.PathLike):
        if cls.get_file_extention(data_path) in AVAILABLE_EXTENSIONS:
            with open(data_path, 'rb') as data_file:
                data = data_file.read()
            if cls.get_file_extention(data_path) in [ASICE, ASICS]:
                return cls.extract_asic(data)
            if cls.get_file_extention(data_path) in [CADES]:
                original_file_name = data_path.replace(CADES,'')
                original_file_ext = cls.get_file_extention(original_file_name)
                return cls.extract_cades(data,original_file_ext)
            if cls.get_file_extention(data_path) in [PADES]:
                return cls.extract_asic(data) 

    @classmethod
    def extract_cades(cls, data: bytes,file_ext:str):
        if not cls.loaded:
            res = cls.load_library()
            if res.get('code') != 0:
                return res

        try:
            S = {}
            d = []
            cls.pIface.VerifyDataInternal(None, data, len(data), d, S)
            signer_info = cls.get_signer_info(data)
            S.update(signer_info.get('cert_info'))
            output_file = tempfile.NamedTemporaryFile(
                    suffix=file_ext, delete=False).name
            with open(output_file, 'wb') as ref_file:
                    ref_file.write(d[0])
            return {'ref_result': output_file, 'code': 0, 'code_message': 'Успішно'}
        except RuntimeError as e:
            logger.error(e)
            error_data = e.args[0]
            error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
            logger.error(error_data)
            return {'code_message': error_data['ErrorDesc'], 'code': 1}

    @classmethod
    def extract_pades(cls):
        pass        

    @classmethod
    def extract_asic(cls, data: bytes):
        if not cls.loaded:
            res = cls.load_library()
            if res.get('code') != 0:
                return res

        data_refs = []
        try:
            cls.pIface.ASiCGetSignReferences(
                dwSignIndex=0, pbASiCData=data, dwASiCDataLength=len(data), ppszReferences=data_refs)
            if data_refs:
                ref_result = []
                cls.pIface.ASiCGetReference(pbASiCData=data, dwASiCDataLength=len(
                    data), pszReference=data_refs[0], ppbReference=ref_result)
                output_file = tempfile.NamedTemporaryFile(
                    suffix='_'+data_refs[0], delete=False).name
                with open(output_file, 'wb') as ref_file:
                    ref_file.write(ref_result[0])
                return {'ref_result': output_file, 'code': 0, 'code_message': 'Успішно'}
            else:
                raise Exception('ASIC- не коректний, відсутні файли')

        except RuntimeError as e:
            logger.error(e)
            error_data = e.args[0]
            error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
            logger.error(error_data)
            return {'code_message': error_data['ErrorDesc'], 'code': 1}

    # @classmethod
    # def get_sign(cls,data_path: os.PathLike):
    #     if not cls.loaded:
    #         res = cls.load_library()
    #         if res.get('code') != 0:
    #             return res

    #     if not os.path.exists(data_path):
    #         return {'code_message': "Посилання на файл недійсне (файл відсутній)", 'code': 3}

    #     if cls.get_file_extention(data_path) in [ASICE, ASICS]:
    #         return cls.get_asic_sign(data_path=data_path)

        # if data_path:
        #     return cls.verify_p7s(data_path=data_path)

        # if cls.get_file_extention(data_path) in [CADES]:
        #     return cls.verify_p7s(data_path=data_path)

        # if cls.get_file_extention(data_path) in [PADES]:
        #     return cls.verify_pdf(data_path=data_path)
    # @classmethod
    # def get_asic_sign(cls,data_path: os.PathLike):
    #     pass

    @classmethod
    def verify_external_p7s(cls, data_path: os.PathLike, sign_path: Union[None, os.PathLike] = None,
                            sign_data: Union[Text, None] = None):
        logger.info('verify_external_p7s')
        S = {}
        sign = None
        try:
            with open(data_path, 'rb') as data_file:
                data = data_file.read()
            if sign_path:
                if not os.path.exists(sign_path):
                    return {'code_message': "Посилання на файл підпису недійсне (файл відсутній)", 'code': 3}
                with open(sign_path, 'rb') as sign_file:
                    sign = sign_file.read()
                cls.pIface.VerifyData(
                    pbData=data, dwDataLength=len(data), pszSign=None, pbSign=sign, dwSignLength=len(sign), pSignInfo=S)
                signer_info = cls.get_signer_info(sign)
            elif sign_data:
                sign_b64 = sign_data
                cls.pIface.VerifyData(pbData=data, dwDataLength=len(
                    data), pszSign=sign_b64, pbSign=None,  dwSignLength=len(sign_b64), pSignInfo=S)
                signer_info = cls.get_signer_info(base64.b64decode(sign_b64))

            S.update(signer_info.get('cert_info'))
            return {'cert': S, 'code': 0, 'code_message': 'Успішно'}
        except RuntimeError as e:
            logger.error(e)
            error_data = e.args[0]
            error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
            logger.error(error_data)
            return {'code_message': error_data['ErrorDesc'], 'code': 1}

    @classmethod
    def get_signer_info(cls, sign_data: bytes, sign_file_type: str = '.p7s') -> Dict:
        try:
            S = {}
            d = []
            if sign_file_type == '.p7s':
                cls.pIface.GetSignerInfo(dwSignIndex=0, pszSign=None, pbSign=sign_data,  dwSignLength=len(
                    sign_data), ppInfo=S, ppbCertificate=d)
                return {'cert_info': S, 'code': 0, 'code_message': 'Успішно', "cert_data": d[0]}
            if sign_file_type in ['.asice', '.asics']:
                cls.pIface.ASiCGetSignerInfo(dwSignIndex=0, pbASiCData=sign_data,  dwASiCDataLength=len(
                    sign_data), ppInfo=S, ppbCertificate=d)
                return {'cert_info': S, 'code': 0, 'code_message': 'Успішно', "cert_data": d[0]}
            if sign_file_type in ['.pdf']:
                cls.pIface.PDFGetSignerInfo(dwSignIndex=0, pbSignedPDFData=sign_data,  dwSignedPDFDataLength=len(
                    sign_data), ppInfo=S, ppbCertificate=d)
                return {'cert_info': S, 'code': 0, 'code_message': 'Успішно', "cert_data": d[0]}

        except RuntimeError as e:
            error_data = e.args[0]
            error_data['ErrorDesc'] = error_data['ErrorDesc'].decode()
            return {'code_message': error_data['ErrorDesc'], 'code': 1}
        except Exception as ee:
            raise ee
