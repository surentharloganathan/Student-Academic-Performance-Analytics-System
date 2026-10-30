
document.addEventListener("DOMContentLoaded", function () {
    const studentCanvas = document.getElementById("studentChart");
    const subjectCanvas = document.getElementById("subjectChart");

    const studentDataElement = document.getElementById("student-chart-data");
    const subjectDataElement = document.getElementById("subject-chart-data");

    // Stop early if required HTML elements are missing.
    if (
        !studentCanvas ||
        !subjectCanvas ||
        !studentDataElement ||
        !subjectDataElement
    ) {
        console.error(
            "Dashboard chart elements are missing. Check dashboard.html IDs."
        );
        return;
    }

    if (typeof Chart === "undefined") {
        console.error("Chart.js has not loaded.");
        return;
    }

    let studentData;
    let subjectData;

    try {
        studentData = JSON.parse(studentDataElement.textContent);
        subjectData = JSON.parse(subjectDataElement.textContent);
    } catch (error) {
        console.error("Unable to parse chart data:", error);
        return;
    }

    new Chart(studentCanvas, {
        type: "bar",
        data: {
            labels: studentData.map(item => item.name),
            datasets: [{
                label: "Percentage (%)",
                data: studentData.map(item => item.percentage)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });

    new Chart(subjectCanvas, {
        type: "bar",
        data: {
            labels: subjectData.map(item => item.name),
            datasets: [{
                label: "Pass Percentage (%)",
                data: subjectData.map(item => item.percentage)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
});
