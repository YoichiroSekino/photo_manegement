/**
 * 品質詳細表示コンポーネント
 */

'use client';

interface QualityIssue {
  type: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  recommendation?: string;
}

interface QualityDetailsProps {
  score: number;
  sharpness?: number;
  brightness?: number;
  contrast?: number;
  issues?: QualityIssue[];
}

export function QualityDetails({
  score,
  sharpness,
  brightness,
  contrast,
  issues = [],
}: QualityDetailsProps) {
  const severityColors = {
    high: 'bg-red-100 text-red-800 border-red-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-blue-100 text-blue-800 border-blue-200',
  };

  const severityLabels = {
    high: '重要',
    medium: '警告',
    low: '情報',
  };

  return (
    <div className="bg-white rounded-lg border p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4">品質詳細</h3>

        {/* 総合スコア */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">総合品質スコア</span>
            <span className="text-2xl font-bold text-gray-900">{score}点</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                score >= 80
                  ? 'bg-green-500'
                  : score >= 60
                    ? 'bg-blue-500'
                    : score >= 40
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
              }`}
              style={{ width: `${score}%` }}
            />
          </div>
        </div>

        {/* 品質指標 */}
        {(sharpness !== undefined || brightness !== undefined || contrast !== undefined) && (
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700">品質指標</h4>

            {sharpness !== undefined && (
              <QualityMetric label="シャープネス" value={sharpness} />
            )}

            {brightness !== undefined && (
              <QualityMetric label="明るさ" value={brightness} />
            )}

            {contrast !== undefined && (
              <QualityMetric label="コントラスト" value={contrast} />
            )}
          </div>
        )}
      </div>

      {/* 品質問題 */}
      {issues.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 mb-3">検出された問題</h4>
          <div className="space-y-2">
            {issues.map((issue, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${severityColors[issue.severity]}`}
              >
                <div className="flex items-start space-x-2">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-white bg-opacity-50">
                    {severityLabels[issue.severity]}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{issue.message}</p>
                    {issue.recommendation && (
                      <p className="text-xs mt-1 opacity-75">
                        推奨: {issue.recommendation}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 推奨アクション */}
      {score < 60 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <svg
              className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-800">推奨アクション</p>
              <p className="text-sm text-yellow-700 mt-1">
                この写真は品質基準を満たしていない可能性があります。再撮影を検討してください。
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface QualityMetricProps {
  label: string;
  value: number;
}

function QualityMetric({ label, value }: QualityMetricProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-600">{label}</span>
        <span className="text-sm font-semibold text-gray-900">{value}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
