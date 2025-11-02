"""
エクスポートサービス

電子納品フォルダ構造の自動生成とファイル名リネーム機能
"""

import os
import shutil
import zipfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime


class ExportService:
    """エクスポートサービスクラス"""

    def __init__(self):
        """初期化"""
        self.photo_folder = "PIC"
        self.drawing_folder = "DRA"
        self.root_folder = "PHOTO"

    def generate_serial_number(self, number: int, prefix: str = "P") -> str:
        """
        シリアル番号を生成（Pnnnnnnn形式）

        Args:
            number: 番号
            prefix: プレフィックス（P=写真、D=参考図）

        Returns:
            シリアル番号
        """
        return f"{prefix}{str(number).zfill(7)}"

    def rename_photo_file(self, photo: Dict, serial_number: int) -> Dict:
        """
        写真ファイル名をリネーム

        Args:
            photo: 写真データ
            serial_number: シリアル番号

        Returns:
            リネーム情報
        """
        new_file_name = f"{self.generate_serial_number(serial_number)}.JPG"

        return {
            "photo_id": photo.get("id"),
            "original_file_name": photo.get("file_name"),
            "new_file_name": new_file_name,
            "serial_number": serial_number,
        }

    def rename_multiple_photos(self, photos: List[Dict]) -> List[Dict]:
        """
        複数写真のファイル名をリネーム

        Args:
            photos: 写真データリスト

        Returns:
            リネーム情報リスト
        """
        renamed_list = []
        for idx, photo in enumerate(photos, start=1):
            renamed = self.rename_photo_file(photo, idx)
            renamed_list.append(renamed)
        return renamed_list

    def check_filename_duplication(self, photos: List[Dict]) -> List[str]:
        """
        ファイル名重複をチェック

        Args:
            photos: 写真データリスト

        Returns:
            重複ファイル名リスト
        """
        file_names = [photo.get("file_name") for photo in photos]
        seen = set()
        duplicates = []

        for file_name in file_names:
            if file_name in seen:
                if file_name not in duplicates:
                    duplicates.append(file_name)
            else:
                seen.add(file_name)

        return duplicates

    def create_folder_structure(self, export_dir: str) -> Dict[str, str]:
        """
        電子納品フォルダ構造を作成

        Args:
            export_dir: エクスポート先ディレクトリ

        Returns:
            作成されたフォルダパス
        """
        root_path = os.path.join(export_dir, self.root_folder)
        pic_path = os.path.join(root_path, self.photo_folder)
        dra_path = os.path.join(root_path, self.drawing_folder)

        # フォルダ作成
        os.makedirs(root_path, exist_ok=True)
        os.makedirs(pic_path, exist_ok=True)
        os.makedirs(dra_path, exist_ok=True)

        return {
            "root": root_path,
            "pic": pic_path,
            "dra": dra_path,
        }

    def validate_folder_structure(self, root_path: str) -> Tuple[bool, List[str]]:
        """
        フォルダ構造をバリデーション

        Args:
            root_path: ルートフォルダパス

        Returns:
            (バリデーション結果, エラーリスト)
        """
        errors = []

        # 必須フォルダ存在チェック
        if not os.path.exists(root_path):
            errors.append(f"ルートフォルダが存在しません: {root_path}")

        pic_path = os.path.join(root_path, self.photo_folder)
        if not os.path.exists(pic_path):
            errors.append(f"写真フォルダが存在しません: {pic_path}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_dtd_template_path(self) -> str:
        """
        DTDテンプレートのパスを取得

        Returns:
            DTDテンプレートパス
        """
        # バックエンドルートディレクトリからの相対パス
        backend_root = Path(__file__).parent.parent.parent
        return str(backend_root / "templates" / "PHOTO05.DTD")

    def get_xsl_template_path(self) -> str:
        """
        XSLテンプレートのパスを取得

        Returns:
            XSLテンプレートパス
        """
        backend_root = Path(__file__).parent.parent.parent
        return str(backend_root / "templates" / "PHOTO05.XSL")

    def copy_templates_to_folder(self, root_path: str) -> Dict[str, bool]:
        """
        DTD/XSLテンプレートをフォルダにコピー

        Args:
            root_path: ルートフォルダパス

        Returns:
            コピー結果
        """
        dtd_copied = False
        xsl_copied = False

        try:
            # DTDコピー
            dtd_src = self.get_dtd_template_path()
            dtd_dst = os.path.join(root_path, "PHOTO05.DTD")
            if os.path.exists(dtd_src):
                shutil.copy2(dtd_src, dtd_dst)
                dtd_copied = True
            else:
                # テンプレートがない場合はダミーファイル作成
                Path(dtd_dst).write_text("<!-- PHOTO05.DTD -->", encoding="shift_jis")
                dtd_copied = True

            # XSLコピー
            xsl_src = self.get_xsl_template_path()
            xsl_dst = os.path.join(root_path, "PHOTO05.XSL")
            if os.path.exists(xsl_src):
                shutil.copy2(xsl_src, xsl_dst)
                xsl_copied = True
            else:
                # テンプレートがない場合はダミーファイル作成
                Path(xsl_dst).write_text("<!-- PHOTO05.XSL -->", encoding="shift_jis")
                xsl_copied = True

        except Exception as e:
            print(f"テンプレートコピーエラー: {e}")

        return {
            "dtd_copied": dtd_copied,
            "xsl_copied": xsl_copied,
        }

    def save_photo_xml(self, root_path: str, xml_content: str) -> str:
        """
        PHOTO.XMLを保存

        Args:
            root_path: ルートフォルダパス
            xml_content: XML内容

        Returns:
            保存されたXMLファイルパス
        """
        xml_path = os.path.join(root_path, "PHOTO.XML")

        with open(xml_path, "w", encoding="shift_jis") as f:
            f.write(xml_content)

        return xml_path

    def create_zip_archive(
        self, source_folder: str, output_dir: str, archive_name: Optional[str] = None
    ) -> str:
        """
        ZIPアーカイブを作成

        Args:
            source_folder: ソースフォルダパス
            output_dir: 出力ディレクトリ
            archive_name: アーカイブ名（省略時は自動生成）

        Returns:
            作成されたZIPファイルパス
        """
        if archive_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"photo_export_{timestamp}.zip"

        zip_path = os.path.join(output_dir, archive_name)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            # フォルダ内の全ファイルをZIPに追加
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    # ZIP内でのパスを相対パスに
                    arcname = os.path.relpath(file_path, source_folder)
                    zipf.write(file_path, arcname)

        return zip_path

    def get_file_size(self, file_path: str) -> int:
        """
        ファイルサイズを取得

        Args:
            file_path: ファイルパス

        Returns:
            ファイルサイズ（バイト）
        """
        return os.path.getsize(file_path)

    def export_package(
        self,
        photos: List[Dict],
        xml_content: str,
        export_dir: str,
        project_name: Optional[str] = None,
    ) -> Dict:
        """
        エクスポートパッケージを作成（統合処理）

        Args:
            photos: 写真データリスト
            xml_content: PHOTO.XML内容
            export_dir: エクスポート先ディレクトリ
            project_name: プロジェクト名

        Returns:
            エクスポート結果
        """
        errors = []

        # バリデーション
        if not photos or len(photos) == 0:
            return {
                "success": False,
                "errors": ["写真が指定されていません"],
                "zip_path": None,
                "total_photos": 0,
            }

        try:
            # フォルダ構造作成
            folders = self.create_folder_structure(export_dir)

            # テンプレートコピー
            self.copy_templates_to_folder(folders["root"])

            # PHOTO.XML保存
            self.save_photo_xml(folders["root"], xml_content)

            # ZIPアーカイブ作成
            archive_name = (
                f"{project_name}_export.zip" if project_name else None
            )
            zip_path = self.create_zip_archive(
                folders["root"], export_dir, archive_name
            )

            return {
                "success": True,
                "errors": [],
                "zip_path": zip_path,
                "total_photos": len(photos),
                "file_size": self.get_file_size(zip_path),
            }

        except Exception as e:
            return {
                "success": False,
                "errors": [str(e)],
                "zip_path": None,
                "total_photos": 0,
            }

    def cleanup_temp_files(self, temp_dir: str):
        """
        一時ファイルをクリーンアップ

        Args:
            temp_dir: 一時ディレクトリパス
        """
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"一時ファイルクリーンアップエラー: {e}")
