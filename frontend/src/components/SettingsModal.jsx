import { useEffect, useState } from "react";
import {setCookie, getCookie} from "../utils/cookies.js";
import { Link } from 'react-router-dom';


export function SettingsModal({ isOpen, onClose, settings, setSettings }) {
  const [initialSettings, setInitialSettings] = useState(settings);

  useEffect(() => {
    if (isOpen) {
      setInitialSettings(settings);

      const loadedSettings = {
        apiKey: getCookie("api_key") || settings.apiKey,
        maxInputTokens: parseInt(getCookie("max_input_tokens") || settings.maxInputTokens, 10),
        maxOutputTokens: parseInt(getCookie("max_output_tokens") || settings.maxOutputTokens, 10),
        maxRequestsPerMinute: parseInt(getCookie("max_requests_per_minute") || settings.maxRequestsPerMinute, 10),
        maxTokensPerMinute: parseInt(getCookie("max_tokens_per_minute") || settings.maxTokensPerMinute, 10),
      };

      setSettings(loadedSettings);
    }
  }, [isOpen]);

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = () => {
    setCookie("api_key", settings.apiKey);
    setCookie("max_input_tokens", settings.maxInputTokens);
    setCookie("max_output_tokens", settings.maxOutputTokens);
    setCookie("max_requests_per_minute", settings.maxRequestsPerMinute);
    setCookie("max_tokens_per_minute", settings.maxTokensPerMinute);

    console.log("Settings saved to cookies.");
    onClose();
  };

  const handleClose = () => {
    setSettings(initialSettings);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-indigo-100 to-purple-200 flex justify-center items-center z-50">
      <div className="bg-white/50 backdrop-blur-lg rounded-2xl p-6 shadow-xl max-w-md w-full shadow-lg flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-purple-800">Settings</h3>
          <button
            onClick={handleClose}
            className="text-purple-600 hover:text-purple-900 font-bold text-2xl leading-none"
            aria-label="Close settings"
          >
            &times;
          </button>
        </div>

        {/* Changed warning with link in English */}
        <p className="text-red-500 bg-red-100 p-2 rounded-md mb-4 text-sm">
          <strong>Warning:</strong> Do not change these settings unless you know what you are doing. Check the
          <Link to="/user-guide" className="text-blue-700 hover:underline font-semibold"> User Guide</Link> first.
        </p>

        <div className="flex flex-col gap-4 flex-grow">
          {[
            { label: "API Key", field: "apiKey", type: "text", placeholder: "Your API key" },
            { label: "Max Input Tokens", field: "maxInputTokens", type: "number", placeholder: "e.g. 2048" },
            { label: "Max Output Tokens", field: "maxOutputTokens", type: "number", placeholder: "e.g. 512" },
            { label: "Max Requests per Minute", field: "maxRequestsPerMinute", type: "number", placeholder: "e.g. 60" },
            { label: "Max Tokens per Minute", field: "maxTokensPerMinute", type: "number", placeholder: "e.g. 100000" },
          ].map(({ label, field, type, placeholder }) => (
            <label key={field} className="flex flex-col text-purple-800 font-semibold text-sm">
              {label}:
              <input
                type={type}
                value={settings[field]}
                onChange={(e) =>
                  handleChange(field, type === "number" ? Number(e.target.value) : e.target.value)
                }
                className="mt-1 p-2 border rounded border-indigo-200 focus:outline-none focus:ring-2
                focus:ring-indigo-400 hover:border-indigo-400 transition duration-200"
                placeholder={placeholder}
              />
            </label>
          ))}

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