export function TranslateButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full bg-yellow-200 hover:bg-yellow-300 text-purple-700 font-semibold py-2 rounded border border-gray-300 transition duration-200"
    >
      Translate Book
    </button>
  );
}