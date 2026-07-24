const dateInput = document.getElementById("id_new_lesson-date");
const durationInput = document.getElementById("id_new_lesson-duration");
const statusInput = document.getElementById("id_new_lesson-status");
const noteInput = document.getElementById("id_new_lesson-note");
const homeworksInput = document.getElementById("id_new_lesson-homeworks");
const reminderInput = document.getElementById("id_new_lesson-reminder");
const notesInput = document.getElementById("id_new_lesson-notes");
const commentInput = document.getElementById("id_new_lesson-comment");

function checkDate(event) {
    console.log("check");
    const date = Date.parse(dateInput.value);
    if (Date.now() < date) {
        statusInput.value = 'planned';
        notesInput.parentElement.classList.add("d-none");
        commentInput.parentElement.classList.add("d-none");
        homeworksInput.parentElement.classList.remove("d-none");
        reminderInput.parentElement.classList.remove("d-none");
        noteInput.parentElement.classList.add("d-none");
    } else {
        statusInput.value = 'done';
        homeworksInput.parentElement.classList.add("d-none");
        reminderInput.parentElement.classList.add("d-none");
        notesInput.parentElement.classList.remove("d-none");
        commentInput.parentElement.classList.remove("d-none");
        noteInput.parentElement.classList.remove("d-none");
    }
}

function getAllData() {
    console.log(commentInput);
}

document.addEventListener('DOMContentLoaded', getAllData);
document.addEventListener('DOMContentLoaded', checkDate);
dateInput.addEventListener('change', checkDate);