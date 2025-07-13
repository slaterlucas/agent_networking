import React from "react";

interface AssistantSidebarProps {
  thoughts: string[];
  content: string;
  user: {
    name: string;
    photoUrl: string;
    interests: string[];
    cuisines: string[];
  } | null;
}

const AssistantSidebar: React.FC<AssistantSidebarProps> = ({ thoughts, content, user }) => {
  return (
    <div className="flex-1 flex flex-col">
      {/* User profile */}
      {user && (
        <div className="flex flex-col items-center mb-6">
          <img
            src={user.photoUrl}
            alt={user.name}
            className="w-24 h-24 object-cover mb-2"
            style={{ borderRadius: 90 }}
          />
          <div className="font-bold text-xl mb-1 text-center">{user.name}</div>
          <div className="text-xs text-gray-500 mb-1 text-center">
            Interests: {user.interests.join(", ")}
          </div>
          <div className="text-xs text-gray-500 text-center">
            Cuisines: {user.cuisines.join(", ")}
          </div>
        </div>
      )}
      {/* Streaming thoughts */}
      <div className="flex-1 overflow-y-auto">
        {thoughts.map((thought, idx) => (
          <div key={idx} className="italic text-gray-400 animate-pulse mb-2">{thought}</div>
        ))}
        {content && <div className="text-base text-gray-800 dark:text-gray-100 mt-4">{content}</div>}
      </div>
    </div>
  );
};

export default AssistantSidebar; 