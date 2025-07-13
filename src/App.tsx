import React, { useState } from "react";
import FriendCarousel from "./components/FriendCarousel";
import AssistantSidebar from "./components/AssistantSidebar";
import PinDetailCard from "./components/PinDetailCard";
import ChatInput from "./components/ChatInput";
import MapView from "./components/MapView";

export default function App() {
  const [pins, setPins] = useState([]);
  const [thoughts, setThoughts] = useState([]);
  const [content, setContent] = useState("");
  const [selectedPin, setSelectedPin] = useState(null);
  const [friends, setFriends] = useState([]); // fetched from backend
  const [user, setUser] = useState(null); // current user profile

  // SSE streaming logic will go here

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className="w-[420px] p-6 flex flex-col border-r border-gray-200 dark:border-gray-800">
        <AssistantSidebar thoughts={thoughts} content={content} user={user} />
        <ChatInput onSend={() => {}} />
      </div>
      {/* Main area */}
      <div className="flex-1 flex flex-col">
        {/* Friend carousel */}
        <div className="h-[30%] min-h-[180px] flex items-center overflow-x-auto px-6">
          <FriendCarousel friends={friends} />
        </div>
        {/* Map and pin details */}
        <div className="relative h-[60%]">
          <MapView pins={pins} onPinSelect={setSelectedPin} />
          {selectedPin && (
            <PinDetailCard pin={selectedPin} onClose={() => setSelectedPin(null)} />
          )}
        </div>
      </div>
    </div>
  );
} 