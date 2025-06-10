import React from 'react';

export function UserGuidePage() {
    return (
        <div className="w-full max-w-2xl mx-auto p-8 bg-white/70 backdrop-blur-lg rounded-lg shadow-xl my-8">
            <h1 className="text-3xl font-bold text-purple-800 mb-6 text-center">User Guide for BookTranslator</h1>
            {/* Section 1: Optional API Key Configuration */}
            <div className="bg-purple-50 p-6 rounded-lg mb-6 border border-indigo-100">
                <h2 className="text-2xl font-semibold text-teal-800 mb-3">1. Optional: Configure Your Google AI API Key</h2>
                <p className="text-indigo-700 mb-4 pl-4">
                    While a Google AI API key is not strictly required for the translator to function, using your own key is
                    <span className="font-semibold text-yellow-700"> highly recommended</span>.
                    It provides you with dedicated usage limits, ensuring a more stable and robust translation experience tailored to your needs.
                </p>
                <h3 className="text-xl font-semibold text-cyan-700 mb-2">How to Generate an API Key:</h3>
                <p className="text-indigo-700 mb-2 pl-4">
                    Visit the Google AI Studio platform:
                    <a href="https://aistudio.google.com/app/apikey"
                       target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-semibold">aistudio.google.com/app/apikey</a>
                </p>
                <p className="text-indigo-700 mb-4 pl-4">
                    Once on the page, click on <span className="font-semibold text-yellow-700">"Create API key in new project" </span>
                    (or <span className="font-semibold">"Create API key"</span> if you have an existing project). Copy the generated key.
                </p>

                <h3 className="text-xl font-semibold text-cyan-700 mb-2">Configuring Translator Settings:</h3>
                <p className="text-indigo-700 mb-2 pl-4">
                    In the BookTranslator application, navigate to the <span className="font-semibold text-yellow-700">"Translator Settings"</span> section.
                    Here, you can paste your newly generated API key and set various model parameters:
                </p>
                <ul className="list-disc list-inside text-purple-600 mb-4 ml-4 pl-4">
                    <li className="mb-1">
                        <span className="font-semibold">Max Input Tokens & Max Output Tokens: </span>
                        Refer to the official Google AI documentation for recommended values for model
                        <a href="https://ai.google.dev/gemini-api/docs/models?hl=pl#gemini-2.0-flash"
                           target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-semibold"> Gemini 2.0 Flash</a>.
                        It's generally best for the input and output token limits to be similar.
                        For safety, you might set these fields to slightly lower values than the maximums.
                    </li>
                    <li className="mb-1">
                        <span className="font-semibold">Max Requests per Minute & Max Tokens per Minute: </span>
                        These rate limits depend on your specific access level/tier with Google AI. Consult the
                        <a href="https://ai.google.dev/gemini-api/docs/rate-limits?hl=pl"
                           target="_blank" rel="noopener noreferrer"
                           className="text-blue-600 hover:underline font-semibold"> Google AI rate limits documentation</a> to set these according to your allocated quota for your model.
                    </li>
                </ul>
                <p className="text-indigo-700 mb-0 pl-4">
                    After adjusting your preferences, remember to click
                    <span className="font-semibold text-yellow-700"> "Save"</span> to apply the changes to your translator settings.
                </p>
            </div>

            {/* Section 2: Uploading Your Book */}
            <div className="bg-indigo-50 p-6 rounded-lg mb-6 border border-indigo-100">
                <h2 className="text-2xl font-semibold text-teal-800 mb-3">2. Uploading Your Book</h2>
                <p className="text-indigo-700 mb-0 pl-4">
                    To begin, simply click on the designated file selection area or drag and drop your book file into it.
                    Please note that, for now, the translator supports <span className="font-semibold text-yellow-700">EPUB files only</span>.
                </p>
            </div>

            {/* Section 3: Choosing the Target Language */}
            <div className="bg-purple-50 p-6 rounded-lg mb-6 border border-indigo-100">
                <h2 className="text-2xl font-semibold text-teal-800 mb-3">3. Choosing the Target Language</h2>
                <p className="text-indigo-700 mb-0 pl-4">
                    Once your EPUB file is uploaded, use the dropdown menu to select the language you wish to translate your book into.
                </p>
            </div>

            {/* Section 4: Initiating Translation */}
            <div className="bg-indigo-50 p-6 rounded-lg mb-6 border border-indigo-100">
                <h2 className="text-2xl font-semibold text-teal-800 mb-3">4. Translating Your Book</h2>
                <p className="text-indigo-700 mb-0 pl-4">
                    After configuring all your settings, click the
                    <span className="font-semibold text-yellow-700">"Translate"</span> button to initiate the translation process.
                    Please be aware that the translation duration can vary significantly.
                    It depends heavily on the size of your book and the stability of your internet connection.
                    For very large files, this process might take a considerable amount of time, potentially
                    <span className="font-semibold text-yellow-700"> up to an hour or more</span>.
                    Ensure you have a strong, uninterrupted internet connection to prevent any disruptions during translation.
                </p>
            </div>

            {/* Section 5: Downloading the Translated Book */}
            <div className="bg-purple-50 p-6 rounded-lg mb-6 border border-indigo-100">
                <h2 className="text-2xl font-semibold text-teal-800 mb-3">5. Downloading the Translated Book</h2>
                <p className="text-indigo-700 mb-0 pl-4">
                    Once the translation is complete, a
                    <span className="font-semibold text-yellow-700"> "Download"</span> button will appear.
                    Simply click it to save your freshly translated book to your device.
                </p>
            </div>

            <p className="text-rose-700 text-center mt-8 text-lg font-semibold">
                Thank you for using BookTranslator! I hope this guide helps you get the most out of your translation experience.
            </p>
            <p className="text-indigo-700 mt-2 text-center">
                If you encounter bugs or have improvement ideas, feel free to
                <a href="mailto:your_email@example.com" className="text-blue-700 hover:underline font-semibold"> contact me</a>.
            </p>

            <div className="mt-8 text-center">
                <a href="/"
                   className="w-full bg-yellow-200 hover:bg-yellow-300 text-purple-700 font-semibold py-2 px-4 rounded border border-gray-300 transition duration-200">
                    Go to Translator!
                </a>
            </div>
        </div>
    );
}