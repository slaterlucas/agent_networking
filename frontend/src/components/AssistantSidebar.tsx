const AssistantSidebar = () => (
  <div>
    <h2 className="text-lg font-bold mb-4 text-gray-800 dark:text-gray-100">AI Thoughts</h2>
    <ul className="space-y-3 mb-6">
      <li className="bg-gray-100 dark:bg-gray-700 rounded px-4 py-3 text-gray-800 dark:text-gray-100 shadow-sm">Let's find a great restaurant nearby!</li>
      <li className="bg-gray-100 dark:bg-gray-700 rounded px-4 py-3 text-gray-800 dark:text-gray-100 shadow-sm">Charlie suggests sushi.</li>
      <li className="bg-gray-100 dark:bg-gray-700 rounded px-4 py-3 text-gray-800 dark:text-gray-100 shadow-sm">Bob is looking for vegan options.</li>
    </ul>
    <hr className="my-4 border-gray-300 dark:border-gray-600" />
    <div className="text-gray-500 dark:text-gray-400 text-sm">Let's annotate these locations on the map.</div>
  </div>
);

export default AssistantSidebar;
