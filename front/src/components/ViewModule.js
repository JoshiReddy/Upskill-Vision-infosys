import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import logo from "../assests/256 icon.png";

const ViewModule = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("t");
  const moduleId = searchParams.get("id");
  const [items, setItems] = useState(null);
  const [quizScores, setQuizcores] = useState(null);
  const [currentItem, setCurrentItem] = useState(0); // Keeps track of the current item (lesson or quiz)
  const [completedItems, setCompletedItems] = useState([]); // Keeps track of completed lessons and quizzes
  const [message, setMessage] = useState("");
  const updateModuleStatus = async () => {
    try {
      const response = await fetch(
        "http://localhost:8080/api/user_course_progress/update_module_status",
        {
          method: "POST",
          headers: { Authorization: token, "Content-Type": "application/json" },
          body: JSON.stringify({
            percentage: ((completedItems.length + 1) / items.length) * 100,
            moduleId,
          }),
        }
      );
      const data = await response.json();
      if (response.ok) {
        console.log("succeessss");
        if (data.complete) {
          window.close();
          if (window.opener) {
            window.opener.location.reload(); // Refresh the parent window
          }
        } else if (data.incomplete) {
          alert("Please, Complete the module fully");
        }
      }
    } catch (error) {
      console.log(error);
    }
  };
  const fetchModuleData = async () => {
    try {
      const response = await fetch(
        `http://localhost:8080/api/user_course_progress/lessons_quizzes/${moduleId}`,
        {
          method: "GET",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
        }
      );
      const data = await response.json();

      // Combine lessons and quizzes into a single array
      const combinedItems = [
        ...data.moduleData.lessons.map((item) => ({
          ...item,
          type: "lesson",
        })),
        ...data.moduleData.quizzes.map((item) => ({ ...item, type: "quiz" })),
      ];

      // Extract completed items (lessons and quizzes)
      const completedItems = [
        ...data.moduleData.lessons
          .filter((lesson) => lesson.status === "completed")
          .map((lesson) => lesson.lesson_id),
        ...data.moduleData.quizzes
          .filter((quiz) => quiz.status === "pass")
          .map((quiz) => quiz.quiz_id),
      ];
      console.log("module data", data.moduleData);

      setItems(combinedItems); // Set the combined items
      setCompletedItems(completedItems);
      setQuizcores(data.quizScores);
      // console.log("Combined Items", combinedItems);
      // Set the combined items
    } catch (error) {
      console.error("Error fetching module data:", error);
    }
  };
  useEffect(() => {
    fetchModuleData();
    // eslint-disable-next-line
  }, [moduleId, token]);

  const handleNext = () => {
    if (currentItem < items.length - 1) {
      setCurrentItem(currentItem + 1);
    }
  };

  const handlePrev = () => {
    if (currentItem > 0) {
      setCurrentItem(currentItem - 1);
    }
  };

  // API request to update the lesson status
  const markAsRead = async (lessonId) => {
    try {
      const response = await fetch(
        `http://localhost:8080/api/user_course_progress/mark_lesson_as_read/${lessonId}`,
        {
          method: "POST",
          headers: {
            Authorization: token,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            percentage: ((completedItems.length + 1) / items.length) * 100,
            moduleId,
          }),
        }
      );
      // console.log({ ...completedItems, ...currentItem }.length);
      // const data = await response.json();

      // Update completed lessons and show message
      if (response.ok) {
        fetchModuleData();
        setCompletedItems([...completedItems, currentItem]);
        setMessage(`Lesson "${items[currentItem].title}" marked as read.`);
        setTimeout(() => setMessage(""), 3000);
      } else {
        setMessage(
          `Failed to mark lesson "${items[currentItem].title}" as read.`
        );
        setTimeout(() => setMessage(""), 3000);
      }
    } catch (error) {
      console.error("Error marking lesson as read:", error);
      setMessage("Error marking lesson as read.");
      setTimeout(() => setMessage(""), 3000);
    }
  };

  // Function to handle quiz participation
  const participateInQuiz = async (quizId) => {
    console.log(`Participating in quiz with ID: ${quizId}`);
    const quizUrl = `/${token}/quiz/${quizId}`;
    window.open(quizUrl, "_blank", "fullscreen=yes");
    // setQuizOpen(true);
    // You can add logic to navigate to the quiz page or open a quiz modal
  };

  return (
    <div className="flex h-screen w-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-72 bg-white border-r border-gray-300 overflow-y-auto p-4 justify-around">
        <div className="flex flex-row justify-center items-center">
          <img src={logo} alt="" className="size-16 m-2" />
          <div className="flex flex-col p-2 font-koulen">
            <p className="flex items-end text-4xl text-primary">UPSKILL</p>
            <p className="flex items-start text-2xl text-red-500">vision</p>
          </div>
        </div>
        <div>
          <h3 className="text-xl font-bold mb-4">Module Content</h3>
          <ul className="space-y-2">
            {items &&
              items.map((item, index) => (
                <li
                  key={index}
                  className={`p-3 rounded-lg cursor-pointer transition-colors duration-200 ${
                    index === currentItem
                      ? "bg-green-200 border-green-400 font-semibold border"
                      : item.status === "completed" || item.status === "pass"
                      ? "bg-gray-200 text-gray-600"
                      : "hover:bg-green-100"
                  }`}
                  onClick={() => setCurrentItem(index)}
                >
                  {item.title}
                </li>
              ))}
          </ul>
        </div>
      </aside>

      {/* Main Content */}
      {items && (
        <main className="flex-1 bg-white p-6 overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">{items[currentItem].title}</h2>
            <div className="space-x-4">
              <button
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400"
                onClick={handlePrev}
                disabled={currentItem === 0}
              >
                Prev
              </button>
              <button
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400"
                onClick={handleNext}
                disabled={currentItem === items.length - 1}
              >
                Next
              </button>

              {items[currentItem].type === "lesson" && (
                <>
                  {items[currentItem].status === "completed" ? (
                    <button
                      disabled
                      className="px-6 py-2 bg-gray-400 cursor-not-allowed text-white rounded"
                    >
                      Marked as Read
                    </button>
                  ) : (
                    <button
                      onClick={() => markAsRead(items[currentItem].lesson_id)}
                      className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Mark as Read
                    </button>
                  )}
                </>
              )}
              {items[currentItem].type === "quiz" &&
              items[currentItem].status === "pass" ? (
                <button
                  onClick={() => updateModuleStatus()}
                  className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Complete Module
                </button>
              ) : (
                ""
              )}
            </div>
          </div>

          {message && <p className="text-green-500 mb-4">{message}</p>}

          <div className="prose">
            {items[currentItem].type === "lesson" ? (
              <p>{items[currentItem].description}</p>
            ) : items[currentItem].type === "quiz" &&
              items[currentItem].status === "pass" ? (
              <>
                <button className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-not-allowed">
                  Quizz Completed
                </button>
                <div className="flex flex-row flex-wrap justify-around py-20 text-center">
                  <div className="flex flex-col items-center justify-center h-40 rounded-lg shadow-lg w-40 border-2 border-green-300 relative">
                    <strong>Total Score:</strong>
                    <span className="text-lg font-semibold">
                      {quizScores[0][2]}/{quizScores[0][3]}
                    </span>

                    <div className="w-4/5 h-2 bg-gray-200 rounded-lg overflow-hidden relative border border-gray-300">
                      {/* Progress Bar */}
                      <div
                        className="h-full bg-green-500"
                        style={{
                          width: `${
                            (quizScores[0][2] / quizScores[0][3]) * 100
                          }%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  <p className="flex flex-col items-center justify-center h-40 rounded-lg shadow-lg w-40 border-2 border-green-300">
                    <strong>Result:</strong>
                    <span>{quizScores[0][4]}</span>
                  </p>
                  <p className="flex flex-col items-center justify-center h-40 rounded-lg shadow-lg w-40 border-2 border-green-300">
                    <strong>Last Attempt:</strong>
                    <span>{quizScores[0][5]}</span>
                  </p>
                </div>
              </>
            ) : (
              <button
                onClick={() => participateInQuiz(items[currentItem].quiz_id)}
                className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Participate in Quiz
              </button>
            )}
          </div>
        </main>
      )}
    </div>
  );
};

export default ViewModule;
