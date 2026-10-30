
const marksForm = document.getElementById("marksForm");
const studentSelect = document.getElementById("studentId");
const subjectSelect = document.getElementById("subjectId");
const scoreInput = document.getElementById("score");
const marksLimit = document.getElementById("marksLimit");
const marksMessage = document.getElementById("marksMessage");
const marksTable = document.getElementById("marksTable");

// Filter dropdowns
const studentFilter = document.getElementById("studentFilter");
const subjectFilter = document.getElementById("subjectFilter");

// Store all marks
let allMarks = [];

// Load students into dropdowns
async function loadStudents() {
    const response = await fetch("/students/");
    const students = await response.json();

    studentSelect.innerHTML = '<option value="">Select Student</option>';
    studentFilter.innerHTML = '<option value="">All Students</option>';

    students.forEach(student => {
        // Add student to Assign Marks dropdown
        const option = document.createElement("option");
        option.value = student.id;
        option.textContent =
            `${student.name} (${student.register_number})`;
        studentSelect.appendChild(option);

        // Add student to Filter dropdown
        const filterOption = document.createElement("option");
        filterOption.value = student.name;
        filterOption.textContent =
            `${student.name} (${student.register_number})`;
        studentFilter.appendChild(filterOption);
    });
}

// Load subjects into dropdowns
async function loadSubjects() {
    const response = await fetch("/subjects/");

    if (!response.ok) {
        throw new Error(`Subjects API failed: ${response.status}`);
    }

    const subjects = await response.json();

    subjectSelect.innerHTML = '<option value="">Select Subject</option>';
    subjectFilter.innerHTML = '<option value="">All Subjects</option>';

    subjects.forEach(subject => {
        const option = document.createElement("option");
        option.value = subject.id;
        option.textContent =
            `${subject.name} (Max: ${subject.max_marks})`;
        option.dataset.maxMarks = subject.max_marks;
        subjectSelect.appendChild(option);

        const filterOption = document.createElement("option");
        filterOption.value = subject.name;
        filterOption.textContent = subject.name;
        subjectFilter.appendChild(filterOption);
    });
}

// Show maximum marks for selected subject
subjectSelect.addEventListener("change", function () {
    const selected = subjectSelect.selectedOptions[0];

    if (!selected.value) {
        marksLimit.textContent = "";
        scoreInput.removeAttribute("max");
        return;
    }

    const max = Number(selected.dataset.maxMarks);

    marksLimit.textContent = `Maximum allowed marks: ${max}`;
    scoreInput.max = max;
});

// Display marks in table
function displayMarks(marks) {
    marksTable.innerHTML = "";

    if (marks.length === 0) {
        marksTable.innerHTML =
            '<tr><td colspan="7">No matching marks found.</td></tr>';
        return;
    }

    marks.forEach(mark => {
        const row = document.createElement("tr");

        const values = [
            mark.id,
            mark.student_name,
            mark.subject_name,
            mark.score,
            mark.max_marks,
            mark.pass_mark
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        const actionCell = document.createElement("td");

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => {
            editMark(mark.id, mark.score, mark.max_marks);
        });

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => {
            deleteMark(mark.id);
        });

        actionCell.append(editButton, deleteButton);
        row.appendChild(actionCell);

        marksTable.appendChild(row);
    });
}

// Apply student-wise and subject-wise filters
function applyFilters() {
    const selectedStudent = studentFilter.value;
    const selectedSubject = subjectFilter.value;

    const filteredMarks = allMarks.filter(mark => {

        const studentMatches =
            !selectedStudent ||
            mark.student_name === selectedStudent;

        const subjectMatches =
            !selectedSubject ||
            mark.subject_name === selectedSubject;

        return studentMatches && subjectMatches;
    });

    displayMarks(filteredMarks);
}

// Load all marks from backend
async function loadMarks() {
    try {
        const response = await fetch("/marks/");
        const marks = await response.json();

        if (!response.ok) {
            throw new Error("Unable to load marks");
        }

        allMarks = marks;

        // Apply currently selected filters
        applyFilters();

    } catch (error) {
        marksTable.innerHTML =
            '<tr><td colspan="7">Failed to load marks.</td></tr>';
        console.error(error);
    }
}

// Filter event listeners
studentFilter.addEventListener("change", applyFilters);
subjectFilter.addEventListener("change", applyFilters);

// Add marks
marksForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const markData = {
        student_id: Number(studentSelect.value),
        subject_id: Number(subjectSelect.value),
        score: Number(scoreInput.value)
    };

    try {
        const response = await fetch("/marks/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(markData)
        });

        const result = await response.json();

        if (!response.ok) {
            marksMessage.textContent =
                result.error || "Unable to assign marks.";
            return;
        }

        marksMessage.textContent = "Marks assigned successfully!";
        marksForm.reset();
        marksLimit.textContent = "";
        scoreInput.removeAttribute("max");

        await loadMarks();

    } catch (error) {
        marksMessage.textContent = "Server connection failed.";
        console.error(error);
    }
});

// Edit marks
async function editMark(id, oldScore, maxMarks) {
    const newScore = prompt(
        `Enter updated marks (0 to ${maxMarks}):`,
        oldScore
    );

    if (newScore === null) return;

    if (newScore.trim() === "") {
        alert("Please enter a score.");
        return;
    }

    const score = Number(newScore);

    if (!Number.isFinite(score) || score < 0 || score > maxMarks) {
        alert(`Score must be between 0 and ${maxMarks}.`);
        return;
    }

    try {
        const response = await fetch(`/marks/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ score })
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Unable to update marks.");
            return;
        }

        alert("Marks updated successfully!");
        await loadMarks();

    } catch (error) {
        alert("Server connection failed.");
        console.error(error);
    }
}

// Delete marks
async function deleteMark(id) {
    if (!confirm("Are you sure you want to delete this mark record?")) {
        return;
    }

    try {
        const response = await fetch(`/marks/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Unable to delete marks.");
            return;
        }

        alert("Marks deleted successfully!");
        await loadMarks();

    } catch (error) {
        alert("Server connection failed.");
        console.error(error);
    }
}

// Initialize page
async function initializeMarksPage() {
    try {
        await Promise.all([
            loadStudents(),
            loadSubjects()
        ]);

        await loadMarks();

    } catch (error) {
        marksMessage.textContent =
            "Unable to load students or subjects. Check the server.";
        console.error(error);
    }
}

initializeMarksPage();
