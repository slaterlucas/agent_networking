import React, { useState } from "react";

interface ChatInputProps {
  onSend: (message: string, file?: File) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend }) => {
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const handleSend = () => {
    if (input.trim() || file) {
      onSend(input, file || undefined);
      setInput("");
      setFile(null);
    }
  };

  return (
    <div className="mt-4 flex items-center space-x-2">
      <input
        type="text"
        className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 dark:bg-gray-900 dark:text-white"
        placeholder="Start typing or upload a file..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter') handleSend(); }}
      />
      <input
        type="file"
        className="hidden"
        id="file-upload"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <label htmlFor="file-upload" className="cursor-pointer px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded-lg text-xs">
        📎
      </label>
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
        onClick={handleSend}
      >
        Send
      </button>
    </div>
  );
};

export default ChatInput; 