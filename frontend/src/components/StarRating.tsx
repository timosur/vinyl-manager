import { useState } from "react";

export const StarRating: React.FC<{ initialRating: number, viewOnly: boolean, onRating?: (rating: number) => void }> = ({ initialRating, onRating, viewOnly }) => {
  const [rating, setRating] = useState(initialRating || 0);

  const handleRating = (rate: number) => {
    if (viewOnly) return;

    setRating(rate);
    if (onRating) {
      onRating(rate);
    }
  };

  return (
    <div className="flex items-center">
      {[...Array(5)].map((_, i) => (
        <svg
          key={i}
          onClick={() => handleRating(i + 1)}
          className={`h-5 w-5 ${viewOnly ? '' : 'cursor-pointer'} ${i < rating ? 'text-yellow-700' : 'text-gray-400'}`}
          fill="currentColor"
          viewBox="0 0 24 24">
          <path d="M12 .587l3.668 7.431L24 8.9l-6 5.833 1.417 8.267L12 19.764l-7.417 3.236L6 14.733 0 8.9l8.332-.982L12 .587z" />
        </svg>
      ))}
    </div>
  );
};