import json
import os
from logging import getLogger

import gspread
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from google.oauth2.service_account import Credentials

from .enums import LanguageCodeType

logger = getLogger(__file__)


class Translator:
    key = "Translator-data"

    cache_duration = timezone.timedelta(minutes=1).total_seconds()

    def __init__(self, sheet_id=None, sheet_name=None, target_language: str = "EN"):
        self.sheet_id = (
            sheet_id
            or getattr(settings, "LEARNGUAL_TRANSLATE_SHEET_ID", None)
            or os.getenv("LEARNGUAL_TRANSLATE_SHEET_ID")
        )
        self.sheet_name = (
            sheet_name
            or getattr(settings, "LEARNGUAL_TRANSLATE_SHEET_NAME", None)
            or os.getenv("LEARNGUAL_TRANSLATE_SHEET_NAME")
        )
        assert (
            self.sheet_id
        ), "`LEARNGUAL_TRANSLATE_SHEET_ID` must be set in enviroment variable or Django setting"
        assert (
            self.sheet_name
        ), "`LEARNGUAL_TRANSLATE_SHEET_NAME` must be set in enviroment variable or Django setting"

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = json.loads(
            getattr(settings, "LEARNGUAL_GOOGLE_BOT_GRED", None)
            or os.getenv("LEARNGUAL_GOOGLE_BOT_GRED")
            or "{}"
        )
        credentials = Credentials.from_service_account_info(creds, scopes=scopes)
        self.gc = gspread.authorize(credentials)
        self.translations = self.load_translations()
        self.target_language = target_language

    def load_translations(self):
        # if data := cache.get(self.key):
        #     self.headers = data.get("headers")
        #     return data.get("translations")

        sheet = self.gc.open_by_key(self.sheet_id)
        worksheet = sheet.worksheet(self.sheet_name)
        data = worksheet.get_all_values()

        self.headers = [x.upper() for x in data[0]]
        translations = {}

        for row in data[1:]:
            en_value = row[0].strip()
            translations[en_value] = {
                self.headers[i]: row[i] for i in range(1, len(self.headers))
            }
        cache.set(
            self.key,
            {"headers": self.headers, "translations": translations},
            timeout=self.cache_duration,
        )
        return translations

    def get_language_code(self, language: str) -> str:
        languages = {
            key.strip().upper(): value.strip().upper()
            for key, value in LanguageCodeType.dict_name_key().items()
        }
        if not language:
            language = "EN"
        language = language.strip().upper()
        return languages.get(language, language)

    def log_microcopy(self, text: str):
        sheet = self.gc.open_by_key(self.sheet_id)
        worksheet = sheet.worksheet(self.sheet_name)
        # Find the first empty row in the English column
        worksheet.insert_row([text.strip()], index=2)
        self.translations[text] = ""
        cache.set(
            self.key,
            {"headers": self.headers, "translations": self.translations},
            timeout=self.cache_duration,
        )
        logger.info(f"Logged missing microcopy: {text}")

    def add_language_column(self, language: str):
        sheet = self.gc.open_by_key(self.sheet_id)
        worksheet = sheet.worksheet(self.sheet_name)
        # Add new column with target language header
        col_count = len(worksheet.row_values(1))
        worksheet.update_cell(1, col_count + 1, language.upper())
        logger.info(f"Added new language column: {language}")
        self.headers.append(language.upper())
        cache.set(
            self.key,
            {"headers": self.headers, "translations": self.translations},
            timeout=self.cache_duration,
        )

    def translate(self, text: str, target_language: str):
        target_language = self.get_language_code(target_language)
        if target_language.upper() not in self.headers:
            self.add_language_column(target_language)
            return text
        stripped_text = text.strip()
        translated_dict = self.translations.get(stripped_text)
        if not translated_dict:
            if translated_dict is None:
                self.log_microcopy(text)
            return stripped_text

        translated_text = translated_dict.get(target_language, text)
        if not translated_text:
            return stripped_text

        return translated_text

    def get_translation(
        self, text, target_language: str | None = None, **kwargs
    ) -> str:
        target_language = target_language or self.target_language
        assert target_language, "target_language is required."

        result = self.translate(text, target_language)
        if kwargs:
            result = self.render(result, **kwargs)

        return result

    def render(self, text: str, **kwargs):
        if not text:
            return text
        try:
            return text.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Imcomplete kwargs for {kwargs} for text {text}") from e
