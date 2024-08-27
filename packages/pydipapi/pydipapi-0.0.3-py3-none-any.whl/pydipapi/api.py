import logging
import os
import re
from typing import List, Union, Optional
import requests
from pydantic import parse_obj_as
from .type import Vorgangsbezug, Vorgangspositionbezug

# Configure logging for the library
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DipAnfrage:
    BASE_URL = "https://search.dip.bundestag.de/api/v1/"
    DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2})?$"

    def __init__(self, apikey: Optional[str] = None, df: bool = False):
        """
        Initialize the API key and other instance variables.

        Args:
            apikey (Optional[str]): API key for authentication.
            df (bool): Whether to return data as a pandas DataFrame.
        """
        self.apikey = apikey or os.getenv('DIP_API_KEY')
        if not self.apikey:
            raise ValueError("API key must be provided")
        self.apikey_param = f"&apikey={self.apikey}"
        self.cursor = ""
        self.documents = []
        self.df = df
        self.pandas_installed = self.__check_pandas_installed()
        if self.df and not self.pandas_installed:
            logger.warning("Pandas is not installed. Returning data as a list of dictionaries")
        if self.df and self.pandas_installed:
            import pandas as pd
            logger.info("Pandas is installed. Returning data as a pandas DataFrame")

    def __check_pandas_installed(self) -> bool:
        """
        Check if pandas is installed.

        Returns:
            bool: True if pandas is installed, False otherwise.
        """
        try:
            import pandas as pd
            return True
        except ImportError:
            return False

    def __build_query_params(self, **kwargs) -> str:
        """
        Build query parameters from the provided keyword arguments.

        Args:
            kwargs: Keyword arguments representing query parameters.

        Returns:
            str: A string of query parameters.
        """
        return '&'.join(f'{key}={value}' for key, value in kwargs.items() if value is not None)

    def __set_cursor(self, composeurl: str):
        """
        Set the request URL based on the cursor value.

        Args:
            composeurl (str): The base URL to which the cursor parameter is appended.
        """
        self.adresse = f"{composeurl}&cursor={self.cursor}" if self.cursor else composeurl

    def __validate_datetime_format(self, date_str: str) -> bool:
        """
        Validate if the given date string matches the required format.

        Args:
            date_str (str): The date string to validate.

        Returns:
            bool: True if the date string matches the format, False otherwise.
        """
        return bool(re.match(self.DATE_PATTERN, date_str))

    def __anfrage(self) -> Optional[dict]:
        """
        Make a GET request to the API and handle potential errors.

        Returns:
            Optional[dict]: The JSON response from the API if successful, otherwise None.
        """
        try:
            logger.debug(f"Making request to URL: {self.adresse}")
            response = requests.get(url=self.adresse)
            response.raise_for_status()
            data = response.json()
            self.cursor = data.get('cursor', self.cursor)
            self.documents.extend(data.get('documents', []))
            logger.info(f"Successfully retrieved {len(data.get('documents', []))} documents.")
            return data
        except requests.exceptions.RequestException as err:
            logger.error(f"Request error occurred: {err}")
        return None

    def __fetch_documents(self, endpoint: str, anzahl: Optional[int], params: dict) -> Union[
        List[dict], 'pd.DataFrame']:
        """
        Fetch documents from the API using specified parameters.

        Args:
            endpoint (str): The API endpoint to query.
            anzahl (Optional[int]): The number of documents to fetch.
            params (dict): Additional query parameters.

        Returns:
            Union[List[dict], pd.DataFrame]: A list of document dictionaries or a pandas DataFrame.
        """
        if not (anzahl or (params.get('f.aktualisiert.start') and params.get('f.aktualisiert.end'))):
            logger.error(
                "Either 'anzahl' must be specified or both 'aktualisiert_start' and 'aktualisiert_end' must be provided.")
            raise ValueError(
                "Either 'anzahl' must be specified or both 'aktualisiert_start' and 'aktualisiert_end' must be provided.")

        self.documents = []
        composeurl = self.BASE_URL + endpoint + '?' + self.apikey_param
        urlquery = ''.join(f'&{key}={value}' for key, value in params.items() if value)
        while anzahl is None or len(self.documents) < anzahl:
            self.__set_cursor(composeurl + urlquery)
            if not self.__anfrage():
                break
            if len(self.documents) == 0:
                break
        logger.info(f"Total documents fetched: {len(self.documents)}")

        if self.df and self.pandas_installed:
            return pd.DataFrame(self.documents[:anzahl] if anzahl else self.documents)
        return self.documents[:anzahl] if anzahl else self.documents

    def get_person(self, anzahl: int = None, aktualisiert_start: str = None, aktualisiert_end: str = None) -> List[
        dict]:
        """
        Retrieve person data from the API.

        Args:
            anzahl (int, optional): Number of records to retrieve.
            aktualisiert_start (str, optional): Start date for filtering updated records.
            aktualisiert_end (str, optional): End date for filtering updated records.

        Returns:
            List[dict]: A list of person dictionaries.
        """
        return self.__fetch_documents(
            'person',
            anzahl,
            {
                'f.aktualisiert.start': aktualisiert_start if self.__validate_datetime_format(
                    aktualisiert_start) else None,
                'f.aktualisiert.end': aktualisiert_end if self.__validate_datetime_format(aktualisiert_end) else None
            }
        )

    def get_person_ids(self, ids: List[int]) -> List[dict]:
        """
        Retrieve persons by their IDs.

        Args:
            ids (List[int]): A list of person IDs.

        Returns:
            List[dict]: A list of person dictionaries.
        """
        self.documents = []
        self.adresse = self.BASE_URL + "person?" + ''.join(f'&f.id={i}' for i in ids)
        if self.__anfrage():
            logger.info(f"Successfully retrieved documents for IDs: {ids}")
        return self.documents

    def get_person_id(self, id: int) -> Union[dict, None]:
        """
        Retrieve a single person by their ID.

        Args:
            id (int): The ID of the person.

        Returns:
            Union[dict, None]: The person dictionary or None if not found.
        """
        self.documents = []
        self.adresse = f"{self.BASE_URL}person/{id}/?"
        result = self.__anfrage()
        if result:
            logger.info(f"Successfully retrieved document for ID: {id}")
        return result

    def get_aktivitaet(self, anzahl: int = None, aktualisiert_start: str = None, aktualisiert_end: str = None) -> List[
        dict]:
        """
        Retrieve activity data from the API.

        Args:
            anzahl (int, optional): Number of records to retrieve.
            aktualisiert_start (str, optional): Start date for filtering updated records.
            aktualisiert_end (str, optional): End date for filtering updated records.

        Returns:
            List[dict]: A list of activity dictionaries.
        """
        return self.__fetch_documents(
            'aktivitaet',
            anzahl,
            {
                'f.aktualisiert.start': aktualisiert_start if self.__validate_datetime_format(
                    aktualisiert_start) else None,
                'f.aktualisiert.end': aktualisiert_end if self.__validate_datetime_format(aktualisiert_end) else None
            }
        )

    def get_drucksache(self, anzahl: int = None, text: bool = True, aktualisiert_start: str = None,
                       aktualisiert_end: str = None,
                       datum_start: str = None, datum_end: str = None, dokumentnummer: list = None,
                       drucksachetyp: str = None,
                       id: list = None, ressort_fdf: list = None, titel: list = None, urheber: list = None,
                       vorgangstyp: list = None, vorgangstyp_notation: list = None, wahlperiode: list = None,
                       zuordnung: str = None) -> List[dict]:
        """
        Retrieve document data from the API.

        Args:
            anzahl (int, optional): Number of records to retrieve.
            aktualisiert_start (str, optional): Start date for filtering updated records.
            aktualisiert_end (str, optional): End date for filtering updated records.
            datum_start (str, optional): Start date for filtering document dates.
            datum_end (str, optional): End date for filtering document dates.
            dokumentnummer (list, optional): List of document numbers.
            drucksachetyp (str, optional): Type of document.
            id (list, optional): List of entity IDs.
            ressort_fdf (list, optional): List of leading departments.
            titel (list, optional): List of titles.
            urheber (list, optional): List of authors.
            vorgangstyp (list, optional): List of process types.
            vorgangstyp_notation (list, optional): List of process type notations.
            wahlperiode (list, optional): List of election periods.
            zuordnung (str, optional): Assignment of the entity.

        Returns:
            List[dict]: A list of document references.
        """
        if not (aktualisiert_start and aktualisiert_end):
            if anzahl is None:
                raise ValueError("Anzahl must be provided if aktualisiert_start and aktualisiert_end are not set.")
        if aktualisiert_start and not self.__validate_datetime_format(aktualisiert_start):
            raise ValueError("Invalid format for aktualisiert_start")
        if aktualisiert_end and not self.__validate_datetime_format(aktualisiert_end):
            raise ValueError("Invalid format for aktualisiert_end")

        query_params = self.__build_query_params(
            f_aktualisiert_start=aktualisiert_start,
            f_aktualisiert_end=aktualisiert_end,
            f_datum_start=datum_start,
            f_datum_end=datum_end,
            f_dokumentnummer=','.join(dokumentnummer) if dokumentnummer else None,
            f_drucksachetyp=drucksachetyp,
            f_id=','.join(map(str, id)) if id else None,
            f_ressort_fdf=','.join(ressort_fdf) if ressort_fdf else None,
            f_titel=','.join(titel) if titel else None,
            f_urheber=','.join(urheber) if urheber else None,
            f_vorgangstyp=','.join(vorgangstyp) if vorgangstyp else None,
            f_vorgangstyp_notation=','.join(map(str, vorgangstyp_notation)) if vorgangstyp_notation else None,
            f_wahlperiode=','.join(map(str, wahlperiode)) if wahlperiode else None,
            f_zuordnung=zuordnung
        )

        self.documents = []
        self.composeurl = f'{self.BASE_URL}drucksache?{query_params}'
        while anzahl is None or len(self.documents) < anzahl:
            self.__set_cursor(self.composeurl)
            if not self.__anfrage():
                break
        return self.documents[:anzahl] if anzahl else self.documents

    def get_plenarprotokoll(self, anzahl: int = None, text: bool = True, aktualisiert_start: str = None,
                            aktualisiert_end: str = None,
                            datum_start: str = None, datum_end: str = None, dokumentnummer: list = None,
                            id: list = None,
                            vorgangstyp: list = None, vorgangstyp_notation: list = None, wahlperiode: list = None,
                            zuordnung: str = None) -> List[dict]:
        """
        Retrieve plenary protocol data from the API.

        Args:
            anzahl (int, optional): Number of records to retrieve.
            aktualisiert_start (str, optional): Start date for filtering updated records.
            aktualisiert_end (str, optional): End date for filtering updated records.
            datum_start (str, optional): Start date for filtering document dates.
            datum_end (str, optional): End date for filtering document dates.
            dokumentnummer (list, optional): List of document numbers.
            id (list, optional): List of entity IDs.
            vorgangstyp (list, optional): List of process types.
            vorgangstyp_notation (list, optional): List of process type notations.
            wahlperiode (list, optional): List of election periods.
            zuordnung (str, optional): Assignment of the entity.

        Returns:
            List[dict]: A list of plenary protocol references.
        """
        if not (aktualisiert_start and aktualisiert_end):
            if anzahl is None:
                raise ValueError("Anzahl must be provided if aktualisiert_start and aktualisiert_end are not set.")
        if aktualisiert_start and not self.__validate_datetime_format(aktualisiert_start):
            raise ValueError("Invalid format for aktualisiert_start")
        if aktualisiert_end and not self.__validate_datetime_format(aktualisiert_end):
            raise ValueError("Invalid format for aktualisiert_end")

        query_params = self.__build_query_params(
            f_aktualisiert_start=aktualisiert_start,
            f_aktualisiert_end=aktualisiert_end,
            f_datum_start=datum_start,
            f_datum_end=datum_end,
            f_dokumentnummer=','.join(dokumentnummer) if dokumentnummer else None,
            f_id=','.join(map(str, id)) if id else None,
            f_vorgangstyp=','.join(vorgangstyp) if vorgangstyp else None,
            f_vorgangstyp_notation=','.join(map(str, vorgangstyp_notation)) if vorgangstyp_notation else None,
            f_wahlperiode=','.join(map(str, wahlperiode)) if wahlperiode else None,
            f_zuordnung=zuordnung,
        )

        self.documents = []
        self.composeurl = f'{self.BASE_URL}plenarprotokoll?{self.apikey_param}&{query_params}'
        while anzahl is None or len(self.documents) < anzahl:
            self.__set_cursor(self.composeurl)
            res = self.__anfrage()
            self.documents.append(res)
            print(len(res))
            print(res['documents'][0])
            if len(res) == 0:
                logger.info("No more documents found.")
                break
        if anzahl > 0:
            return self.documents[:anzahl]
        else:
            return self.documents

    def get_vorgang(self, anzahl: int = None, aktualisiert_start: str = None, aktualisiert_end: str = None,
                    beratungsstand: list = None, datum_start: str = None, datum_end: str = None,
                    deskriptor: list = None,
                    dokumentart: str = None, dokumentnummer: list = None, drucksache: int = None,
                    drucksachetyp: str = None,
                    frage_nummer: list = None, gesta: list = None, id: list = None, initiative: list = None,
                    plenarprotokoll: int = None, ressort_fdf: list = None, sachgebiet: list = None, titel: list = None,
                    urheber: list = None, verkuendung_fundstelle: list = None, vorgangstyp: list = None,
                    vorgangstyp_notation: list = None, wahlperiode: list = None) -> List[Vorgangsbezug]:
        """
        Retrieve process data from the API.

        Args:
            anzahl (int, optional): Number of records to retrieve.
            aktualisiert_start (str, optional): Start date for filtering updated records.
            aktualisiert_end (str, optional): End date for filtering updated records.
            (other parameters...)

        Returns:
            List[Vorgangsbezug]: A list of process references.
        """
        if not (aktualisiert_start and aktualisiert_end):
            if anzahl is None:
                raise ValueError("Anzahl must be provided if aktualisiert_start and aktualisiert_end are not set.")
        if aktualisiert_start and not self.__validate_datetime_format(aktualisiert_start):
            raise ValueError("Invalid format for aktualisiert_start")
        if aktualisiert_end and not self.__validate_datetime_format(aktualisiert_end):
            raise ValueError("Invalid format for aktualisiert_end")

        query_params = self.__build_query_params(
            f_aktualisiert_start=aktualisiert_start,
            f_aktualisiert_end=aktualisiert_end,
            f_beratungsstand=','.join(beratungsstand) if beratungsstand else None,
            f_datum_start=datum_start,
            f_datum_end=datum_end,
            f_deskriptor=','.join(deskriptor) if deskriptor else None,
            f_dokumentart=dokumentart,
            f_dokumentnummer=','.join(dokumentnummer) if dokumentnummer else None,
            f_drucksache=drucksache,
            f_drucksachetyp=drucksachetyp,
            f_frage_nummer=','.join(frage_nummer) if frage_nummer else None,
            f_gesta=','.join(gesta) if gesta else None,
            f_id=','.join(map(str, id)) if id else None,
            f_initiative=','.join(initiative) if initiative else None,
            f_plenarprotokoll=plenarprotokoll,
            f_ressort_fdf=','.join(ressort_fdf) if ressort_fdf else None,
            f_sachgebiet=','.join(sachgebiet) if sachgebiet else None,
            f_titel=','.join(titel) if titel else None,
            f_urheber=','.join(urheber) if urheber else None,
            f_verkuendung_fundstelle=','.join(verkuendung_fundstelle) if verkuendung_fundstelle else None,
            f_vorgangstyp=','.join(vorgangstyp) if vorgangstyp else None,
            f_vorgangstyp_notation=','.join(map(str, vorgangstyp_notation)) if vorgangstyp_notation else None,
            f_wahlperiode=','.join(map(str, wahlperiode)) if wahlperiode else None
        )

        self.documents = []
        self.composeurl = f'{self.BASE_URL}vorgang?{query_params}'
        while anzahl is None or len(self.documents) < anzahl:
            self.__set_cursor(self.composeurl)
            if not self.__anfrage():
                break
        return parse_obj_as(List[Vorgangsbezug], self.documents[:anzahl] if anzahl else self.documents)

    def get_vorgangsposition(self, anzahl: int = None, aktualisiert_start: str = None, aktualisiert_end: str = None,
                             datum_start: str = None, datum_end: str = None, dokumentart: str = None,
                             dokumentnummer: list = None, drucksache: int = None, drucksachetyp: str = None,
                             frage_nummer: list = None, id: list = None, plenarprotokoll: int = None,
                             ressort_fdf: list = None, titel: list = None, urheber: list = None, vorgang: int = None,
                             vorgangstyp: list = None, vorgangstyp_notation: list = None, wahlperiode: list = None,
                             zuordnung: str = None) -> List[Vorgangspositionbezug]:
        """
        Retrieve process position data from the API.

        Args:
            anzahl (int, optional): Number of records to retrieve.
            aktualisiert_start (str, optional): Start date for filtering updated records.
            aktualisiert_end (str, optional): End date for filtering updated records.
            (other parameters...)

        Returns:
            List[Vorgangspositionbezug]: A list of process position references.
        """
        if not (aktualisiert_start and aktualisiert_end):
            if anzahl is None:
                raise ValueError("Anzahl must be provided if aktualisiert_start and aktualisiert_end are not set.")
        if aktualisiert_start and not self.__validate_datetime_format(aktualisiert_start):
            raise ValueError("Invalid format for aktualisiert_start")
        if aktualisiert_end and not self.__validate_datetime_format(aktualisiert_end):
            raise ValueError("Invalid format for aktualisiert_end")

        query_params = self.__build_query_params(
            f_aktualisiert_start=aktualisiert_start,
            f_aktualisiert_end=aktualisiert_end,
            f_datum_start=datum_start,
            f_datum_end=datum_end,
            f_dokumentart=dokumentart,
            f_dokumentnummer=','.join(dokumentnummer) if dokumentnummer else None,
            f_drucksache=drucksache,
            f_drucksachetyp=drucksachetyp,
            f_frage_nummer=','.join(frage_nummer) if frage_nummer else None,
            f_id=','.join(map(str, id)) if id else None,
            f_plenarprotokoll=plenarprotokoll,
            f_ressort_fdf=','.join(ressort_fdf) if ressort_fdf else None,
            f_titel=','.join(titel) if titel else None,
            f_urheber=','.join(urheber) if urheber else None,
            f_vorgang=vorgang,
            f_vorgangstyp=','.join(vorgangstyp) if vorgangstyp else None,
            f_vorgangstyp_notation=','.join(map(str, vorgangstyp_notation)) if vorgangstyp_notation else None,
            f_wahlperiode=','.join(map(str, wahlperiode)) if wahlperiode else None,
            f_zuordnung=zuordnung
        )

        self.documents = []
        self.composeurl = f'{self.BASE_URL}vorgangsposition?{query_params}'
        while anzahl is None or len(self.documents) < anzahl:
            self.__set_cursor(self.composeurl)
            if not self.__anfrage():
                break
        return parse_obj_as(List[Vorgangspositionbezug], self.documents[:anzahl] if anzahl else self.documents)