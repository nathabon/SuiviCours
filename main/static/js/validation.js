const studentSelect = document.getElementById("id_student");
const dateSelect = document.getElementById('id_date')


async function loadChaptersForStudent() {
    const chapterSelect = document.getElementById("id_chapter");

    const studentId = studentSelect.value;

    chapterSelect.innerHTML = '<option value="">---------</option>';

    if (!studentId) {
        return;
    }

    try {

        const response = await fetch(`/api/student/${studentId}/chapters/`);

        if (!response.ok) {
            throw new Error("Erreur lors du chargement des chapitres");
        }

        const chapters = await response.json();

        chapters.forEach(chapter => {
            const option = document.createElement("option");
            option.value = chapter.id;
            option.textContent = chapter.title;
            chapterSelect.appendChild(option);
        });

    } catch (error) {
        console.error(error);
    }
}

async function getDefaultPriceForStudent() {
    const priceSelect = document.getElementById("id_price");

    const studentId = studentSelect.value;

    if (!studentId) {
        console.log('no student')
        return;
    }

    try {

        const response = await fetch(`/api/student/${studentId}/`);
        

        if (!response.ok) {
            throw new Error("Erreur lors du chargement des info de l'étudiant");
        }

        const jsonResponse = await response.json();
        const defaultPrice = jsonResponse['default_price']

        priceSelect.value = defaultPrice

    } catch (error) {
        console.error(error);
    }

}

studentSelect.addEventListener("change", loadChaptersForStudent);
studentSelect.addEventListener("change", getDefaultPriceForStudent);