"""

Zotero utils and highlights manager in sioyek PDF reader.

Author: eduardotcampos@usp.br

Based on pyzotero and sqlite3.

=======
CONFIGS
=======

To use this script define the variables in this script or as environment variables:

ZOTERO_LIBRARY_ID: Your personal library ID available in https://www.zotero.org/settings/keys,
in the section Your userID for use in API calls.

ZOTERO_API_KEY: Api key, you can obtain in https://www.zotero.org/settings/keys/new.

ZOTERO_LIBRARY_TYPE: Zotero library type, can be 'user' or 'group'.

SIOYEK_LOCAL_DATABASE_FILE_PATH: Sioyek .db local database file path.

SIOYEK_SHARED_DATABASE_FILE_PATH: Sioyek .db shared database file path.

SIOYEK_PATH: Sioyek program path.

ZOTERO_TO_SIOYEK_COLORS: Sioyek highlight type letter associated to each zotero highlight color.

ZOTERO_LOCAL_DIR: Zotero local PDFs directory like 'home/user/Zotero/storage'

"""
import argparse
import ast
import datetime
import hashlib
import os
import pathlib
import re
import sqlite3
import sys
import textwrap
import uuid
from collections.abc import Sequence
from difflib import SequenceMatcher
from os import path, walk
from typing import NamedTuple, Optional, TypedDict, Union

from pyzotero import zotero
from sioyek.sioyek import DocumentPos, Sioyek, clean_path

ZOTERO_LIBRARY_ID = ""
ZOTERO_LOCAL_DIR = ""
ZOTERO_LIBRARY_TYPE = "user"
ZOTERO_API_KEY = ""
SIOYEK_LOCAL_DATABASE_FILE_PATH = ""
SIOYEK_SHARED_DATABASE_FILE_PATH = ""
SIOYEK_PATH = ""
ZOTERO_TO_SIOYEK_COLORS = {
    "#5fb236": "g",
    "#a28ae5": "a",
    "#e56eee": "p",
    "#2ea8e5": "b",
    "#ff6666": "r",
    "#f19837": "o",
    "#ffd400": "y",
}

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MGN = "\033[35m"
CYAN = "\033[36m"
RST = "\033[0m"

ConvertibleToNumbers = Union[str, bytes, int, float]


class ZoteroHighlight(NamedTuple):
    text: str
    color: ConvertibleToNumbers
    page: int
    date_added: str
    date_modified: str
    abs_doc_page: int


class Document(TypedDict):
    id: int
    path: str
    hash: str


