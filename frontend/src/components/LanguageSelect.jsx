import React from "react";

export function LanguageSelect({
  label,
  language,
  setLanguage,
  languages,
  includeAutoDetect,
}) {
  return (
    <div className="mb-3">
      <label className="block text-purple-800 text-sm font-semibold mb-1">
        {label}
      </label>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="w-full text-purple-800 rounded border border-indigo-200 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition"
      >
        {includeAutoDetect && (
          <option value="auto">✨ Auto-detect Language</option>
        )}
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
}
