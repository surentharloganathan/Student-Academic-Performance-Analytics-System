
const studentForm = document.getElementById("studentForm");

studentForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const studentData = {
        name: document.getElementById("name").value.trim(),
        register_number: document.getElementById("register_number").value.trim(),
        department: document.getElementById("department").value.trim()
    };

    const message = document.getElementById("message");

    console.log("Submitting student:", studentData);

    try {
        const response = await fetch("/students/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(studentData)
        });

        const result = await response.json();

        console.log("Server response:", response.status, result);

        if (!response.ok) {
            message.textContent = result.error || "Unable to add student.";
            return;
        }

        message.textContent = "Student added successfully!";

        studentForm.reset();

        setTimeout(() => {
            window.location.reload();
        }, 700);

    } catch (error) {
        console.error("Submission error:", error);
        message.textContent = "Server connection failed.";
    }
});


// DELETE STUDENT
window.deleteStudent = async function(id) {

    const confirmed = confirm(
        "Are you sure you want to delete this student? Associated marks may also be deleted."
    );

    if (!confirmed) return;

    try {
        const response = await fetch(`/students/${id}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Unable to delete student.");
            return;
        }

        alert("Student deleted successfully!");
        window.location.reload();

    } catch (error) {
        alert("Server connection failed.");
        console.error(error);
    }
};


window.editStudent = async function(
    id, oldName, oldRegister, oldDepartment
) {
    const name = prompt("Enter student name:", oldName);
    if (name === null) return;

    const registerNumber = prompt(
        "Enter register number:", oldRegister
    );
    if (registerNumber === null) return;

    const department = prompt(
        "Enter department:", oldDepartment
    );
    if (department === null) return;

    const data = {
        name: name.trim(),
        register_number: registerNumber.trim(),
        department: department.trim()
    };

    if (!data.name || !data.register_number || !data.department) {
        alert("All fields are required.");
        return;
    }

    try {
        const response = await fetch(`/students/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            alert(result.error || "Unable to update student.");
            return;
        }

        alert("Student updated successfully!");
        window.location.reload();

    } catch (error) {
        alert("Server connection failed.");
        console.error(error);
    }
};


// Handle Edit and Delete buttons
document.getElementById("studentTable").addEventListener("click", function(event) {

    const button = event.target;

    // EDIT
    if (button.classList.contains("edit-btn")) {

        const id = button.dataset.id;
        const name = button.dataset.name;
        const register = button.dataset.register;
        const department = button.dataset.department;

        editStudent(id, name, register, department);
    }

    // DELETE
    if (button.classList.contains("delete-btn")) {

        const id = button.dataset.id;

        deleteStudent(id);
    }
});

// SORT STUDENTS
const studentSort = document.getElementById("studentSort");

studentSort.addEventListener("change", function () {

    const table = document.getElementById("studentTable");
    const rows = Array.from(table.querySelectorAll("tr"));

    // Ignore the "No students added yet" row
    const dataRows = rows.filter(row => row.cells.length === 5);

    const sortType = studentSort.value;

    if (sortType === "name") {
        dataRows.sort((a, b) =>
            a.cells[1].textContent.trim().localeCompare(
                b.cells[1].textContent.trim()
            )
        );
    }

    else if (sortType === "register") {
        dataRows.sort((a, b) =>
            a.cells[2].textContent.trim().localeCompare(
                b.cells[2].textContent.trim(),
                undefined,
                { numeric: true, sensitivity: "base" }
            )
        );
    }

    else {
        // Restore default order using student ID
        dataRows.sort((a, b) =>
            Number(a.cells[0].textContent) -
            Number(b.cells[0].textContent)
        );
    }

    dataRows.forEach(row => table.appendChild(row));
});