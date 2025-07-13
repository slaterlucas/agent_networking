import React from "react";

interface Friend {
  id: string;
  name: string;
  photoUrl: string;
  interests: string[];
  cuisines: string[];
}

interface FriendCarouselProps {
  friends: Friend[];
}

const FriendCarousel: React.FC<FriendCarouselProps> = ({ friends }) => {
  return (
    <div className="flex space-x-6 w-full">
      {friends.length === 0 ? (
        <div className="text-gray-400 italic">No friends to show</div>
      ) : (
        friends.map((friend) => (
          <div
            key={friend.id}
            className="bg-white dark:bg-gray-800 rounded-card shadow-lg p-4 flex flex-col items-center min-w-[180px] max-w-[220px]"
            style={{ borderRadius: 20 }}
          >
            <img
              src={friend.photoUrl}
              alt={friend.name}
              className="w-20 h-20 object-cover mb-2"
              style={{ borderRadius: 90 }}
            />
            <div className="font-bold text-lg mb-1 text-center">{friend.name}</div>
            <div className="text-xs text-gray-500 mb-1 text-center">
              Interests: {friend.interests.join(", ")}
            </div>
            <div className="text-xs text-gray-500 text-center">
              Cuisines: {friend.cuisines.join(", ")}
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default FriendCarousel; 