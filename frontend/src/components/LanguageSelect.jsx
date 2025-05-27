export function LanguageSelect({ language, setLanguage, languages }) {
  return (
    <div className="mb-3">
      <label className="block text-purple-800 text-sm font-semibold mb-1">
        Target language:
      </label>
      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="w-full text-purple-800 rounded border border-indigo-200 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
}