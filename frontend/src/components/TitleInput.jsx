export function TitleInput({ title, setTitle }) {
  return (
    <div className="mb-4">
      <label className="block text-purple-800 text-sm font-semibold mb-1">
        Book title
      </label>
      <input
        type="text"
        placeholder="Book title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full text-purple-800 rounded border border-indigo-200 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:border-indigo-400 transition duration-200"
      />
    </div>
  );
}