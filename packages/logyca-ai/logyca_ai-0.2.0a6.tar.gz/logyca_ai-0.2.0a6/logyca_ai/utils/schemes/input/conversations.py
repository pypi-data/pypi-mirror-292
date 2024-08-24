from logyca_ai.utils.constants.content import ContentType, ContentRole
from logyca_ai.utils.constants.image import ImageResolution
from logyca_ai.utils.helpers.content_loaders import save_base64_to_file, save_file_from_url, load_text_from_url, decode_base64_to_str
from logyca_ai.utils.helpers.general_utils import get_random_name_datetime, delete_files_by_modification_hours
from logyca_ai.utils.helpers.text_extraction import extract_text_from_pdf_file
from pydantic import BaseModel, AliasChoices, Field, model_validator
from typing import Any
import os

class MessageExceptionErrors:
    UNSUPPORTED_IMAGE_FORMAT="Unsupported image format: {}"
    UNSUPPORTED_PDF_FORMAT="Unsupported pdf format: {}"
    UNSUPPORTED_FILE_FORMAT="Unsupported file format: {}"

class Content(BaseModel):
    system: str = Field(default="Personality, context, purpose.",validation_alias=AliasChoices(ContentRole.SYSTEM))
    messages: list = Field(default=[],validation_alias=AliasChoices("messages"))
    
    @model_validator(mode="before")
    def check_keys(cls, values):
        return values

    def to_dict(self)->dict:
        tmp = self.__dict__.copy()
        tmp["messages"] = [message.to_dict() for message in tmp["messages"]]
        return tmp

class UserMessage(BaseModel):
    additional_content: Any = Field(default="",validation_alias=AliasChoices("additional_content"))
    type: str = Field(default=ContentType.TEXT,validation_alias=AliasChoices("type"))
    user: str = Field(default="",validation_alias=AliasChoices("user"))
    
    @model_validator(mode="before")
    def check_keys(cls, values):
        return values

    def to_dict(self)->dict:
        return self.__dict__

    @classmethod
    def get_supported_types(cls)->list:        
        return ContentType.get_type_list()

    @classmethod
    def get_default_types(cls)->list:        
        return [ContentType.TEXT]

class AssistantMessage(BaseModel):
    assistant: str = Field(default="",validation_alias=AliasChoices("assistant"))
    
    @model_validator(mode="before")
    def check_keys(cls, values):
        return values

    def to_dict(self)->dict:
        return self.__dict__
    
class ImageFileMessage(BaseModel):
    base64_content_or_url: str = Field(default="",validation_alias=AliasChoices("base64_content_or_url"))
    image_format: str = Field(default="",validation_alias=AliasChoices("image_format"))
    image_resolution: str = Field(default=ImageResolution.AUTO,validation_alias=AliasChoices("image_resolution"))
    
    @model_validator(mode="before")
    def check_keys(cls, values):
        return values

    def to_dict(self)->dict:
        return self.__dict__
    
    def __get_mime_types(self,extension:str=None)->str|dict|None:
        mime_types={
            "bmp":"bmp",
            "gif":"gif",
            "jpeg":"jpeg",
            "jpg":"jpg",
            "png":"png",
            "svg":"svg+xml",
            "webp":"webp",
        }
        if extension is None:
            return mime_types
        else:
            return mime_types.get(extension,None)

    @classmethod
    def get_supported_formats(cls)->list:        
        return [key for key, value in cls().__get_mime_types().items()]
        
    @classmethod
    def get_default_types(cls)->list:        
        return [ContentType.IMAGE_URL,ContentType.IMAGE_BASE64]

    def build_message_content(self)->dict|None:
        if self.image_format == ContentType.IMAGE_URL:
            image_url=self.base64_content_or_url
        else: 
            mime_type = self.__get_mime_types(self.image_format)
            if(mime_type is None): raise ValueError(MessageExceptionErrors.UNSUPPORTED_IMAGE_FORMAT.format(self.image_format))
            image_url=f"data:image/{mime_type};base64,{self.base64_content_or_url}"
        return {
            "type": "image_url",
            "image_url": {
                "url" : image_url, 
                "detail" : str(self.image_resolution)
            }
        }

