import React, { useState, useEffect } from "react";
import "../styles/index.css";
import languageData from "../data/languages.json";
import { FileInput } from "./FileInput.jsx";
import { LanguageSelect } from "./LanguageSelect.jsx";
import { TitleInput } from "./TitleInput.jsx";
import { setCookie, getCookie } from "../utils/cookies.js";
import { Button } from "./Button.jsx";

export function BookTranslator() {
  const [translating, setTranslating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [file, setFile] = useState(null);

  // Use NLLB FLORES-200 language codes directly
  const [srcLanguage, setSrcLanguage] = useState(
    () => getCookie("srcLanguage") || "auto",
  );
  const [targetLanguage, setTargetLanguage] = useState(
    () => getCookie("targetLanguage") || "pol_Latn",
  );

  const [title, setTitle] = useState("");
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [languages, setLanguages] = useState([]);

  useEffect(() => {
    if (!downloadUrl) return;

    return () => {
      URL.revokeObjectURL(downloadUrl);
    };
  }, [downloadUrl]);

  useEffect(() => {
    setCookie("srcLanguage", srcLanguage);
  }, [srcLanguage]);

  useEffect(() => {
    setCookie("targetLanguage", targetLanguage);
  }, [targetLanguage]);

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

  // Update book title preview based on file name and target language code
  useEffect(() => {
    if (file) {
      const nameWithoutExt = file.name.replace(/\.epub$/i, "");
      setTitle(`${nameWithoutExt}_${targetLanguage}`);
    }
  }, [file, targetLanguage]);

  const handleFileChange = (selectedFile) => {
    if (selectedFile && !selectedFile.name.toLowerCase().endsWith(".epub")) {
      setFile(null);
      setError("Only .epub files are supported.");
      setTitle("");
    } else if (
      selectedFile &&
      selectedFile.type !== "application/epub+zip" &&
      !selectedFile.name.endsWith(".epub")
    ) {
      setError("Invalid EPUB file type.");
    } else {
      setFile(selectedFile);
      setError("");
      if (selectedFile) {
        const nameWithoutExt = selectedFile.name.replace(/\.epub$/i, "");
        setTitle(`${nameWithoutExt}_${targetLanguage}`);
      }
    }
  };

  const pollTaskProgress = async (taskId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/task-status/${taskId}`,
        );
        const data = await response.json();

        if (data.progress !== undefined) {
          setProgress(data.progress);
        }

        if (data.state === "SUCCESS") {
          clearInterval(interval);

          try {
            const downloadResp = await fetch(
              `http://localhost:8000/download/${taskId}`,
            );
            const blob = await downloadResp.blob();
            const url = URL.createObjectURL(blob);
            setDownloadUrl(url);
          } catch (e) {
            setError("Download failed after success.");
          }

          setTranslating(false);
        } else if (data.state === "FAILURE") {
          clearInterval(interval);
          setError(`Translation failed: ${data.error || "Unknown error"}`);
          setTranslating(false);
        }
      } catch (e) {
        console.error("Polling error", e);
        clearInterval(interval);
        setError("Connection error during polling.");
        setTranslating(false);
      }
    }, 5000); // Polling every 5 seconds for better UX over local background tasks
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
    formData.append("src_lang", srcLanguage);
    formData.append("target_lang", targetLanguage);
    formData.append("title", title);

    try {
      const response = await fetch("http://localhost:8000/translate-book/", {
        style: "cors",
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(`Error: ${errorData.detail || response.statusText}`);
        setTranslating(false);
        return;
      }

      const { task_id } = await response.json();
      if (!task_id) {
        setError("No task ID returned from server.");
        setTranslating(false);
        return;
      }

      pollTaskProgress(task_id);
    } catch (err) {
      console.error(err);
      setError("An error occurred during translation submission.");
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
      <div className="bg-white/50 backdrop-blur-lg rounded-2xl p-6 max-w-md w-full relative shadow-xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-purple-800">
            Translate{" "}
            <span className="text-purple-900 font-bold">eBooks easily</span>
          </h2>
        </div>

        <FileInput
          file={file}
          error={error}
          isDragging={isDragging}
          setIsDragging={setIsDragging}
          onFileChange={handleFileChange}
        />

        {/* Source Language Input with Auto Detect functionality */}
        <LanguageSelect
          label="Source language:"
          language={srcLanguage}
          setLanguage={setSrcLanguage}
          languages={languages}
          includeAutoDetect={false}
        />

        {/* Target Language Input */}
        <LanguageSelect
          label="Target language:"
          language={targetLanguage}
          setLanguage={setTargetLanguage}
          languages={languages}
          includeAutoDetect={false}
        />

        <TitleInput title={title} setTitle={setTitle} />

        <Button
          downloadUrl={downloadUrl}
          handleDownload={handleDownload}
          translating={translating}
          handleTranslate={handleTranslate}
          progress={progress}
        />
      </div>
    </div>
  );
}
