"""
PHOTO.XML生成サービス

デジタル写真管理情報基準（PHOTO05.DTD）準拠のXML生成
"""

from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from datetime import datetime


class PhotoXMLGenerator:
    """PHOTO.XML生成クラス"""

    def __init__(self):
        """初期化"""
        self.dtd_version = "05"
        self.photo_folder = "PHOTO/PIC"
        self.standard = "土木202303-01"

    def generate_xml(self, photos: List[Dict], pretty_print: bool = False) -> str:
        """
        PHOTO.XMLを生成

        Args:
            photos: 写真データのリスト
            pretty_print: 整形出力するかどうか

        Returns:
            生成されたXML文字列
        """
        # XML宣言とDOCTYPE
        xml_declaration = '<?xml version="1.0" encoding="Shift_JIS"?>\n'
        doctype = '<!DOCTYPE photodata SYSTEM "PHOTO05.DTD">\n'

        # ルート要素
        root = ET.Element("photodata", attrib={"DTD_version": self.dtd_version})

        # 基礎情報
        basic_info = ET.SubElement(root, "基礎情報")
        folder_name = ET.SubElement(basic_info, "写真フォルダ名")
        folder_name.text = self.photo_folder
        standard_elem = ET.SubElement(basic_info, "適用要領基準")
        standard_elem.text = self.standard

        # 写真情報（各写真ごと）
        for idx, photo in enumerate(photos, start=1):
            self._add_photo_info(root, photo, idx)

        # XML文字列生成
        if pretty_print:
            xml_str = self._prettify_xml(root)
        else:
            xml_str = ET.tostring(root, encoding="unicode")

        return xml_declaration + doctype + xml_str

    def _add_photo_info(self, root: ET.Element, photo: Dict, serial: int):
        """
        写真情報セクションを追加

        Args:
            root: ルート要素
            photo: 写真データ
            serial: シリアル番号
        """
        photo_info = ET.SubElement(root, "写真情報")

        # 写真ファイル情報
        file_info = ET.SubElement(photo_info, "写真ファイル情報")
        serial_elem = ET.SubElement(file_info, "シリアル番号")
        serial_elem.text = self.format_serial_number(serial)
        filename_elem = ET.SubElement(file_info, "写真ファイル名")
        filename_elem.text = self.escape_xml_special_chars(photo.get("file_name", ""))

        # 撮影工種区分（work_typeがある場合）
        work_type = photo.get("work_type")
        if work_type:
            work_category = ET.SubElement(photo_info, "撮影工種区分")
            work_type_elem = ET.SubElement(work_category, "工種")
            work_type_elem.text = self.escape_xml_special_chars(work_type)

            work_kind = photo.get("work_kind")
            if work_kind:
                work_kind_elem = ET.SubElement(work_category, "種別")
                work_kind_elem.text = self.escape_xml_special_chars(work_kind)

            work_detail = photo.get("work_detail")
            if work_detail:
                work_detail_elem = ET.SubElement(work_category, "細別")
                work_detail_elem.text = self.escape_xml_special_chars(work_detail)

        # 撮影情報
        shooting_info = ET.SubElement(photo_info, "撮影情報")

        # タイトル
        title_elem = ET.SubElement(shooting_info, "写真タイトル")
        title_elem.text = self.escape_xml_special_chars(photo.get("title", ""))

        # 撮影年月日
        shooting_date = photo.get("shooting_date")
        if shooting_date:
            date_elem = ET.SubElement(shooting_info, "撮影年月日")
            date_elem.text = self.format_date_ccyymmdd(shooting_date)

        # 写真区分
        photo_type = photo.get("photo_type")
        if photo_type:
            type_elem = ET.SubElement(shooting_info, "写真区分")
            type_elem.text = self.escape_xml_special_chars(photo_type)

        # OCRメタデータがある場合
        photo_metadata = photo.get("photo_metadata", {})
        ocr_result = photo_metadata.get("ocr_result", {})

        if ocr_result:
            # 測点
            station = ocr_result.get("station")
            if station:
                station_elem = ET.SubElement(shooting_info, "測点")
                station_elem.text = self.escape_xml_special_chars(station)

            # 設計寸法
            design_dim = ocr_result.get("design_dimension")
            if design_dim is not None:
                design_elem = ET.SubElement(shooting_info, "設計寸法")
                design_elem.text = str(design_dim)

            # 実測寸法
            actual_dim = ocr_result.get("actual_dimension")
            if actual_dim is not None:
                actual_elem = ET.SubElement(shooting_info, "実測寸法")
                actual_elem.text = str(actual_dim)

            # 検査員
            inspector = ocr_result.get("inspector")
            if inspector:
                inspector_elem = ET.SubElement(shooting_info, "検査員")
                inspector_elem.text = self.escape_xml_special_chars(inspector)

    def _prettify_xml(self, elem: ET.Element) -> str:
        """
        XMLを整形

        Args:
            elem: XML要素

        Returns:
            整形されたXML文字列
        """
        rough_string = ET.tostring(elem, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        # XML宣言を除外して整形（後で手動で追加するため）
        pretty_str = reparsed.toprettyxml(indent="  ", encoding=None)
        # XML宣言行を削除
        lines = pretty_str.split("\n")
        return "\n".join(line for line in lines if not line.strip().startswith("<?xml"))

    def validate_photo_data(self, photo: Dict) -> List[str]:
        """
        写真データをバリデーション

        Args:
            photo: 写真データ

        Returns:
            エラーメッセージのリスト
        """
        errors = []

        # 必須項目チェック
        required_fields = [
            "id",
            "file_name",
            "title",
            "shooting_date",
            "major_category",
        ]
        for field in required_fields:
            if not photo.get(field):
                errors.append(f"必須項目 '{field}' が不足しています")

        # ファイル名形式チェック
        file_name = photo.get("file_name", "")
        if file_name and not self.validate_filename(file_name):
            errors.append(f"ファイル名形式が不正です: {file_name}")

        # タイトル長さチェック
        title = photo.get("title", "")
        if title and not self.validate_title(title):
            errors.append(f"タイトルが127文字を超えています: {len(title)}文字")

        return errors

    def format_serial_number(self, num: int) -> str:
        """
        シリアル番号をフォーマット（7桁）

        Args:
            num: 番号

        Returns:
            フォーマットされた番号
        """
        return str(num).zfill(7)

    def format_date_ccyymmdd(self, date_str: str) -> str:
        """
        日付をCCYY-MM-DD形式にフォーマット

        Args:
            date_str: 日付文字列

        Returns:
            フォーマットされた日付
        """
        # すでにCCYY-MM-DD形式の場合
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return date_str

        # CCYYMMDD形式の場合
        if re.match(r"^\d{8}$", date_str):
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

        # CCYY/MM/DD形式の場合
        if re.match(r"^\d{4}/\d{2}/\d{2}$", date_str):
            return date_str.replace("/", "-")

        # その他の形式は変換試行
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return date_str

    def validate_filename(self, filename: str) -> bool:
        """
        ファイル名形式をバリデーション（Pnnnnnnn.JPG）

        Args:
            filename: ファイル名

        Returns:
            バリデーション結果
        """
        pattern = r"^P\d{7}\.JPG$"
        return bool(re.match(pattern, filename))

    def validate_title(self, title: str) -> bool:
        """
        タイトル長さをバリデーション（127文字以内）

        Args:
            title: タイトル

        Returns:
            バリデーション結果
        """
        return len(title) <= 127

    def check_work_category_required(self, photo_type: str) -> bool:
        """
        工種区分記入可否をチェック

        Args:
            photo_type: 写真区分

        Returns:
            記入必須かどうか
        """
        # 着手前及び完成写真：工種記入不要
        if photo_type == "着手前及び完成写真":
            return False

        # 品質管理写真：工種記入必須
        if photo_type == "品質管理写真":
            return True

        # 施工状況写真：工種記入可能（optional）
        if photo_type == "施工状況写真":
            return "optional"

        return False

    def escape_xml_special_chars(self, text: str) -> str:
        """
        XML特殊文字をエスケープ

        Args:
            text: テキスト

        Returns:
            エスケープされたテキスト
        """
        if not text:
            return ""

        # XML特殊文字を置換
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&apos;")

        return text
