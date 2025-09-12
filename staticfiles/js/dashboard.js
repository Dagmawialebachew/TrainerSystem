// Dashboard JavaScript functionality

document.addEventListener("DOMContentLoaded", function () {
  // Initialize dashboard features
  initializeProgressCharts();
  initializeNotifications();
  initializeMobileMenu();
});

function initializeProgressCharts() {
  // Simple progress visualization without external libraries
  const progressBars = document.querySelectorAll(".progress-bar");

  progressBars.forEach((bar) => {
    const percentage = bar.dataset.percentage || 0;
    const fill = bar.querySelector(".progress-fill");

    if (fill) {
      setTimeout(() => {
        fill.style.width = percentage + "%";
      }, 100);
    }
  });
}

function initializeNotifications() {
  // Auto-hide success messages after 5 seconds
  const alerts = document.querySelectorAll(".alert");

  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      setTimeout(() => {
        alert.remove();
      }, 300);
    }, 5000);
  });
}

function initializeMobileMenu() {
  const mobileMenuButton = document.getElementById("mobile-menu-button");
  const mobileMenu = document.getElementById("mobile-menu");

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
    });
  }
}

// Utility functions for AJAX requests
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Progress logging functionality
function logProgress(formData) {
  const csrftoken = getCookie("csrftoken");

  fetch("/client/progress/log/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        showNotification("Progress logged successfully!", "success");
        location.reload();
      } else {
        showNotification("Error logging progress", "error");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification("Error logging progress", "error");
    });
}

function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `fixed top-4 right-4 p-4 rounded-md shadow-lg z-50 ${
    type === "success"
      ? "bg-green-500 text-white"
      : type === "error"
      ? "bg-red-500 text-white"
      : "bg-blue-500 text-white"
  }`;
  notification.textContent = message;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.opacity = "0";
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

function renderWeightChart(chartId, labels, data) {
  console.log(chartId, labels, data);
  const ctx = document.getElementById(chartId);
  if (!ctx) return; // Exit if canvas not found

  new Chart(ctx.getContext("2d"), {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Weight (kg)",
          data: data,
          borderColor: "#10B981", // Tailwind green-500
          backgroundColor: "rgba(16,185,129,0.2)",
          tension: 0.3,
          fill: true,
          pointRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true },
      },
      scales: {
        y: { beginAtZero: false },
        x: { ticks: { color: "#374151" } }, // Tailwind gray-700
      },
    },
  });
}

// Function to render a generic progress bar (optional)
function updateProgressBar(barId, percentage) {
  const bar = document.getElementById(barId);
  if (bar) bar.style.width = percentage + "%";
}

// dashboard.js

// document.addEventListener("DOMContentLoaded", function () {
//   const daysContainer = document.getElementById("days-container");
//   const addDayBtn = document.getElementById("add-day-btn");
//   const workoutInput = document.getElementById("id_workout_structure");
//   const workoutBuilder = document.getElementById("workout-builder");
  
//   function updateWorkoutJSON() {
//     const workoutData = [];
//     daysContainer.querySelectorAll(".day-block").forEach(dayBlock => {
//       const dayName = dayBlock.querySelector(".day-name").value;
//       const exercises = [];
//       dayBlock.querySelectorAll(".exercise-block").forEach(exBlock => {
//         const name = exBlock.querySelector(".exercise-name").value;
//         const sets = exBlock.querySelector(".exercise-sets").value;
//         const reps = exBlock.querySelector(".exercise-reps").value;
//         if(name) exercises.push({name, sets: parseInt(sets), reps: parseInt(reps)});
//       });
//       if(dayName) workoutData.push({day: dayName, exercises});
//     });
//     workoutInput.value = JSON.stringify(workoutData);
//   }

//   function addExercise(dayBlock, ex = {name: "", sets: "", reps: ""}) {
//     const exerciseBlock = document.createElement("div");
//     exerciseBlock.className =
//       "exercise-block max-md:grid flex max-md:grid-cols-2  max-sm:grid-cols-1 gap-2  mt-2 ";
//     exerciseBlock.innerHTML = `
//       <input type="text" placeholder="Exercise Name" class="exercise-name flex-1 border px-3 py-2 rounded-md focus:ring-2 focus:ring-primary-400" value="${ex.name}" required>
//       <input type="number" placeholder="Sets" class="exercise-sets w-20 border px-2 py-2 rounded-md focus:ring-2 focus:ring-primary-400" min="1" value="${ex.sets}" required>
//       <input type="number" placeholder="Reps" class="exercise-reps w-20 border px-2 py-2 rounded-md focus:ring-2 focus:ring-primary-400" min="1" value="${ex.reps}" required>
//       <button type="button" class="remove-exercise bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md font-semibold transition">Remove</button>
//     `;
//     exerciseBlock.querySelector(".remove-exercise").addEventListener("click", () => {
//       exerciseBlock.remove();
//       updateWorkoutJSON();
//     });
//     dayBlock.querySelector(".exercises-container").appendChild(exerciseBlock);
//     exerciseBlock.querySelectorAll("input").forEach(input => input.addEventListener("input", updateWorkoutJSON));
//   }

