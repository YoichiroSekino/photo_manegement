/**
 * 品質バッジコンポーネント
 */

'use client';

interface QualityBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function QualityBadge({ score, size = 'md', showLabel = true }: QualityBadgeProps) {
  const getQualityLevel = (score: number) => {
    if (score >= 80) return { label: '優', color: 'bg-green-500', textColor: 'text-green-700' };
    if (score >= 60) return { label: '良', color: 'bg-blue-500', textColor: 'text-blue-700' };
    if (score >= 40) return { label: '可', color: 'bg-yellow-500', textColor: 'text-yellow-700' };
    return { label: '不可', color: 'bg-red-500', textColor: 'text-red-700' };
  };

  const quality = getQualityLevel(score);

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2',
  };

  return (
    <div className="inline-flex items-center space-x-2">
      <span className={`${quality.color} text-white rounded-full font-bold ${sizeClasses[size]}`}>
        {quality.label}
      </span>
      {showLabel && (
        <span className={`${sizeClasses[size]} font-medium ${quality.textColor}`}>
          {score}点
        </span>
      )}
    </div>
  );
}
