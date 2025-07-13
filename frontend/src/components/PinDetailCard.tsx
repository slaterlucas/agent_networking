const PinDetailCard = () => (
  <div className="w-72 bg-white dark:bg-gray-900 rounded-lg shadow-lg p-4">
    <h3 className="text-xl font-bold mb-2">Restaurant Name</h3>
    <p className="text-gray-600 dark:text-gray-300 mb-1">123 Main St, City</p>
    <p className="text-gray-500 dark:text-gray-400 mb-2">Open: 11am - 10pm</p>
    <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded mb-2 flex items-center justify-center">[Image]</div>
    <div className="text-sm text-gray-700 dark:text-gray-300">"Great food and atmosphere!"</div>
  </div>
);

export default PinDetailCard;
