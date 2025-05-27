export function FileInput({ file, error, isDragging, setIsDragging, onFileChange }) {
  return (
    <label
      htmlFor="file-upload"
      className={`flex flex-col items-center gap-2 p-4 rounded-lg cursor-pointer transition mb-6 border-2 border-dashed ${
        isDragging
          ? "bg-indigo-100 border-indigo-400"
          : error
          ? "bg-red-50 border-red-400"
          : file
          ? "bg-green-50 border-green-400"
          : "bg-white/60 border-indigo-200 hover:border-indigo-400"
      }`}
      onDragEnter={() => setIsDragging(true)}
      onDragLeave={() => setIsDragging(false)}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files.length > 0) {
          onFileChange(e.dataTransfer.files[0]);
        }
      }}
    >
      <span className={`text-2xl ${error ? "text-red-500" : "text-purple-800"}`}>
        {error ? "❌" : file ? "✅" : "📘"}
      </span>
      <p className={`text-sm ${error ? "text-red-600" : file ? "text-green-700" : "text-purple-900"} text-center`}>
        {error
          ? error
          : file
          ? <span>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
          : "Choose or drag and drop a file here (.epub only)"}
      </p>

      <input
        id="file-upload"
        type="file"
        accept=".epub"
        onChange={(e) => {
          if (e.target.files.length > 0) onFileChange(e.target.files[0]);
        }}
        className="hidden"
      />
    </label>
  );
}