<p align="center">
  <a href="https://logyca.com/"><img src="https://logyca.com/sites/default/files/logyca.png" alt="Logyca"></a>
</p>
<p align="center">
    <em>LOGYCA public libraries</em>
</p>

<p align="center">
<a href="https://pypi.org/project/logyca-ai" target="_blank">
    <img src="https://img.shields.io/pypi/v/logyca-ai?color=orange&label=PyPI%20Package" alt="Package version">
</a>
<a href="(https://www.python.org" target="_blank">
    <img src="https://img.shields.io/badge/Python-%5B%3E%3D3.8%2C%3C%3D3.11%5D-orange" alt="Python">
</a>
</p>


---

# About us

* <a href="http://logyca.com" target="_blank">LOGYCA Company</a>
* <a href="https://www.youtube.com/channel/UCzcJtxfScoAtwFbxaLNnEtA" target="_blank">LOGYCA Youtube Channel</a>
* <a href="https://www.linkedin.com/company/logyca" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Linkedin"></a>
* <a href="https://twitter.com/LOGYCA_Org" target="_blank"><img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter"></a>
* <a href="https://www.facebook.com/OrganizacionLOGYCA/" target="_blank"><img src="https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white" alt="Facebook"></a>

---

# LOGYCA public libraries: To interact with ChatGPT and analyze documents, files and other functionality of the OpenAI library.

[Source code](https://github.com/logyca/python-libraries/tree/main/logyca-ai)
| [Package (PyPI)](https://pypi.org/project/logyca-ai/)
| [Samples](https://github.com/logyca/python-libraries/tree/main/logyca-ai/samples)


## To interact with the examples, keep the following in mind

FastAPI example. Through Swagger, you can:
- https://github.com/logyca/python-libraries/tree/main/logyca-ai/samples/fastapi_async
- Use the example endpoints to obtain the input schemas for the post method and interact with the available parameters.
- Endpoint publishing is asynchronous of openai SDK.
- The model used is ChatGPT-4o for testing.

Script example. Through of code, you can:
- https://github.com/logyca/python-libraries/tree/main/logyca-ai/samples/script_app_sync
- Examples shared with the example written in FastAPI.
- The examples use synchronous functionality of openai SDK.
- The model used is ChatGPT-4o for testing.

---

# OCR engine to extract images.

- Tesseract is an optical character recognition engine for various operating systems.
  It is free software, released under the Apache License. Originally developed by Hewlett-Packard as proprietary software in the 1980s,
  it was released as open source in 2005 and development was sponsored by Google in 2006

## Install

- (Source Code) https://tesseract-ocr.github.io/tessdoc/Downloads.html
- (Windows Binaries) https://github.com/UB-Mannheim/tesseract/wiki
- (Linux/Docker) apt-get -y install tesseract-ocr

# Example for simple conversation.

```json
{
  "system": "Voy a definirte tu personalidad, contexto y proposito.\nActua como un experto en venta de frutas.\nSe muy positivo.\nTrata a las personas de usted, nunca tutees sin importar como te escriban.",
  "messages": [
    {
      "additional_content": "",
      "type": "text",
      "user": "Dime 5 frutas amarillas"
    },
    {
      "assistant": "\n¡Claro! Aquí te van 5 frutas amarillas:\n\n1. Plátano\n2. Piña\n3. Mango\n4. Melón\n5. Papaya\n"
    },
    {
      "additional_content": "",
      "type": "text",
      "user": "Dame los nombres en ingles."
    }
  ]
}
```

---

# Example for image conversation.

## Using public published URL for image
```json
{
  "system": "Actua como una maquina lectora de imagenes.\nDevuelve la información sin lenguaje natural, sólo responde lo que se está solicitando.\nEl dispositivo que va a interactuar contigo es una api, y necesita la información sin markdown u otros caracteres especiales.",
  "messages": [
    {
      "additional_content": {
        "base64_content_or_url": "https://raw.githubusercontent.com/logyca/python-libraries/main/logyca-ai/logyca_ai/assets_for_examples/file_or_documents/image.png",
        "image_format": "image_url",
        "image_resolution": "auto"
      },
      "type": "image_url",
      "user": "Extrae el texto que recibas en la imagen y devuelvelo en formato json."
    }
  ]
}
```

## Using image content in base64
```json
{
  "system": "Actua como una maquina lectora de imagenes.\nDevuelve la información sin lenguaje natural, sólo responde lo que se está solicitando.\nEl dispositivo que va a interactuar contigo es una api, y necesita la información sin markdown u otros caracteres especiales.",
  "messages": [
    {
      "additional_content": {
        "base64_content_or_url": "<base64 image png content>",
        "image_format": "png",
        "image_resolution": "auto"
      },
      "type": "image_base64",
      "user": "Extrae el texto que recibas en la imagen y devuelvelo en formato json."
    }
  ]
}
```

---

# Example for pdf conversation.

## Using public published URL for pdf
```json
{
  "system": "No uses lenguaje natural para la respuesta.\nDame la información que puedas extraer de la imagen en formato JSON.\nSolo devuelve la información, no formatees con caracteres adicionales la respuesta.",
  "messages": [
    {
      "additional_content": {
        "base64_content_or_url": "https://raw.githubusercontent.com/logyca/python-libraries/main/logyca-ai/logyca_ai/assets_for_examples/file_or_documents/pdf.pdf",
        "pdf_format": "pdf_url"
      },
      "type": "pdf_url",
      "user": "Dame los siguientes datos: Expediente, radicación, Fecha, Numero de registro, Vigencia."
    }
  ]
}
```

## Using pdf content in base64
```json
{
  "system": "No uses lenguaje natural para la respuesta.\nDame la información que puedas extraer de la imagen en formato JSON.\nSolo devuelve la información, no formatees con caracteres adicionales la respuesta.",
  "messages": [
    {
      "additional_content": {
        "base64_content_or_url": "<base64 pdf content>",
        "pdf_format": "pdf"
      },
      "type": "pdf_base64",
      "user": "Dame los siguientes datos: Expediente, radicación, Fecha, Numero de registro, Vigencia."
    }
  ]
}
```


---

# Semantic Versioning

logyca_ai < MAJOR >.< MINOR >.< PATCH >

* **MAJOR**: version when you make incompatible API changes
* **MINOR**: version when you add functionality in a backwards compatible manner
* **PATCH**: version when you make backwards compatible bug fixes

## Definitions for releasing versions
* https://peps.python.org/pep-0440/

    - X.YaN (Alpha release): Identify and fix early-stage bugs. Not suitable for production use.
    - X.YbN (Beta release): Stabilize and refine features. Address reported bugs. Prepare for official release.
    - X.YrcN (Release candidate): Final version before official release. Assumes all major features are complete and stable. Recommended for testing in non-critical environments.
    - X.Y (Final release/Stable/Production): Completed, stable version ready for use in production. Full release for public use.

---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Types of changes

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

## [0.0.1aX] - 2024-08-02
### Added
- First tests using pypi.org in develop environment.

## [0.1.0] - 2024-08-02
### Added
- Completion of testing and launch into production.

## [0.1.1] - 2024-08-16
### Added
- The functions of extracting text from PDF files are refactored, using disk to optimize the use of ram memory and methods are added to extract text from images within the pages of the PDF files.

## [0.1.2] - 2024-08-26
### Added
- New feature of attaching documents with txt, csv, docx, xlsx extension