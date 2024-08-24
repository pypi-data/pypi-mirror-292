from logyca_ai.assets_for_examples.conversation_samples import (
    get_content_image_sample,
    get_content_pdf_sample,
    get_content_plain_text_sample,
    get_content_simple_sample,
    )
from logyca_ai.utils.constants.content import ContentRole, ContentType
from logyca_ai.utils.constants.image import ImageResolution
from logyca_ai.utils.helpers.azure_openai_chatgpt import AzureOpenAIChatGPT
from logyca_ai.utils.schemes.input.conversations import (
    AssistantMessage,
    Content,
    ImageFileMessage,
    PdfFileMessage,
    PlainTextFileMessage,
    UserMessage,
    )
from logyca_ai.utils.helpers.general_utils import get_random_name_datetime, delete_files_by_modification_hours
from logyca_ai.utils.helpers.text_extraction import extract_text_from_pdf_file
from logyca_ai.utils.helpers.content_loaders import (
    get_base64_from_file,
    load_text_from_url,
    save_base64_to_file,
    save_file_from_url,
)