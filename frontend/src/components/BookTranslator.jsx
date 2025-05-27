import React, { useState, useEffect } from "react";
import '../styles/index.css';
import languageData from "../data/languages.json";
import {FileInput} from "./FileInput.jsx";
import {LanguageSelect} from "./LanguageSelect.jsx";
import {TitleInput} from "./TitleInput.jsx";
import {TranslateButton} from "./TranslateButton.jsx";
import {SettingsModal} from "./SettingsModal.jsx";

export function BookTranslator() {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("Polish");
  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [languages, setLanguages] = useState([]);

  // Settings modal state
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settings, setSettings] = useState({
    apiKey: "",
    maxInputTokens: 2048,
    maxOutputTokens: 512,
    maxRequestsPerMinute: 60,
    maxTokensPerMinute: 100000,
  });

  useEffect(() => {
    setLanguages(languageData);
  }, []);

  useEffect(() => {
    const preventDefaults = (e) => {
      e.preventDefault();
      e.stopPropagation();
    };

    window.addEventListener("dragover", preventDefaults);
    window.addEventListener("drop", preventDefaults);

    return () => {
      window.removeEventListener("dragover", preventDefaults);
      window.removeEventListener("drop", preventDefaults);
    };
  }, []);

  useEffect(() => {
    if (file) {
      const nameWithoutExt = file.name.replace(/\.epub$/i, "");
      setTitle(`${nameWithoutExt}_${language}`);
    }
  }, [file, language]);

  const handleFileChange = (selectedFile) => {
    if (selectedFile && !selectedFile.name.toLowerCase().endsWith(".epub")) {
      setFile(null);
      setError("Only .epub files are supported.");
      setTitle("");
    } else {
      setFile(selectedFile);
      setError("");
      if (selectedFile) {
        const nameWithoutExt = selectedFile.name.replace(/\.epub$/i, "");
        setTitle(`${nameWithoutExt}_${language}`);
      }
    }
  };

  const handleTranslate = () => {
    if (!file) {
      setError("Please select a valid .epub file before translating.");
      return;
    }
    console.log("Translating:", { file, language, title, settings });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 to-purple-200 flex items-center justify-center p-4">
      <div className="bg-white/50 backdrop-blur-lg rounded-2xl p-6 shadow-xl max-w-md w-full relative">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-purple-800">
            Translate{" "}
            <span className="text-purple-900 font-bold">eBooks easily</span>
          </h2>

          {/* Settings gear icon */}
          <button
              onClick={() => setSettingsOpen(true)}
              className="text-purple-700 hover:text-purple-900 focus:outline-none"
              aria-label="Open settings"
          >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
            >
              <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 15.5a3.5 3.5 0 100-7 3.5 3.5 0 000 7z"
              />
              <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09a1.65 1.65 0 00-1-1.51 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09a1.65 1.65 0 001.51-1 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06a1.65 1.65 0 001.82.33h.09a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51h.09a1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82v.09a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"
              />
            </svg>
          </button>
        </div>

        <FileInput
            file={file}
            error={error}
            isDragging={isDragging}
            setIsDragging={setIsDragging}
            onFileChange={handleFileChange}
        />

        <LanguageSelect language={language} setLanguage={setLanguage} languages={languages}/>

        <TitleInput title={title} setTitle={setTitle}/>

        <TranslateButton onClick={handleTranslate}/>

        <SettingsModal
            isOpen={settingsOpen}
            onClose={() => setSettingsOpen(false)}
            settings={settings}
            setSettings={setSettings}
        />
      </div>
    </div>
  );
}
