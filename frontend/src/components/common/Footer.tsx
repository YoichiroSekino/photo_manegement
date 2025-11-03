export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="text-sm text-gray-600">
            <p>&copy; 2025 工事写真自動整理システム. All rights reserved.</p>
          </div>

          <div className="flex space-x-6 text-sm text-gray-600">
            <a href="#" className="hover:text-gray-900">
              利用規約
            </a>
            <a href="#" className="hover:text-gray-900">
              プライバシーポリシー
            </a>
            <a href="#" className="hover:text-gray-900">
              お問い合わせ
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