def calculate_md5(file_path):
    """

    Calculate a file md5sum hash.

    Parameters
    ----------
    file_path : str
        Complete file path

    Returns
    -------
    hash : str
        md5sum hash string of the file

    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


# -TODO: Check annotationSortIndex value meaning
# -TODO: Check if the use of the annotation_data variable list will have any functionalitty
class ZoteroData:
    zotero_api: zotero.Zotero
    highlights: list
    annotation_data: list
    """

    A class to extract and store zotero highlight annotations from the user database.

    Class to handle highlight type annotations from zotero pdfs, being possible to specify
    the documents to manipulate based on the pdf file name or on the the highlight date of creation.

    Attributes
    ----------
    highlights : list
        list containing Highlight class elements, with the keys:
        text, text of the highlight
        color, str of the html hex code
        page, str of the page number, considering the document numeration
        date_added, Addition of the highlight, formatted like %Y-%m-%d %H:%M:%S
        date_modified, Addition of the highlight, formatted like %Y-%m-%d %H:%M:%S
        abs_doc_page, Page starting in 1

    zotero_api : pyzotero.zotero.Zotero
        pyzotero class object, obtained from the user zotero database, from the given
        library id, library type, and api key

    annotation_data : list
        list of dicts, being each dict a highlight/annotation formatted like:

            key : str
                attachment item id, like 'VENEZY2N'

            version : int
                version of the api

            parentItem : str
                item id of the zotero library parent item of the attachment, like 'I9M4ZAZ9'

            itemType : str
                type of the data, like 'annotation'

            annotationType : str
                type of the annotation, like 'highlight'

            annotationText : str
                The text that is highlighted

            annotationComment : str
                Comment of the annotation

            annotationColor : str
                Html hex code string

            annotationPageLabel : str
                Page number string or label if exists

            annotationSortIndex : str
                Formated like '0000|001579|0359'

            annotationPosition : str
                string of a dict formatted like:
                    pageIndex : int
                        page number index (start in 0)
                    rects : list[list]
                        list of a list containing start x position, start y position,
                        end x position and end y position of the highlight

            tags : list
                Tags of the item

            relations : dict

            dateAdded : str
                Date formatted like %Y-%m-%dT%H:%M:%SZ, like '2024-08-13T15:28:42Z'

            dateModified : str
                Date formatted like %Y-%m-%dT%H:%M:%SZ, like '2024-08-13T15:28:42Z'

    Methods
    -------
    get_item_id_by_file_path(file_path:str) -> str
        Return the item key string from the passed local path

    get_first_page_number(item_key:str) -> int
        Get the relative first page from the document, as it is labeled in the PDF.

    get_highlights_by_file(file_path:str)
        Given a zotero file name, extracts it highlights to the class lists.

    get_highlights_by_date() -> dict
        Same from above Method, but instead of inputting the file_name string, takes a date, and
        queryes all the files more recent than the given date.

    extract_highlights(file_path:str)
        Update the class highlights attribute, with the obtained highlights from the file path.

    get_zotero_tags_by_pdf_path(file_path:str) -> str
        Get a zotero local PDF attachment parent item tags.

    add_zotero_tag_by_pdf_path(file_path:str, added_tag:str)
        Add a tag to a zotero PDF file attachment parent item.

    remove_zotero_tag_by_pdf_path(file_path:str, removed_tag:str)
        Remove a tag from a zotero PDF file attachment parent item.

    Examples
    --------
    annotation_data example:
    [{'key': 'VENEZY2N', 'version': 8758, 'parentItem': 'I9M4ZAZ9', 'itemType': 'annotation',
      'annotationType': 'highlight', 'annotationText': 'photosystem (PS) II photoinhibition',
      'annotationComment': '', 'annotationColor': '#ff6666', 'annotationPageLabel': '1',
      'annotationSortIndex': '00000|001579|00359',
      'annotationPosition': '{"pageIndex":0,"rects":[[47.849,410.948,190.332,423.397]]}',
      'tags': [], 'relations': {}, 'dateAdded': '2024-08-13T15:28:42Z',
      'dateModified': '2024-08-13T15:28:42Z'},
     {'key': 'NJNN4SEF', 'version': 8757, 'parentItem': 'I9M4ZAZ9', 'itemType': 'annotation',
      'annotationType': 'highlight',
      'annotationText': 'and this accumulation was correlated with the extent of',
      'annotationComment': '', 'annotationColor': '#a28ae5', 'annotationPageLabel': '1',
      'annotationSortIndex': '00000|001537|00351',
      'annotationPosition': '{"pageIndex":0,"rects":[[306.815,422.555,549.921,431.441]]}',
      'tags': [], 'relations': {}, 'dateAdded': '2024-08-13T15:28:36Z',
      'dateModified': '2024-08-13T15:28:36Z'}
     ]

    """

    def __init__(
        self,
        zotero_api: Optional[zotero.Zotero] = None,
        library_id: Optional[str] = None,
        library_type: Optional[str] = None,
        api_key: Optional[str] = None,
        highlights: Sequence[ZoteroHighlight] = None,
        annotations_data: Optional[list] = None,
    ):
        self.zotero_api = zotero.Zotero(library_id, library_type, api_key)
        self.highlights = []
        self.annotation_data = []

    def get_item_id_by_file_path(self, file_path):
        """

        Get the Zotero item ID for an attachment given its local file path.

        Parameters
        ----------
        file_path : str
            Local PDF file path

        Returns
        -------
        str
            Given file path zotero item ID.

        """
        file_name = path.basename(file_path)
        items = self.zotero_api.items(q=file_name, itemtype="attachment")
        for item in items:
            if "file_name" in item["data"] and item["data"]["file_name"] == file_name:
                return item["data"]["parentItem"]
        storage_name = path.basename(path.dirname(file_path))
        if (
            re.match(r"^[A-Z0-9]+$", storage_name)
            and self.zotero_api.item(storage_name) is not None
        ):
            return storage_name
        return None

    def get_first_page_number(self, item_key):
        """

        Calculate the relative first page number of a given Zotero item.

        Parameters
        ----------
        file_path : str
            Zotero item file complete path

        Returns
        -------
        absolute_page_number : int
            Document absolute page number, starting in 1

        Notes
        -----
        Zotero attachment PDF page retrieved by pyzotero, is the page as it is numbered in the PDF,
        like if it is a book chapter from pages 750-760, it considers the first page has the number
        750, but since sioyek considers the page starts necessary in 0, its necessary to convert
        the page number in this cases.

        """
        item = self.zotero_api.item(item_key)
        first_page = item["data"].get("pages")
        if first_page is None:
            item = self.zotero_api.item(item["data"]["parentItem"])
            first_page = item["data"].get("pages")
        if first_page is not None and first_page.split("-")[0] is not None:
            return int(first_page.split("-")[0])
        return None

    def extract_highlights(self, item_key):
        """

        Given a zotero item key, extract it highlights.

        Parameters
        ----------
        item_key : str
            str of a zotero item key

        Notes
        -----
        This function extracts the higlights to the class lists highlights and annotation_data

        """
        first_page = self.get_first_page_number(item_key)
        annotations = self.zotero_api.children(item_key, itemType="annotation")
        for annotation in annotations:
            if annotation["data"]["annotationType"] == "highlight":
                text = annotation["data"].get("annotationText", "")
                color = annotation["data"].get("annotationColor", "")
                page = annotation["data"].get("annotationPageLabel", "")
                date_added = annotation["data"].get("dateAdded", "")
                date_modified = annotation["data"].get("dateModified", "")
                abs_doc_page = int(page) - (int(first_page) - 1)
                highlight = ZoteroHighlight(
                    text,
                    color,
                    page,
                    date_added,
                    date_modified,
                    abs_doc_page,
                )
                self.highlights.append(highlight)
# -TODO: Check if this function is still needed, after the code was refactored to use file path
#       In all the functions

    def get_highlights_by_file(self, file_path):
        """
        Given a zotero file name, extracts it highlights to the class lists.

        Parameters
        ----------
        file_path : str
            Zotero database complete local PDF file path

        Returns
        -------
        None

        """
        file_name = os.path.basename(file_path)
        items = self.zotero_api.items(q=file_name, itemtype="attachment")
        md5_hash = calculate_md5(file_path)
        for item in items:
            if "md5" in item["data"] and item["data"]["md5"] == md5_hash:
                self.extract_highlights(item["key"])
                break

    def get_highlights_by_date(self, date):
        """

        Given a date, return all zotero highlights made after that.

        Parameters
        ----------
        date : datetime.datetime
            Date to filter highlights to start at

        Returns
        -------
        None

        """
        date_str = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        items = self.zotero_api.everything(
            self.zotero_api.items(since=date_str, itemType="attachment")
        )
        for item in items:
            self.extract_highlights(item["key"])

    def get_zotero_tags_by_pdf_path(self, file_path):
        """

        Get a zotero local PDF attachment parent item tags.

        Parameters
        ----------
        pdf_path : str
            Local complete PDF file path.

        Returns
        -------
        tags_str : str
            Zotero item tags, separated by ','

        """
        file_name = os.path.basename(file_path)
        items = self.zotero_api.items(q=file_name)
        md5_hash = calculate_md5(file_path)
        tags_list = []
        for item in items:
            if "md5" in item["data"] and item["data"]["md5"] == md5_hash:
                parent_item = self.zotero_api.item(item["data"]["parentItem"])
                for n in parent_item["data"]["tags"]:
                    tags_list.append(n["tag"])
                return ", ".join(tags_list)

        return None

    def add_zotero_tag_by_pdf_path(self, file_path, added_tag):
        """

        Add a tag to a zotero PDF file attachment parent item.

        Parameters
        ----------
        file_path : str
            Complete local file path to PDF file attachment present in zotero.

        added_tag : str
            Tag name to add to the zotero item.

        Returns
        -------
        None

        """
        file_name = os.path.basename(file_path)
        items = self.zotero_api.items(q=file_name)
        md5_hash = calculate_md5(file_path)
        for item in items:
            if "md5" in item["data"] and item["data"]["md5"] == md5_hash:
                parent_item = self.zotero_api.item(item["data"]["parentItem"])
                if {"tag": added_tag} in parent_item["data"]["tags"]:
                    print(
                        f"Tag {RED}{added_tag}{RST} Already exists in PDF parent item!"
                    )
                else:
                    parent_item["data"]["tags"].append({"tag": added_tag})
                    self.zotero_api.update_item(parent_item)
                    print(f"Tag {CYAN}{added_tag}{RST} added to PDF parent item.")
            else:
                print(
                    f"{RED}Given PDF file md5 hash not found in Zotero attachments!{RST}"
                )

    def remove_zotero_tag_by_pdf_path(self, file_path, removed_tag):
        """

        Remove a tag from a zotero PDF file attachment parent item.

        Parameters
        ----------
        file_path : str
            Complete local file path to PDF file attachment present in zotero.

        removed_tag : str
            Tag name to remove from the zotero item.

        Returns
        -------
        None

        """
        file_name = os.path.basename(file_path)
        items = self.zotero_api.items(q=file_name)
        md5_hash = calculate_md5(file_path)
        for item in items:
            if "md5" in item["data"] and item["data"]["md5"] == md5_hash:
                parent_item = self.zotero_api.item(item["data"]["parentItem"])
                if {"tag": removed_tag} in parent_item["data"]["tags"]:
                    parent_item["data"]["tags"].remove({"tag": removed_tag})
                    self.zotero_api.update_item(parent_item)
                    print(f"Tag {CYAN}{removed_tag}{RST} removed from item.")
                else:
                    print(
                        f"Tag {RED}{removed_tag}{RST} not found in the given PDF parent item!"
                    )


class SioyekData:
    """
    Sioyek highligts class.

    Attributes
    ----------
    local_database_file_path : str
        Path to the local database .db file path

    shared_database_file_path : str
        Path to the shared database .db file path

    sioyek_path : str
        Path to the sioyek executable

    zotero_hl_to_sioyek : dict
        Dictionary wich keys are zotero highlight html colors, and the value is the sioyek
        highlight letter, to which this highlights should be when embedding in sioyek

    docs : list
        list of dicts, containing the documents in the sioyek database, having each dict the id
        of a file, the path to this file, and the hash to this file path, for example:

    sioyek : sioyek.sioyek.Sioyek
        Sioyek python class object, to execute sioyek commands

    Methods
    -------
    list_files()
        List all file paths and hashes in the sioyek database

    list_hash(file:str)
        Given a file, print this file hash

    get_hash(file:str) -> str
        Similar to list_hash, but return this file hash

    get_attributes(file:str) -> dict
        Return a dict with the highlights data fields.

    is_string_in_dicts(string:str, list_of_dicts:list) -> bool
        Checks in a list of dicts for any dict value matching a given string, returning a boolean.

    insert_documents(file_path:str)
        Insert if don't exist, a file into local sioyek database.

    print_attributes(file:str)
        Print all attributes from sioyek database file, and this attributes values.
        the attributes are bookmarks, highlights, links and marks.

    to_abs(highlights:ZoteroData.highlights, file_path:str) -> tuple
        Get the absolute position of a document highlight, based on the highlight text, the
        highlight page, and the document file path.

    convert_zot_date_to_sioyek(date_str:str) -> str
        Convert a date from zotero default format to sioyek format.

    get_zotero_to_sioyek_data(file_path:str,
                                     zotero_data:__main__.ZoteroData) -> list
        Get a zotero file highlights, formatted in a dict with essential data to embed to sioyek.

    insert_highlight(file_path:str, zotero_data:__main__.ZoteroData)
        Insert a zotero file annotations to this sioyek file database.

    Examples
    --------
    docs attribute example of list:
    [{'id': 1,
      'path': '/home/user/Zotero/storage/RZ54E2RK/processing_of_calcium_sulfate_the_.pdf',
      'hash': '04456fccdb9854ca3bea51d6442d9bb2',
     },
     {'id': 2,
      'path': '/home/user/Programação/LaTeX/tutorial/tut.pdf',
      'hash': '4e35e5dca3a3f648ba6594453347f498',
     },
     {'id': 3,
      'path': '/home/user/Library/python/numpydoc.pdf',
      'hash': '82f60ed6cc8e494a82d24d84105065b0',
     }
    ]
    """

    def __init__(
        self,
        local_database_file_path: Optional[str] = None,
        shared_database_file_path: Optional[str] = None,
        sioyek_path: Optional[str] = None,
        zotero_hl_to_sioyek: Optional[dict] = None,
        docs: Sequence[Document] = None,
        sioyek: Optional[Sioyek] = None,
    ):
        check_env_variables()
        self.local_database_file_path = SIOYEK_LOCAL_DATABASE_FILE_PATH
        self.shared_database_file_path = SIOYEK_SHARED_DATABASE_FILE_PATH
        self.sioyek_path = SIOYEK_PATH
        self.zotero_hl_to_sioyek = ZOTERO_TO_SIOYEK_COLORS
        local_db = sqlite3.connect(clean_path(self.local_database_file_path))
        local_cursor = local_db.cursor()
        local_cursor.execute("select * from document_hash")
        documents = local_cursor.fetchall()
        column_names = [description[0] for description in local_cursor.description]
        self.docs = [dict(zip(column_names, bm)) for bm in documents]
        self.sioyek = Sioyek(
            self.sioyek_path,
            self.local_database_file_path,
            self.shared_database_file_path,
        )
        local_db.close()

    def list_files(self):
        """List all file paths and hashes in the sioyek database."""
        for doc in self.docs:
            print(doc["hash"], ":", doc["path"])

    def list_hash(self, file):
        """

        Given a file, prints this file hash.

        Parameters
        ----------
        file : str

        Returns
        -------
        None

        """
        found = False
        for doc in self.docs:
            if pathlib.Path(doc["path"]).samefile(file):
                print(doc["hash"])
                found = True
                break
        if not found:
            print("File not found in the database.")

    def get_hash(self, file_path):
        """

        Similar to list_hash, but return this file hash.

        Parameters
        ----------
        file_path : str
            file complete path

        Returns
        -------
        result : str
            String of the file md5sum hash

        """
        found = False
        result = ""
        for doc in self.docs:
            if pathlib.Path(doc["path"]).samefile(file_path):
                result = doc["hash"]
                found = True
                break
        if not found:
            print("File not found in the database.")
        return result

    def get_attributes(self, file_path):
        """

        Return a dict with the highlights data fields.

        Parameters
        ----------
        file_path : str
            String of a file path.

        Returns
        -------
        from_annotation : dict
            dict with the keys:
                bookmarks : list
                highlights : list
                    list of dicts, with the keys:
                        id : int
                            number of the highlight index
                        document_path : str
                            hash str of the document path
                        desc : str
                            text of the highlight
                        text_annot : str
                            annotation of the highlight
                        type : str
                            letter of the sioyek highlight type
                        creation_time : str
                            date formatted like %Y-%m-%d %H:%M:%S
                        modification_time : str
                            date formatted like %Y-%m-%d %H:%M:%S
                        uuid : str
                            uuid of the highlight
                        begin_x : float
                            coordinate of the sioyek absolute position x begin
                        begin_y : float
                            coordinate of the sioyek absolute position y begin
                        end_x : float
                            coordinate of the sioyek absolute position x end
                        end_y : float
                            coordinate of the sioyek absolute position y end

        Examples
        --------
        An example of a returned from_annotations dict:
        {'bookmarks': [],
         'highlights': [{'id': 1,
                         'document_path': '04456fccdb9854ca3bea51d6442d9bb2',
                         'desc': 'thermodynamic databases.',
                         'text_annot': 'None',
                         'type': 'i', 'creation_time': '2024-08-13 15:53:45',
                         'modification_time': '2024-08-13 15:53:45',
                         'uuid': '0b573e66-66aa-4fc7-886b-2e21d94104af',
                         'begin_x': -198.7873992919922, 'begin_y': 1121.375,
                         'end_x': -156.77529907226562, 'end_y': 1155.4794921875}],
         'links': [],
         'marks': []}

        """
        table_names = [
            ("bookmarks", "document_path"),
            ("highlights", "document_path"),
            ("links", "src_document"),
            ("marks", "document_path"),
        ]
        from_annotations = {}
        from_hash = self.get_hash(file_path)
        for table, column_name in table_names:
            with sqlite3.connect(self.shared_database_file_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT * FROM {table} WHERE {column_name} = ?", (from_hash,)
                )
                annotations = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                from_annotations[table] = [
                    dict(zip(column_names, bm)) for bm in annotations
                ]
        return from_annotations

    def is_string_in_dicts(self, string, list_of_dicts):
        """

        Check if a given string matches any dict value from a list of dicts.

        Parameters
        ----------
        string : str
            String to search for matches in the dicts values

        list_of_dicts : list
            List, with each element being a dict, being this dicts the ones that will
            have the values checked for matchings with the given string.

        Returns
        -------
        bool
            Boolean, True if any value of the dicts mathces the string, and False if not.

        """
        for dictionary in list_of_dicts:
            if any(string in str(value) for value in dictionary.values()):
                return True
        return False

    def insert_document(self, file_path):
        """

        Check and insert a file if don't exist in local sioyek database.

        Parameters
        ----------
        file_path : str
            Complete file path

        """
        local_db = sqlite3.connect(clean_path(self.local_database_file_path))
        md5_hash = calculate_md5(file_path)
        doc_exists = self.is_string_in_dicts(md5_hash, self.docs)
        user_inp = None
        q_doc_insert = None
        if not doc_exists:
            q_doc_insert = f"""
            INSERT INTO document_hash(path, hash)
            VALUES ('{file_path}','{md5_hash}');
            """
            file_name = f"{path.basename(clean_path(file_path))}"
            user_inp = input(
                textwrap.dedent(
                    f"""\
                Insert {CYAN}{file_name}{RST} in {MGN}local Sioyek database{RST}? {BLUE}(y/n){RST}:
            """
                )
            )
        if user_inp in ["Y", "y", "yes"]:
            if q_doc_insert is not None:
                print(q_doc_insert)
            print(f"{file_name} {GREEN} Added to local database{RST}")
            local_db.execute(q_doc_insert)
            local_db.execute("commit")
        elif user_inp in ["N", "n", "no"]:
            print(f"{file_name} {RED}Addition abortted!{RST}")
        elif user_inp is not None:
            print(f"{RED}Answer should be y or n!{RST}")
        local_db.close()

    def print_attributes(self, file_path):
        """

        Print all attributes from sioyek database file, and this attributes values.

        the attributes are bookmarks, highlights, links and marks.

        Parameters
        ----------
        file_path : str
            String of a file path.

        Returns
        -------
        None

        """
        from_annotations = self.get_attributes(file_path)
        colors_list = [f"{CYAN}", f"{MGN}", f"{YELLOW}", f"{GREEN}"]
        for key, attribute in from_annotations.items():
            idx = list(from_annotations).index(key)
            print(f"{colors_list[idx]}{key}\n{'=' * len(key)}{RST}\n")
            for idx, value in enumerate(attribute):
                print(f"{idx + 1}\n--------")
                for i, j in value.items():
                    print(f"{i}: {j}")
            print("\n")

    def to_abs(self, zotero_data, highlight, file_path):
        """

        Get the absolute position of a document highlight, based on the text, page and file path.

        Parameters
        ----------
        zotero_data : __main__.ZoteroData
            Main zotero highlights class

        highlight : ZoteroData.highlight
            Zotero highlights class object

        file_path : str
            String of a file path

        """
        doc = self.sioyek.get_document(file_path)
        begin, end = doc.get_text_selection_begin_and_end(
            (highlight.abs_doc_page) - 1, highlight.text
        )
        if begin == (None, None) or end == (None, None):
            raise ValueError("highlight text not found")
        offset_x = (doc.page_widths[highlight.abs_doc_page - 1]) / 2
        begin_pos = DocumentPos(
            highlight.abs_doc_page - 1, begin[0] - offset_x, begin[1]
        )
        end_pos = DocumentPos(highlight.abs_doc_page - 1, end[0] - offset_x, end[1])
        return (doc.to_absolute(begin_pos), doc.to_absolute(end_pos))

    def convert_zot_date_to_sioyek(self, date_str):
        """

        Convert a date from zotero default format to sioyek format.

        Parameters
        ----------
        date_str : str
            Date string in zotero default format, '%Y-%m-%dT%H:%M:%SZ'

        Returns
        -------
        formatted_date_str : str
            Date string in sioyek default format, '%Y-%m-%d %H:%M:%S'

        Examples
        --------
        >>> time_test = convert_zot_date_to_sioyek("2024-08-13T15:53:45Z")
        >>> print(time_test)
        2024-08-13 15:53:45

        """
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_date_str

    def get_zotero_to_sioyek_data(self, file_path, zotero_data):
        """

        Get a zotero file highlights, formatted in a dict with essential data to embed to sioyek.

        Parameters
        ----------
        file_path : str
            Complete file path

        zotero_data : __main__.ZoteroData
            Main zotero highlights class

        Returns
        -------
        zotero_annotations : list
            list containing highlight dicts, being one dict per highlight

        Examples
        --------
        zotero_annotations example list of dict:
        [{'document_path': '04456fccdb9854ca3bea51d6442d9bb2',
          'desc': 'thermodynamic databases.,
          'type': 'i', 'begin_x': '-198.7873992919922',
          'begin_y': '1121.375', 'end_x': '-156.77529907226562', 'end_y': '1155.4794921875',
          'text_annot': 'None', 'creation_time': '2024-08-13 15:53:45',
          'modification_time': '2024-08-13 15:53:45',
          'uuid': 'cc3366af-b523-4a67-a802-c7afd846d942',
          'page': 335
          'absolute_page': 1
         },
         {'document_path': '04456fccdb9854ca3bea51d6442d9bb2',
          'desc': 'reported by many authors and used in practice for several decades,',
          'type': 'd', 'begin_x': '-165.0081024169922', 'begin_y': '997.185546875',
          'end_x': '-152.75357055664062', 'end_y': '1031.2900390625',
          'text_annot': 'None', 'creation_time': '2024-08-13 15:53:42',
          'modification_time': '2024-08-13 15:53:42',
          'uuid': '58d238b6-1b42-4b52-97aa-4773b9b6c734',
          'page': 335
          'absolute_page': 1
          }]
        """
        zotero_data.get_highlights_by_file(file_path)
        highlights = zotero_data.highlights
        zotero_annotations = []
        for highlight in highlights:
            abs_pos = self.to_abs(zotero_data, highlight, file_path)
            zotero_annotations.append({
                "document_path": calculate_md5(file_path),
                "desc": highlight.text,
                "type": self.zotero_hl_to_sioyek[highlight.color],
                "begin_x": str(abs_pos[0].offset_x),
                "begin_y": str(abs_pos[0].offset_y),
                "end_x": str(abs_pos[1].offset_x),
                "end_y": str(abs_pos[1].offset_y),
                "text_annot": "none",
                "creation_time": self.convert_zot_date_to_sioyek(highlight.date_added),
                "modification_time": self.convert_zot_date_to_sioyek(
                    highlight.date_modified
                ),
                "uuid": str(uuid.uuid4()),
                "page": highlight.page,
                "absolute_page": highlight.abs_doc_page,
            })
        return zotero_annotations

    def list_all_sioyek_highlights(self):
        """

        Get all sioyek database documents highlights, and list them.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        shared_db = sqlite3.connect(clean_path(self.shared_database_file_path))
        cursor = shared_db.cursor()
        cursor.execute("select * from highlights")
        documents = cursor.fetchall()
        for n in documents:
            print(
                textwrap.dedent(
                    f"""\
            {n[0]}
            -----
            ID: {n[0]}
            Document Path md5: {n[1]}
            Text: {n[2]}
            Annotation: {n[3]}
            Type: {n[4]}
            Creation: {n[5]}
            Modification: {n[6]}
            Highligh UUID: {n[7]}
            Begin X: {n[8]}
            Begin Y: {n[9]}
            End X: {n[10]}
            End Y: {n[11]}
            """
                )
            )

    def insert_highlight(self, file_path, zotero_data):
        """

        Insert a zotero file annotations to this sioyek file database.

        Inser a zotero file highlights into a sioyek file, through sqlite3.
        The colors association is based on the color dict of the start of this file, and the
        function checks for repeated annotations through both databases, to not insert repeated
        highlights. Repeated highlights is checked through the highligh similarity, if above
        90%.
        When a highlight is inserted in the sioyek file, it also prints the execed sqlite3 command.

        Parameters
        ----------
        file_path : str
            Complete file path present in zotero and sioyek database

        zotero_data : __main__.ZoteroData
            ZoteroData class

        Notes
        -----
        The only field not present in the inserted highlight is the highlight id number, this way
        it permits to add highlights to files that already contain sioyek highlights, and the id
        number is automatically generated by sioyek.

        """
        self.insert_document(file_path)
        tables = self.get_zotero_to_sioyek_data(file_path, zotero_data)
        from_annotations = self.get_attributes(file_path)
        shared_db = sqlite3.connect(clean_path(self.shared_database_file_path))
        tables_to_keep = [
            table
            for table in tables
            if not any(
                SequenceMatcher(None, table["desc"], annotation["desc"]).ratio() >= 0.98
                for annotation in from_annotations["highlights"]
            )
        ]

        for table in tables_to_keep:
            q_hi_insert = """
            INSERT INTO highlights (document_path,desc,type,begin_x,begin_y,
                                    end_x,end_y,text_annot,creation_time,modification_time,uuid)
            VALUES ('{}','{}','{}',{},{},{},{},'{}','{}','{}','{}');
            """.format(
                table["document_path"],
                table["desc"],
                table["type"],
                table["begin_x"],
                table["begin_y"],
                table["end_x"],
                table["end_y"],
                table["text_annot"],
                table["creation_time"],
                table["modification_time"],
                table["uuid"],
            )
            print(q_hi_insert)
            shared_db.execute(q_hi_insert)
            shared_db.execute("commit")
        shared_db.close()
        self.sioyek.close()


