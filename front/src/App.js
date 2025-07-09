import Login from "./components/Login";
import Welcome from "./components/Welcome";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import Footer from "./components/Footer";
import Register from "./components/Register";
import Contact from "./components/Contact";
import AboutUs from "./components/AboutUs";
import CourseContent from "./components/CourseContent";
import ViewModule from "./components/ViewModule";
import QuizPage from "./components/QuizPage";
import IndividualPerformance from "./components/IndividualPerformance";
import AllUsersPerformance from "./components/AllUsersPerformance";

function App() {
  return (
    <>
      <Router
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/login" element={<Login />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/about" element={<AboutUs />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route
            path="/dashboard/courses/:courseid"
            element={<CourseContent />}
          />
          <Route
            path="/dashboard/all-users-performance"
            element={<AllUsersPerformance />}
          />
          <Route
            path="/dashboard/user-performance/:token/:userId"
            element={<IndividualPerformance />}
          />
          <Route
            path="/dashboard/view-module/:courseId"
            element={<ViewModule />}
          />
          <Route path="/:token/quiz/:quizId" element={<QuizPage />} />
        </Routes>
        <Footer />
      </Router>
    </>
  );
}

export default App;
