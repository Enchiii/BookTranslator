import React, { useState, useEffect } from "react";
import '../styles/index.css';
import languageData from "../data/languages.json";
import {FileInput} from "./FileInput.jsx";
import {LanguageSelect} from "./LanguageSelect.jsx";
import {TitleInput} from "./TitleInput.jsx";
import {SettingsModal} from "./SettingsModal.jsx";
import {setCookie, getCookie} from "../utils/cookies.js";
import {Button} from "./Button.jsx";
import {Footer} from "./Footer.jsx"


export function BookTranslator() {

  const [translating, setTranslating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState(() => getCookie("targetLanguage") || "Polish");

  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [languages, setLanguages] = useState([]);

  // Settings modal state
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settings, setSettings] = useState({
    apiKey: "",
    maxInputTokens: 4000,
    maxOutputTokens: 6000,
    maxRequestsPerMinute: 15,
    maxTokensPerMinute: 1000000,
  });

  useEffect(() => {
    if (!downloadUrl) return;

    return () => {
      URL.revokeObjectURL(downloadUrl);
    };
  }, [downloadUrl]);

  useEffect(() => {
    setCookie("targetLanguage", language);
  }, [language]);


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
    } else if (selectedFile && (selectedFile.type !== "application/epub+zip")) {
      setError("Invalid EPUB file type.");
    } else {
      setFile(selectedFile);
      setError("");
      if (selectedFile) {
        const nameWithoutExt = selectedFile.name.replace(/\.epub$/i, "");
        setTitle(`${nameWithoutExt}_${language}`);
      }
    }
  };

  const pollTaskProgress = async (taskId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/task-status/${taskId}`);
        const data = await response.json();

        if (data.progress !== undefined) {
          setProgress(data.progress);
        }

        if (data.state === "SUCCESS") {
          clearInterval(interval);

          try {
            const downloadResp = await fetch(`http://localhost:8000/download/${taskId}`);
            const blob = await downloadResp.blob();
            const url = URL.createObjectURL(blob);
            setDownloadUrl(url);
            // eslint-disable-next-line no-unused-vars
          } catch (e) {
            setError("Download failed after success.");
          }

          setTranslating(false);
        } else if (data.state === "FAILURE") {
          clearInterval(interval);
          setError("Translation failed.");
          setTranslating(false);
        }
      } catch (e) {
        console.error("Polling error", e);
        clearInterval(interval);
        setError("Connection error during polling.");
        setTranslating(false);
      }
    }, 20000); // checking 1 time per 20s
  };


  const handleTranslate = async () => {
    if (!file) {
    setError("Please select a valid .epub file before translating.");
    return;
  }

    setError("");
    setTranslating(true);
    setDownloadUrl(null);
    setProgress(0);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);

    const loadedSettings = {
      apiKey: getCookie("apiKey") || "",
      maxInputTokens: parseInt(getCookie("maxInputTokens") || settings.maxInputTokens, 10),
      maxOutputTokens: parseInt(getCookie("maxOutputTokens") || settings.maxOutputTokens, 10),
      maxRequestsPerMinute: parseInt(getCookie("maxRequestsPerMinute") || settings.maxRequestsPerMinute, 10),
      maxTokensPerMinute: parseInt(getCookie("maxTokensPerMinute") || settings.maxTokensPerMinute, 10),
    };

    for (const [key, value] of Object.entries(loadedSettings)) {
      formData.append(key, value);
    }

    try {
      const response = await fetch("http://localhost:8000/translate-book/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(`Error: ${errorData.error || response.statusText}`);
        setTranslating(false);
        return;
      }

      const { task_id } = await response.json();
      if (!task_id) {
        setError("No task ID returned.");
        setTranslating(false);
        return;
      }

      pollTaskProgress(task_id);

    } catch (err) {
      console.error(err);
      setError("An error occurred during translation.");
      setTranslating(false);
    }
  };

  const handleDownload = () => {
    if (!downloadUrl) return;

    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = `${title}.epub`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
      <div className="flex-grow flex items-center justify-center w-full">
        <div
            className={`bg-white/50 backdrop-blur-lg rounded-2xl p-6 max-w-md w-full relative ${settingsOpen ? '' : 'shadow-xl'}`}>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-purple-800">
              Translate{" "}
              <span className="text-purple-900 font-bold">eBooks easily</span>
            </h2>

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

          <Button
              downloadUrl={downloadUrl}
              handleDownload={handleDownload}
              translating={translating}
              handleTranslate={handleTranslate}
              progress={progress}
          />

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