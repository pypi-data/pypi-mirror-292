from logyca_ai.utils.schemes.input.conversations import (
    AssistantMessage,
    Content,
    ImageFileMessage,
    PdfFileMessage,
    UserMessage,
)
from logyca_ai.utils.constants.content import ContentType
from logyca_ai.utils.constants.image import ImageResolution
from logyca_ai.assets_for_examples.file_or_documents.image_base64 import image_base64_sample
from logyca_ai.assets_for_examples.file_or_documents.pdf_base64 import pdf_base64_sample

def get_content_simple_sample()->Content:
    return Content(
        system="""
                    Voy a definirte tu personalidad, contexto y proposito.
                    Actua como un experto en venta de frutas.
                    Se muy positivo.
                    Trata a las personas de usted, nunca tutees sin importar como te escriban.
                """.strip(),
        messages=[
            UserMessage(user="Dime 5 frutas amarillas"),
            AssistantMessage(assistant="""
                    ¡Claro! Aquí te van 5 frutas amarillas:

                    1. Plátano
                    2. Piña
                    3. Mango
                    4. Melón
                    5. Papaya
                """
            ),
            UserMessage(user="Dame los nombres en ingles."),
        ]
        )

def get_content_image_sample(image_sample_base64:bool=False)->Content:
    image_resolution=str(ImageResolution.AUTO)
    if image_sample_base64:
        base64_content_or_url=image_base64_sample
        image_format="png"
        type_message=ContentType.IMAGE_BASE64
    else:
        base64_content_or_url="https://raw.githubusercontent.com/logyca/python-libraries/3d91b5a93fb1219804753ce233fabd5f635662d3/logyca-ai/logyca_ai/assets_for_examples/file_or_documents/image.png"
        image_format=ContentType.IMAGE_URL
        type_message=ContentType.IMAGE_URL
    return Content(
        system="""
                Actua como una maquina lectora de imagenes.
                Devuelve la información sin lenguaje natural, sólo responde lo que se está solicitando.
                El dispositivo que va a interactuar contigo es una api, y necesita la información sin markdown u otros caracteres especiales.
                """.strip(),
        messages=[
            UserMessage(
                user="Extrae el texto que recibas en la imagen y devuelvelo en formato json.",
                type=type_message,
                additional_content=ImageFileMessage(
                    base64_content_or_url=base64_content_or_url,
                    image_format=image_format,
                    image_resolution=image_resolution,
                ).to_dict()
            )
        ]
    )

def get_content_pdf_sample(pdf_sample_base64:bool=False)->Content:
    if pdf_sample_base64:
        base64_content_or_url=pdf_base64_sample
        pdf_format="pdf"
        type_message=ContentType.PDF_BASE64
    else:
        base64_content_or_url="https://raw.githubusercontent.com/logyca/python-libraries/3d91b5a93fb1219804753ce233fabd5f635662d3/logyca-ai/logyca_ai/assets_for_examples/file_or_documents/pdf.pdf"
        pdf_format=ContentType.PDF_URL
        type_message=ContentType.PDF_URL
    return Content(
        system="""
                No uses lenguaje natural para la respuesta.
                Dame la información que puedas extraer de la imagen en formato JSON.
                Solo devuelve la información, no formatees con caracteres adicionales la respuesta.
                """.strip(),
        messages=[
            UserMessage(
                user="Dame los siguientes datos: Expediente, radicación, Fecha, Numero de registro, Vigencia.",
                type=type_message,
                additional_content=PdfFileMessage(
                    base64_content_or_url=base64_content_or_url,
                    pdf_format=pdf_format,
                ).to_dict()
            )
        ]
    )



