import './styles/index.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {BookTranslator} from "./components/BookTranslator.jsx";
import {UserGuidePage} from "./components/UserGuidePage.jsx";
import {Footer} from "./components/Footer.jsx";

const App = () =>{

  return (
      <Router>
          <div className="min-h-screen bg-gradient-to-br from-indigo-100 to-purple-200 flex flex-col items-center p-4">
              <Routes>
                  <Route path="/" element={<BookTranslator></BookTranslator>}/>
                  <Route path="/user-guide" element={<UserGuidePage />} />
              </Routes>
              <Footer></Footer>
          </div>
      </Router>
)
}

export default App
