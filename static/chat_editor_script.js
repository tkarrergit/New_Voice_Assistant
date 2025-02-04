document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("entry-form");
    
    const entrySelector = document.getElementById("entry-selector");
    const deleteButton = document.getElementById("delete-button");
    // Service Worker registrieren für webapp ohne browser fenster
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('service-worker.js');
      }

    // Neue Daten speichern
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {};
        new FormData(form).forEach((value, key) => {
            data[key] = value;
        });

        const response = await fetch("/api/entries", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            form.reset();
            loadEntries();
        } else {
            alert("Failed to save entry.");
        }
    });

    // Einträge laden
    async function loadEntries() {
        const response = await fetch("/api/entries");
        if (!response.ok) {
            console.error("Failed to fetch entries");
            return;
        }
        const entries = await response.json();
    
        // Dropdown aktualisieren
        entrySelector.innerHTML = `<option value="" disabled selected>Select an entry</option>`;
        entries.forEach((entry) => {
            const [id, name] = entry; // ID und Name extrahieren
            const option = document.createElement("option");
            option.value = id;
            option.textContent = `${id}: ${name}`;
            entrySelector.appendChild(option);
        });
    }

    // Datensatz auswählen und laden
    entrySelector.addEventListener("change", async () => {
        const entryId = entrySelector.value;

        if (!entryId) {
            alert("Please select an entry.");
            return;
        }

        const response = await fetch(`/api/entry/${entryId}`);
        if (response.ok) {
            const entry = await response.json();
            const [id, ...values] = entry;

            // ID in das ID-Feld im Formular laden
            document.getElementById("id").value = id;

            // Formularfelder mit den Werten füllen
            const formData = new FormData(form);
            Array.from(formData.keys()).forEach((key, index) => {
                const inputField = document.getElementById(key);
                if (inputField && key !== "id") {  // ID nicht überschreiben
                    inputField.value = values[index - 1] || ""; // Index -1, da ID nicht im Formular ist
                }
            });
        } else {
            alert("Failed to load the entry.");
        }
    });

    // Eintrag löschen
    deleteButton.addEventListener("click", async () => {
        const entryId = entrySelector.value;
    
        if (!entryId) {
            alert("Please select an entry to delete.");
            return;
        }
    
        const response = await fetch(`/api/entry/${entryId}`, {
            method: "DELETE",
        });
    
        if (response.ok) {
            alert("Entry deleted successfully.");
            console.log(`Deleted entry with ID: ${entryId}`);
            
            console.log("Reloading entries...");
            await loadEntries(); // Warte, bis die Einträge neu geladen wurden
    
            // Debugging: Kontrolliere, welche Daten nach dem Löschen geladen werden
            const debugResponse = await fetch("/api/entries");
            const debugEntries = await debugResponse.json();
            console.log("Entries after delete:", debugEntries);
        } else {
            alert("Failed to delete entry.");
        }
    });
    

    loadEntries();
});
