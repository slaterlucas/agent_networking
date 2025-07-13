import React from "react";

interface PinDetailCardProps {
  pin: {
    id: string;
    title: string;
    details?: {
      address?: string;
      hours?: string;
      image?: string;
      reviews?: { user: string; text: string; }[];
    };
    emoji: string;
  };
  onClose: () => void;
}

const PinDetailCard: React.FC<PinDetailCardProps> = ({ pin, onClose }) => {
  return (
    <div className="absolute right-8 top-8 bg-white dark:bg-gray-800 rounded-card shadow-2xl p-6 w-[340px] z-20 flex flex-col items-center" style={{ borderRadius: 20 }}>
      <button className="absolute top-2 right-2 text-gray-400 hover:text-gray-700" onClick={onClose}>&times;</button>
      <div className="text-4xl mb-2">{pin.emoji}</div>
      <div className="font-bold text-xl mb-2 text-center">{pin.title}</div>
      {pin.details?.image && (
        <img src={pin.details.image} alt={pin.title} className="w-full h-32 object-cover rounded-lg mb-2" />
      )}
      {pin.details?.address && (
        <div className="text-sm text-gray-500 mb-1">{pin.details.address}</div>
      )}
      {pin.details?.hours && (
        <div className="text-xs text-gray-400 mb-2">Open: {pin.details.hours}</div>
      )}
      {pin.details?.reviews && pin.details.reviews.length > 0 && (
        <div className="w-full mt-2">
          <div className="font-semibold text-sm mb-1">Reviews:</div>
          <ul className="text-xs text-gray-600 dark:text-gray-300">
            {pin.details.reviews.map((review, idx) => (
              <li key={idx} className="mb-1">{review.user}: "{review.text}"</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PinDetailCard; 