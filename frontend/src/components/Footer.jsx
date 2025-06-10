import React from 'react';
import { Link } from 'react-router-dom';

export function Footer(){
    return(
        <>
            <footer className="w-full sm:w-3/4 md:w-1/2 lg:w-2/5 mx-auto text-center text-purple-800 text-sm pt-4 pb-0 mt-8 border-t border-indigo-300">
                <div className="flex flex-col sm:flex-row justify-center items-center gap-2 sm:gap-4">
                    <span className="text-purple-700">
                        Check out
                        <Link to="/user-guide" className="text-blue-700 hover:underline font-semibold"> User Guide </Link>
                        to learn how to use this best
                    </span>
                    <span
                        className="hidden sm:inline text-purple-500">|</span>
                    <a href="https://github.com/Enchiii/BookTranslator" target="_blank" rel="noopener noreferrer"
                       className="text-purple-700 hover:text-purple-900 hover:underline">View source code on  <span className="font-bold text-purple-500">GitHub</span></a>
                </div>

                <p className="text-purple-600 mt-2">
                    Encounter bugs or have improvement ideas? Feel free to
                    <a href="mailto:your_email@example.com" className="text-blue-700 hover:underline font-semibold"> contact me</a>.
                </p>

                <p className="mt-2 text-purple-600">
                    <span className="font-bold text-purple-800">&copy; </span> {new Date().getFullYear()}
                    BookTranslator. Powered by <span className="font-bold text-purple-500">Google AI</span>.
                </p>
            </footer>
        </>
)
}