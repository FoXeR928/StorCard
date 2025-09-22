from io import BytesIO
from barcode import Code128,Code39,EAN13,CODABAR
from barcode.writer import SVGWriter
from loguru import logger


def check_code_type(code:str,code_type:str):
    if code_type=="code128":
        result=generate_code128(code=code)
    elif code_type=="code39":
        result=generate_code39(code=code)
    elif code_type=="ean13":
        result=generate_ean13(code=code)
    elif code_type=="codabar":
        result=generate_codabar(code=code)
    return result

def generate_code128(code:str):
    buffer=BytesIO()
    try:
        Code128(code=code,writer=SVGWriter()).write(buffer)
        result=buffer.getvalue()
    except Exception as err:
        logger.error(f"Не удалось сгенерировать SVG code128 ошибка: {err}")
        result=None
    finally:
        buffer.close()
    return result

def generate_code39(code:str):
    buffer=BytesIO()
    try:
        Code39(code=code,writer=SVGWriter()).write(buffer)
        result=buffer.getvalue()
    except Exception as err:
        logger.error(f"Не удалось сгенерировать SVG code128 ошибка: {err}")
        result=None
    finally:
        buffer.close()
    return result

def generate_ean13(code:str):
    buffer=BytesIO()
    try:
        EAN13(code=code,writer=SVGWriter()).write(buffer)
        result=buffer.getvalue()
    except Exception as err:
        logger.error(f"Не удалось сгенерировать SVG code128 ошибка: {err}")
        result=None
    finally:
        buffer.close()
    return result

def generate_codabar(code:str):
    buffer=BytesIO()
    try:
        CODABAR(code=code,writer=SVGWriter()).write(buffer)
        result=buffer.getvalue()
    except Exception as err:
        logger.error(f"Не удалось сгенерировать SVG code128 ошибка: {err}")
        result=None
    finally:
        buffer.close()
    return result