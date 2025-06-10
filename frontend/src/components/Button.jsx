import React from "react";

export function Button({downloadUrl, handleDownload, translating, handleTranslate, progress}){
    return (
        <>
            {downloadUrl ? (
          <button
            onClick={handleDownload}
            className="w-full bg-yellow-200 hover:bg-yellow-300 text-purple-700 font-semibold py-2 rounded border border-gray-300 transition duration-200"
          >
            Download Translated Book
          </button>
        ) : (
          <button
            onClick={handleTranslate}
            disabled={translating}
            className="w-full bg-yellow-200 hover:bg-yellow-300 text-purple-700 font-semibold py-2 rounded border border-gray-300 transition duration-200 flex items-center justify-center gap-2"
          >
            {translating ? (
              <>
                <svg className="animate-spin h-4 w-4 text-purple-700" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.372 0 0 5.372 0 12h4z"
                  />
                </svg>
                <span>Translating... {progress}%</span>
              </>
            ) : (
              "Translate Book"
            )}
          </button>
        )}
        </>
    )
}