class PdfFileMessage(BaseModel):
    base64_content_or_url: str = Field(default="",validation_alias=AliasChoices("base64_content_or_url"))
    pdf_format: str = Field(default="",validation_alias=AliasChoices("pdf_format"))
    
    @model_validator(mode="before")
    def check_keys(cls, values):
        return values

    def to_dict(self)->dict:
        return self.__dict__
    
    def __get_pdf_formats(self,extension:str=None)->str|dict|None:
        pdf_formats={
            "pdf":"pdf",
        }
        if extension is None:
            return pdf_formats
        else:
            return pdf_formats.get(extension,None)

    @classmethod
    def get_supported_formats(cls)->list:        
        return [key for key, value in cls().__get_pdf_formats().items()]
        
    @classmethod
    def get_default_types(cls)->list:        
        return [ContentType.PDF_URL,ContentType.PDF_BASE64]

    def build_message_content(self,advanced_image_recognition:bool=False,ocr_engine_path:str=None,output_temp_dir:str=None,cleanup_output_temp_dir_after_hours: int = 24)->str|None:
        """
        Build the supported message list.

        :param content: Content to send to chatgpt, which consists of system and messages.
        :type content: str
        :param advanced_image_recognition: (pdf for now) Indicates whether to perform text recognition on images within the files or documents.
                                If True, OCR techniques will be used to extract text from images.
        :type advanced_image_recognition: bool
        :param ocr_engine_path: Path to the OCR executable. If provided, this path will be used instead of the default.
        :type ocr_engine_path: str, optional
        :param output_temp_dir: Temporary directory for storing output files.
                                If not provided, a default tmp temporary directory in the application root folder will be used.
        :type output_temp_dir: str, optional
        :param cleanup_output_temp_dir_after_hours: Number of hours after which the files in the temporary directory will be deleted on the next call of the function.
        :type cleanup_output_temp_dir_after_hours: int, optional

        :return: Supported message list.
        :rtype: str
        """
        if output_temp_dir is None: output_temp_dir=os.path.abspath(os.path.join(os.getcwd(),"tmp"))
        if not os.path.exists(output_temp_dir):
            os.makedirs(output_temp_dir)
        delete_files_by_modification_hours(output_temp_dir,cleanup_output_temp_dir_after_hours)
        pdf_filename = f"{get_random_name_datetime()}.pdf"
        pdf_tmp_to_work = os.path.abspath(os.path.join(output_temp_dir,pdf_filename))
        if self.pdf_format == ContentType.PDF_URL:
            save_file_from_url(self.base64_content_or_url,output_temp_dir,pdf_filename)
            pdf_text=extract_text_from_pdf_file(pdf_tmp_to_work,advanced_image_recognition=advanced_image_recognition,ocr_engine_path=ocr_engine_path,output_temp_dir=output_temp_dir)
            os.remove(pdf_tmp_to_work)
            return pdf_text
        else:
            if(self.__get_pdf_formats(self.pdf_format) is None): raise ValueError(MessageExceptionErrors.UNSUPPORTED_PDF_FORMAT.format(self.pdf_format))
            save_base64_to_file(self.base64_content_or_url,output_temp_dir,pdf_filename)
            pdf_text=extract_text_from_pdf_file(pdf_tmp_to_work,advanced_image_recognition=advanced_image_recognition,ocr_engine_path=ocr_engine_path,output_temp_dir=output_temp_dir)
            os.remove(pdf_tmp_to_work)
            return pdf_text            

class PlainTextFileMessage(BaseModel):
    base64_content_or_url: str = Field(default="",validation_alias=AliasChoices("base64_content_or_url"))
    file_format: str = Field(default="",validation_alias=AliasChoices("file_format"))
    
    @model_validator(mode="before")
    def check_keys(cls, values):
        return values

    def to_dict(self)->dict:
        return self.__dict__
    
    def __get_file_formats(self,extension:str=None)->str|dict|None:
        file_formats={
            "txt":"txt",
            "csv":"csv",
        }
        if extension is None:
            return file_formats
        else:
            return file_formats.get(extension,None)

    @classmethod
    def get_supported_formats(cls)->list:        
        return [key for key, value in cls().__get_file_formats().items()]
        
    @classmethod
    def get_default_types(cls)->list:        
        return [ContentType.PLAIN_TEXT_URL,ContentType.PLAIN_TEXT_BASE64]

    def build_message_content(self)->str|None:
        if self.file_format == ContentType.PLAIN_TEXT_URL:
            plain_text=load_text_from_url(self.base64_content_or_url)
            return plain_text
        else:
            if(self.__get_file_formats(self.file_format) is None): raise ValueError(MessageExceptionErrors.UNSUPPORTED_FILE_FORMAT.format(self.file_format))
            plain_text=decode_base64_to_str(self.base64_content_or_url)
            return plain_text

