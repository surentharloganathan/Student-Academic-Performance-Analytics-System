
const subjectForm = document.getElementById("subjectForm");
const subjectTable = document.getElementById("subjectTable");
const message = document.getElementById("subjectMessage");

// LOAD SUBJECTS
async function loadSubjects() {
    try {
        const response = await fetch("/subjects/");
        const subjects = await response.json();

        if (!response.ok) {
            throw new Error(subjects.error || "Unable to load subjects.");
        }

        subjectTable.innerHTML = "";

        if (subjects.length === 0) {
            subjectTable.innerHTML = `
                <tr>
                    <td colspan="5">No subjects found.</td>
                </tr>
            `;
            return;
        }

        subjects.forEach(subject => {
            subjectTable.innerHTML += `
                <tr>
                    <td>${subject.id}</td>
                    <td>${subject.name}</td>
                    <td>${subject.max_marks}</td>
                    <td>${subject.pass_mark}</td>
                    <td>
                        <button data-action="edit" data-id="${subject.id}">Edit</button>
                        <button data-action="delete" data-id="${subject.id}">Delete</button>
                    </td>
                </tr>
            `;
        });

    } catch (error) {
        subjectTable.innerHTML = `
            <tr>
                <td colspan="5">Error loading subjects.</td>
            </tr>
        `;
        console.error(error);
    }
}

// ADD SUBJECT
subjectForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const subjectData = {
        name: document.getElementById("subjectName").value.trim(),
        max_marks: Number(document.getElementById("maxMarks").value),
        pass_mark: Number(document.getElementById("passMark").value)
    };

    try {
        const response = await fetch("/subjects/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(subjectData)
        });

        const result = await response.json();

        if (!response.ok) {
            message.textContent = result.error || "Unable to add subject.";
            return;
        }

        message.textContent = "Subject added successfully!";
        subjectForm.reset();

        document.getElementById("maxMarks").value = 100;
        document.getElementById("passMark").value = 40;

        loadSubjects();

    } catch (error) {
        message.textContent = "Server connection failed.";
        console.error(error);
    }
});

// EDIT AND DELETE SUBJECTS
subjectTable.addEventListener("click", async function(event) {
    const button = event.target.closest("button[data-action]");

    if (!button) return;

    const id = button.dataset.id;
    const action = button.dataset.action;

    if (action === "edit") {
        await editSubject(id);
    } else if (action === "delete") {
        await deleteSubject(id);
    }
});

// EDIT SUBJECT
async function editSubject(id) {
    const response = await fetch("/subjects/");
    const subjects = await response.json();

    const subject = subjects.find(s => s.id === Number(id));

    if (!subject) return;

    const name = prompt("Enter subject name:", subject.name);
    if (name === null) return;

    const maxMarks = prompt("Enter maximum marks:", subject.max_marks);
    if (maxMarks === null) return;

    const passMark = prompt("Enter pass marks:", subject.pass_mark);
    if (passMark === null) return;

    const subjectData = {
        name: name.trim(),
        max_marks: Number(maxMarks),
        pass_mark: Number(passMark)
    };

    if (!subjectData.name ||
        !Number.isInteger(subjectData.max_marks) ||
        !Number.isInteger(subjectData.pass_mark) ||
        subjectData.max_marks <= 0 ||
        subjectData.pass_mark < 0 ||
        subjectData.pass_mark > subjectData.max_marks) {
        alert("Please enter valid subject details.");
        return;
    }

    try {
        const updateResponse = await fetch(`/subjects/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(subjectData)
        });

        const result = await updateResponse.json();

        if (!updateResponse.ok) {
            alert(result.error || "Unable to update subject.");
            return;
        }

        alert("Subject updated successfully!");
        loadSubjects();

    } catch (error) {
        alert("Server connection failed.");
        console.error(error);
    }
}

// DELETE SUBJECT
async function deleteSubject(id) {
    const confirmed = confirm(
        "Are you sure you want to delete this subject?"
    );

    if (!confirmed) return;

    try {
        const response = await fetch(`/subjects/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Unable to delete subject.");
            return;
        }

        alert("Subject deleted successfully!");
        loadSubjects();

    } catch (error) {
        alert("Server connection failed.");
        console.error(error);
    }
}

// INITIAL LOAD
loadSubjects();