//   function addDay(dayName = "", exercises = []) {
//     const dayBlock = document.createElement("div");
//     dayBlock.className = "day-block border border-primary-200 p-4 rounded-xl bg-primary-50 shadow-sm space-y-3";
//     dayBlock.innerHTML = `
//       <div class="flex max-md:flex-col justify-center gap-2 items-center max-md:items-start">
//         <input type="text" placeholder="Day Name (e.g., Monday)" class="day-name flex-1 border px-3 py-2 rounded-md focus:ring-2 focus:ring-primary-400" value="${dayName}" required>
//         <button type="button" class="add-exercise-btn bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded-md font-semibold transition">+ Exercise</button>
//         <button type="button" class="remove-day-btn bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md font-semibold transition">Remove Day</button>
//       </div>
//       <div class="exercises-container space-y-2"></div>
//     `;
//     dayBlock.querySelector(".add-exercise-btn").addEventListener("click", () => addExercise(dayBlock));
//     dayBlock.querySelector(".remove-day-btn").addEventListener("click", () => {
//       dayBlock.remove();
//       updateWorkoutJSON();
//     });
//     dayBlock.querySelector(".day-name").addEventListener("input", updateWorkoutJSON);
//     daysContainer.appendChild(dayBlock);
//     exercises.forEach(ex => addExercise(dayBlock, ex));
//     updateWorkoutJSON();
//   }

//   addDayBtn.addEventListener("click", () => addDay());
//   console.log(workoutBuilder.dataset.workout)

//   // Prefill if editing
//  const workoutDataTag = document.getElementById("workoutData");
// if (workoutDataTag) {
//   const existingWorkout = JSON.parse(workoutDataTag.textContent);
//   existingWorkout.forEach(day => addDay(day.day, day.exercises));
// } else {
//   addDay(); // default for create
// }


//   document.querySelector("form").addEventListener("submit", () => updateWorkoutJSON());
// });

//Nutrition Js

document.addEventListener("DOMContentLoaded", () => {
    // Toggle collapsible days
    document.querySelectorAll(".day-toggle").forEach(btn => {
        btn.addEventListener("click", () => {
            const content = btn.nextElementSibling;
            content.classList.toggle("hidden");
            btn.querySelector("svg").classList.toggle("rotate-180");
        });
    });

    // Add food handler
    document.querySelectorAll(".add-food-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const foodsList = btn.closest(".meal-section").querySelector(".foods-list");
            const template = foodsList.querySelector(".food-item.template");
            const clone = template.cloneNode(true);
            clone.classList.remove("hidden", "template");
            foodsList.appendChild(clone);

            // Remove food handler
            clone.querySelector(".remove-food-btn").addEventListener("click", () => {
                clone.remove();
            });

            // Live search handler
            const input = clone.querySelector(".food-search");
            const suggestions = clone.querySelector(".food-suggestions");

            input.addEventListener("input", () => {
                const query = input.value.trim();
                if (query.length < 2) {
                    suggestions.classList.add("hidden");
                    return;
                }
                fetch(`/nutrition/search-foods/?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        suggestions.innerHTML = "";
                        if (data.length === 0) {
                            suggestions.innerHTML = `<li class="px-3 py-2 z-50 text-sm text-gray-500 cursor-pointer">No results. Press Enter to add.</li>`;
                        } else {
                            data.forEach(food => {
                                const li = document.createElement("li");
                                li.textContent = `${food.name} (${food.calories} kcal)`;
                                li.dataset.id = food.id;
                                li.className = "px-3 py-2 text-sm hover:bg-primary-50 cursor-pointer z-50";
                                li.addEventListener("click", () => {
                                    input.value = food.name;
                                    suggestions.classList.add("hidden");
                                });
                                suggestions.appendChild(li);
                            });
                        }
                        suggestions.classList.remove("hidden");
                    });
            });
        });
    });

    
    // --- Collect Meal Structure ---
  
});





