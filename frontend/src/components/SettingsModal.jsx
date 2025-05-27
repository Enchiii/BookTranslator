export function SettingsModal({ isOpen, onClose, settings, setSettings }) {
  if (!isOpen) return null;

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = () => {
    console.log("Saving");
  };

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-indigo-100 to-purple-200 flex justify-center items-center z-50">
      <div className="bg-white/50 backdrop-blur-lg rounded-2xl p-6 shadow-xl max-w-md w-full shadow-lg">

        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-purple-800">Settings</h3>
          <button
              onClick={onClose}
              className="text-purple-600 hover:text-purple-900 font-bold text-2xl leading-none"
              aria-label="Close settings"
          >
            &times;
          </button>
        </div>

        <div className="flex flex-col gap-4">
          <label className="flex flex-col text-purple-800 font-semibold text-sm">
            API Key:
            <input
                type="text"
                value={settings.apiKey}
                onChange={(e) => handleChange("apiKey", e.target.value)}
                className="mt-1 p-2 border rounded border-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition duration-200"
                placeholder="Your API key"
            />
          </label>

          <label className="flex flex-col text-purple-800 font-semibold text-sm">
            Max Input Tokens:
            <input
                type="number"
                min={1}
                value={settings.maxInputTokens}
                onChange={(e) => handleChange("maxInputTokens", e.target.value)}
                className="mt-1 p-2 border rounded border-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition duration-200"
                placeholder="e.g. 2048"
            />
          </label>

          <label className="flex flex-col text-purple-800 font-semibold text-sm">
            Max Output Tokens:
            <input
                type="number"
                min={1}
                value={settings.maxOutputTokens}
                onChange={(e) => handleChange("maxOutputTokens", e.target.value)}
                className="mt-1 p-2 border rounded border-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition duration-200"
                placeholder="e.g. 512"
            />
          </label>

          <label className="flex flex-col text-purple-800 font-semibold text-sm">
            Max Requests per Minute:
            <input
                type="number"
                min={1}
                value={settings.maxRequestsPerMinute}
                onChange={(e) => handleChange("maxRequestsPerMinute", e.target.value)}
                className="mt-1 p-2 border rounded border-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition duration-200"
                placeholder="e.g. 60"
            />
          </label>

          <label className="flex flex-col text-purple-800 font-semibold text-sm">
            Max Tokens per Minute:
            <input
                type="number"
                min={1}
                value={settings.maxTokensPerMinute}
                onChange={(e) => handleChange("maxTokensPerMinute", e.target.value)}
                className="mt-1 p-2 border rounded border-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition duration-200"
                placeholder="e.g. 100000"
            />
          </label>

          <button
              onClick={handleSave}
              className="w-full bg-yellow-200 hover:bg-yellow-300 text-purple-700 font-semibold py-2 rounded border border-gray-300 transition duration-200"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}