def check_file_name_in_lib(path_or_file_name: str) -> str:
    """

    Use in argparse type to check a file name or path, and return the complete path.

    Parameters
    ----------
    path_or_file_name : str
        file name or file complete path

    Returns
    -------
    path : str
        file complete path

    """
    directory = ZOTERO_LOCAL_DIR
    if path_or_file_name.startswith('"') and path_or_file_name.endswith('"'):
        path_or_file_name = f"{path_or_file_name[1:-1]}"
    try:
        exists = path.exists(path_or_file_name)
        if exists:
            return path_or_file_name

        for root, _, files in walk(directory):
            if path_or_file_name in files:
                return path.join(root, path_or_file_name)
        raise ValueError
    except ValueError:
        print(f"{RED}be a file name or file path!{RST}")
        return ""


def hex_to_rgb(hex_color):
    """

    Convert a html hex to rgb.

    Parameters
    ----------
    hex_color : str
        Html hex color code

    Returns
    -------
    rgb : tuple
        r,g,b tuple, rangin each color from 0 to 255

    Examples
    --------
    >>> rgb = hex_to_rgb("#ff6666")
    >>> print(rgb)
    (255, 102, 102)

    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def print_colored_string(string, hex_color, auto_print=True):
    """

    Print to terminal a string colored with a html hex code color.

    Parameters
    ----------
    string : str
        string to be printted

    hex_color : str
        html hex code color

    auto_print : bool
        Whether to print the colored string, or to return the string ansi escaped.

    Returns
    -------
    str
        Ansi escaped string, with the correct color, returned only if auto_print=False.

    """
    rgb = hex_to_rgb(hex_color)
    ansi_escape = f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
    reset_escape = "\033[0m"
    if auto_print:
        print(f"{ansi_escape}{string}{reset_escape}")
        return None
    return f"{ansi_escape}{string}{reset_escape}"


def check_env_variables():
    """

    Check this script global variables.

    Check this script global variables, defining the variable if it is present in environment
    variables and not defined in the script (This script initial global variables has higher
    preference, except for ZOTERO_TO_SIOYEK_COLORS). Print a warning message and exit if
    a needed variable is not defined neither in the script or environment variables.

    Parameters
    ----------
    None

    """
    exit_bool = False
    if os.getenv("ZOTERO_TO_SIOYEK_COLORS") is not None:
        globals()["ZOTERO_TO_SIOYEK_COLORS"] = ast.literal_eval(
            os.getenv("ZOTERO_TO_SIOYEK_COLORS"),
        )
    for k, v in {
        "ZOTERO_LIBRARY_ID": ZOTERO_LIBRARY_ID,
        "ZOTERO_LOCAL_DIR": ZOTERO_LOCAL_DIR,
        "ZOTERO_API_KEY": ZOTERO_API_KEY,
        "SIOYEK_LOCAL_DATABASE_FILE_PATH": SIOYEK_LOCAL_DATABASE_FILE_PATH,
        "SIOYEK_SHARED_DATABASE_FILE_PATH": SIOYEK_SHARED_DATABASE_FILE_PATH,
        "SIOYEK_PATH": SIOYEK_PATH,
    }.items():
        if v == "":
            value = os.getenv(k)
            if value is not None:
                globals()[k] = value
            else:
                print(f"{RED} {k}{RST} script variable needs to be defined")
                exit_bool = True

    if exit_bool:
        sys.exit()


def validate_arg(arg, type_str):
    """

    Validate a given argparse argument, based on the passed type.

    Parameters
    ----------
    arg : argparse.Namespace
        Argparse argument value.

    type_str : str
        String with the type that should be checked the arg, with the options:
            "float", "str", "tag", "int", "filename_in_lib"

    Returns
    -------
    bool

    Examples
    --------
    >>> print(validate_arg("24.4", "float"))
    True

    """
    if arg is None:
        return False

    if type_str in ("str", "tag"):
        try:
            isinstance(arg, str)
            return True
        except ValueError:
            print("\nValue must be a string!\n")
            return False

    elif type_str == "filename_in_lib":
        return check_file_name_in_lib(arg)

    else:
        return True


def check_args_number(argnsp, argument_name, type_list, parser, zotero_data=None):
    """

    Cheks argparse passed number of arguments.

    Checks numbers of arguments passed to an specific argparse flag, and
     if this number is lower than the length of the argument metravar,
     a prompt is activated to the user to input the missing arguments.
    Also checks if arguments type are correct, as well as argument
    range. If any of the checkings fail, the user is inputted to
    reinsert the argument.

    Parameters
    ----------
    argnsp : list
        argparse argument

    argument_name : str
        str of the name from the argparse argument.
        args.argument_name=argnsp

    type_list : list
        list of strings, containing the argument values types, to be passed
        to the validate_arg function

    Returns
    -------
    none

    """
    if argnsp is None:
        argnsp = []
    currentlen = len(argnsp)
    for action in parser._actions:
        if argument_name in action.option_strings:
            lenargs = len(action.metavar)
            if currentlen != lenargs:
                while currentlen < lenargs:
                    input_text = "Insert Argument: "
                    curr_options = " ".join(reversed(action.option_strings))
                    curr_metas = " ".join(action.metavar)
                    print(
                        f"\n{curr_options} [{curr_metas}]\n"
                    )
                    input_text = f"{action.metavar[currentlen]}: "
                    if type_list[currentlen] == "tag" and zotero_data is not None:
                        tags_str = zotero_data.get_zotero_tags_by_pdf_path(
                            argnsp[currentlen - 1]
                        )
                        print(f"{CYAN}Tags\n----{RST}\n{tags_str}\n")
                        input_text = "Tag: "
                    new_arg = input(input_text)
                    check_validate = validate_arg(new_arg, type_list[currentlen])
                    if isinstance(check_validate, str):
                        argnsp.append(check_validate)
                    else:
                        argnsp.append(new_arg)
                    currentlen = len(argnsp)
                    print("\n")
            else:
                for n in range(0, lenargs - 1):
                    exc_validate = validate_arg(argnsp[n], type_list[n])
                    while not exc_validate:
                        new_arg = input("Insert Argument: ")
                        argnsp[n] = new_arg


def print_gen_help(parser):
    """

    Print this script sclient help message.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        argparse parser class object.

    Returns
    -------
    None

    """
    group_colors = [f"{GREEN}", f"{RED}", f"{CYAN}"]
    line_list = []
    group_desc_list = []
    line_str_group = []
    headers_sep = " " * (30)
    for group in parser._action_groups:
        if group.title and group.description is not None:
            for action in group._group_actions:
                tmp_list = []
                flag = ", ".join(reversed(action.option_strings))
                if action.metavar is not None:
                    for n in action.metavar:
                        tmp_list.append(f"[{n}]")
                    metas = ", ".join(tmp_list)
                else:
                    metas = ""
                hnew = " " * (35 - len(flag))
                line_list.append(f"{BLUE}{flag}{RST}{hnew}{YELLOW}{metas}{RST}\n{action.help}")
            group_desc_list.append(f"{group.description}\n")
            line_str_group.append("\n".join(line_list))
            line_list = []

    print(
        f"\n{parser.prog}\n\n{parser.description}\n\n"
        f"{BLUE}FLAGS{RST}{headers_sep}{YELLOW}ARGUMENTS{RST}\n"
        f"{BLUE}====={RST}{headers_sep}{YELLOW}=========={RST}\n"
    )
    for idx, value in enumerate(line_str_group):
        print(f"\n{group_colors[idx]}{group_desc_list[idx]}{'-' * len(group_desc_list[idx])}\n{RST}")
        print(f"{value}")
    print(f"\n{parser.epilog}")


def print_group_help(parser, group_title):
    """

    Print to terminal the help function from one of the available argparse groups.
    The group is passed as flag, and can be: sioyek; zotero; general.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        argparse parser class object.

    group_title : str
        Name of the group to print the help

    """
    for group in parser._action_groups:
        if group.title == group_title and group.description is not None:
            print(f"\n{group.description}\n")
            for action in group._group_actions:
                action_join = " ".join(action.option_strings)
                meta_join = " ".join(action.metavar) if action.metavar is not None else ""
                print(f"{MGN}{action_join}{RST}  {YELLOW}{meta_join}{RST}\n{action.help}\n")


def cli_args_general_utils(args, parser):
    """

    Handler of the -h/--help flags, to check if any argument was passed, in the case of specific
    argparse groups help printing.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        argparse parser class object.

    group_title : str
        Name of the group to print the help

    """
    if args.help is None:
        args.help = []
    if len(args.help) == 0 :
        if "-h" in sys.argv:
            parser.print_help()
        else:
            print_gen_help(parser)
        return

    for n in args.help:
        n = str(n)
        if n and n[0].islower():
            n = n[0].upper() + n[1:]
        print_group_help(parser, n)


def main():
    check_env_variables()

    zotero_data = ZoteroData(
        library_id=ZOTERO_LIBRARY_ID,
        library_type=ZOTERO_LIBRARY_TYPE,
        api_key=ZOTERO_API_KEY,
    )

    sioyek_data = SioyekData()

    parser = argparse.ArgumentParser(
        prog="python zot2sioyek.py [FLAG] [ARGUMENTS]",
        description=textwrap.dedent(
            """\
            Zotero highlights to sioyek manager.
            If any necessary argument is not given, the user will be prompted to input it.\
        """
        ),
        epilog=textwrap.dedent(
            """\
            If an argument passed after a flag contain blank spaces, remember to quote wrap it,
            while not being necessary case inputted after through prompted option.

            Author: eduardotcampos@usp.br\
        """
        ),
        allow_abbrev=True,
        add_help=False,
    )

    group_general = parser.add_argument_group(
        "General",
        description="Script general utils.",
    )

    group_zotero = parser.add_argument_group(
        "Zotero",
        description="Zotero Managing Commands.",
    )

    group_sioyek = parser.add_argument_group(
        "Sioyek",
        description="Sioyek Main Commands.",
    )

    group_general.add_argument(
        "--help",
        "-h",
        help=textwrap.dedent(
            """\
             Print this script help.
             If a Group name is passed after --help, the help to this specific group is printted
             only. Available groups are: general, zotero, sioyek.\
         """
        ),
        nargs="*",
    )

    group_zotero.add_argument(
        "--get-highlights",
        "-g",
        type=check_file_name_in_lib,
        nargs="*",
        action="store",
        help="Print all highlights from a given zotero file.",
        metavar=("file_name_or_path",),
    )
    group_zotero.add_argument(
        "--print-annotation-text",
        "-p",
        type=check_file_name_in_lib,
        nargs="*",
        action="store",
        help="print all highlighted text for a given zotero PDF local file.",
        metavar=("file_name_or_path",),
    )

    group_zotero.add_argument(
        "--zotero-tags",
        "-T",
        nargs="*",
        metavar=("file_name_or_path",),
        action="store",
        help="Prints a zotero PDF attachment parent item existing arguments.",
    )

    group_zotero.add_argument(
        "--add-zotero-tag",
        "-A",
        nargs="*",
        metavar=(
            "file_name_or_path",
            "tag_str_to_add",
        ),
        action="store",
        help=textwrap.dedent(
            """\
             Add a tag to a zotero PDF attachment parent item. Takes arguments file name or
             path, and tag str to add.\
         """
        ),
    )

    group_zotero.add_argument(
        "--remove-zotero-tag",
        "-R",
        nargs="*",
        metavar=(
            "file_name_or_path",
            "tag_str_to_remove",
        ),
        action="store",
        help=textwrap.dedent(
            """\
             Remove a tag from a zotero PDF attachment parent item. Takes arguments file name or
             path, and tag str to remove.\
         """
        ),
    )

    group_sioyek.add_argument(
        "--list-sioyek-files",
        "-f",
        action="store_true",
        help="Print all files in sioyek local database",
    )

    group_sioyek.add_argument(
        "--list-sioyek-hash",
        "-H",
        type=check_file_name_in_lib,
        nargs="*",
        action="store",
        help="print a sioyek database pdf file md5sum hash.",
        metavar=("file_name_or_path",),
    )

    group_sioyek.add_argument(
        "--print-sioyek-attributes",
        "-l",
        type=check_file_name_in_lib,
        nargs="*",
        metavar=("file_name_or_path",),
        action="store",
        help="Print all Attributes and values in a sioyek database PDF file.",
    )

    group_sioyek.add_argument(
        "--insert-highlight",
        "-i",
        nargs="*",
        metavar=("file_name_or_path",),
        action="store",
        help=textwrap.dedent(
            """\
             Insert highlights in a sioyek database PDF file, importing this highlights from this
             PDF file zotero attachment highlight.\
         """
        ),
        type=check_file_name_in_lib,
    )

    group_sioyek.add_argument(
        "--list-all-sioyek-highlights",
        "-S",
        action="store_true",
        help="Print all sioyek highlights",
    )

    args = parser.parse_args()

    if len(sys.argv) <= 1:
        cli_args_general_utils(args, parser)

    if args.help is not None:
        cli_args_general_utils(args, parser)

    if args.get_highlights is not None:
        check_args_number(
            args.get_highlights,
            "--get-highlights",
            ["filename_in_lib"],
            parser,
        )
        file_path = args.get_highlights[0]
        zotero_data.get_highlights_by_file(file_path)
        highlights = zotero_data.highlights
        n = 1
        print("\n")
        for highlight in highlights:
            mod_date = sioyek_data.convert_zot_date_to_sioyek(highlight.date_modified)
            create_date = sioyek_data.convert_zot_date_to_sioyek(highlight.date_added)
            colored_color = print_colored_string(
                highlight.color, highlight.color, auto_print=False
            )
            print(
                textwrap.dedent(
                    f"""\
                {n}
                -----
                Text: {highlight.text}
                Color: {colored_color}
                Relative Page: {highlight.page}
                Doc Page: {highlight.abs_doc_page}
                Creation Date: {create_date}
                Modification Date: {mod_date}
                """
                )
            )
            n += 1

    if args.print_annotation_text is not None:
        check_args_number(
            args.print_annotation_text,
            "--print-annotation-text",
            ["filename_in_lib"],
            parser,
        )

        file_path = args.print_annotation_text[0]
        zotero_data.get_highlights_by_file(file_path)
        for n in zotero_data.highlights:
            print_colored_string(n.text, n.color)

    if args.list_sioyek_files:
        sioyek_data.list_files()

    if args.list_sioyek_hash is not None:
        check_args_number(
            args.list_sioyek_hash,
            "--list-sioyek-hash",
            ["filename_in_lib"],
            parser,
        )
        file_path = args.list_sioyek_hash[0]
        sioyek_data.list_hash(file_path)

    if args.print_sioyek_attributes is not None:
        check_args_number(
            args.print_sioyek_attributes,
            "--print-sioyek-attributes",
            ["filename_in_lib"],
            parser,
        )
        file_path = args.print_sioyek_attributes[0]
        sioyek_data.print_attributes(file_path)

    if args.insert_highlight is not None:
        check_args_number(
            args.insert_highlight,
            "--insert-highlight",
            ["filename_in_lib"],
            parser,
        )
        file_path = args.insert_highlight[0]
        sioyek_data.insert_highlight(file_path, zotero_data)

    if args.list_all_sioyek_highlights:
        sioyek_data.list_all_sioyek_highlights()

    if args.zotero_tags is not None:
        check_args_number(
            args.zotero_tags,
            "--zotero-tags",
            ["filename_in_lib"],
            parser,
        )
        file_path = args.zotero_tags[0]
        tags_str = zotero_data.get_zotero_tags_by_pdf_path(file_path)
        print(tags_str)

    if args.add_zotero_tag is not None:
        check_args_number(
            args.add_zotero_tag,
            "--add-zotero-tag",
            ["filename_in_lib", "tag"],
            parser,
            zotero_data,
        )
        file_path = args.add_zotero_tag[0]
        added_tag = args.add_zotero_tag[1]
        zotero_data.add_zotero_tag_by_pdf_path(file_path, added_tag)

    if args.remove_zotero_tag is not None:
        check_args_number(
            args.remove_zotero_tag,
            "--remove-zotero-tag",
            ["filename_in_lib", "tag"],
            parser,
            zotero_data,
        )
        file_path = args.remove_zotero_tag[0]
        removed_tag = args.remove_zotero_tag[1]
        zotero_data.remove_zotero_tag_by_pdf_path(file_path, removed_tag)


if __name__ == "__main__":
    main()
