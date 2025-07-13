const FriendCarousel = () => (
  <div className="flex space-x-4 overflow-x-auto">
    {/* Placeholder friend cards */}
    <div className="w-32 h-40 bg-blue-200 rounded-lg flex items-center justify-center">Friend 1</div>
    <div className="w-32 h-40 bg-green-200 rounded-lg flex items-center justify-center">Friend 2</div>
    <div className="w-32 h-40 bg-yellow-200 rounded-lg flex items-center justify-center">Friend 3</div>
  </div>
);

export default FriendCarousel;
