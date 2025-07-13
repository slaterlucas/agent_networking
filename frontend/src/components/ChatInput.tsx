const ChatInput = () => (
  <form className="flex items-center space-x-2">
    <input
      type="text"
      className="flex-1 p-2 rounded border border-gray-300 dark:bg-gray-800 dark:text-white"
      placeholder="Ask the agents or suggest a place..."
      disabled
    />
    <button
      type="submit"
      className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      disabled
    >
      Send
    </button>
  </form>
);

export default ChatInput;
