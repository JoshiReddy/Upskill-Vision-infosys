import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom"; // If using React Router

const QuizPage = () => {
  const { quizId } = useParams(); // Get quizId from the URL
  const { token } = useParams();
  const [quizData, setQuizData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [score, setScore] = useState(0);

  useEffect(() => {
    const fetchQuizData = async () => {
      try {
        const response = await fetch(
          `http://localhost:8080/api/user_course_progress/fetch_quizzes/${quizId}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        const data = await response.json();
        if (response.ok) {
          console.log(data.quizData);
          setQuizData(data.quizData);
        }
      } catch (error) {
        console.log(error);
      }
    };

    fetchQuizData();
  }, [quizId]);

  const handleOptionSelect = (questionId, selectedOptionId) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: selectedOptionId,
    }));
  };

  const handleSubmitQuiz = async () => {
    let calculatedScore = 0;

    Object.keys(quizData.questions).forEach((questionId) => {
      const question = quizData.questions[questionId];
      const correctOption = question.options.find(
        (option) => option.is_correct === 1
      );
      if (userAnswers[questionId] === correctOption.option_id) {
        calculatedScore += 1;
      }
    });

    setScore(calculatedScore);
    setQuizCompleted(true);
    // console.log(token, quizId, score, Object.keys(quizData.questions).length);

    try {
      const response = await fetch(
        `http://localhost:8080/api/user_course_progress/submitting_quizzes/${quizId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            token,
            score: calculatedScore,
            totalScore: Object.keys(quizData.questions).length,
          }),
        }
      );
      //   const data = await response.json();
      if (response.ok) {
        console.log("sucesssss");
        setTimeout(() => {
          window.close();
          if (window.opener) {
            window.opener.location.reload(); // Refresh the parent window
          }
        }, 5000);
      }
    } catch (error) {
      console.log(error);
    }
  };

  if (!quizData) {
    return <p>Loading quiz...</p>;
  }

  if (quizCompleted) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
        <h2 className="text-3xl font-bold mb-4">{quizData.title}</h2>
        <p className="text-xl">
          Your Score: {score} / {Object.keys(quizData.questions).length}
        </p>
      </div>
    );
  }

  const currentQuestionId = Object.keys(quizData.questions)[
    currentQuestionIndex
  ];
  const currentQuestion = quizData.questions[currentQuestionId];

  return (
    <>
      {quizData && (
        <div className="h-screen bg-gray-100 flex flex-col justify-center items-center">
          <h1 className="text-2xl font-bold mb-6">{quizData.title}</h1>
          <div className="w-3/4 bg-white p-6 rounded-lg shadow-lg">
            <h2 className="text-lg font-bold mb-4">
              Question {currentQuestionIndex + 1}:{" "}
              {currentQuestion.question_text}
            </h2>
            <ul className="space-y-4">
              {currentQuestion.options.map((option) => (
                <li key={option.option_id}>
                  <button
                    className={`w-full p-2 rounded-lg ${
                      userAnswers[currentQuestionId] === option.option_id
                        ? "bg-green-500 text-white"
                        : "bg-gray-200 hover:bg-gray-300"
                    }`}
                    onClick={() =>
                      handleOptionSelect(currentQuestionId, option.option_id)
                    }
                  >
                    {option.option_text}
                  </button>
                </li>
              ))}
            </ul>
            <div className="flex justify-between mt-6">
              {currentQuestionIndex > 0 && (
                <button
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={() => setCurrentQuestionIndex((prev) => prev - 1)}
                >
                  Previous
                </button>
              )}
              {currentQuestionIndex <
              Object.keys(quizData.questions).length - 1 ? (
                <button
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  onClick={() => setCurrentQuestionIndex((prev) => prev + 1)}
                >
                  Next
                </button>
              ) : (
                <button
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                  onClick={handleSubmitQuiz}
                >
                  Submit Quiz
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default QuizPage;
