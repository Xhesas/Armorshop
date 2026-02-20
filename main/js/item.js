try{
    document.getElementById('currency').addEventListener('change', () => {
        Array.from(document.getElementById('additions').getElementsByTagName("p")).forEach(element => {
            if (element.getAttribute("name") == document.getElementById('currency').value) {
                element.classList.remove("hide");
            }
            else {
                element.classList.add("hide");
            }
        });
    });

    document.getElementById('currency').value = "glanga";
    document.getElementById('currency').dispatchEvent(new Event("change", { bubbles: true }));
}
catch {}

async function openForm() {
    const closeFormButton = document.getElementById("closeFormButton");
    const purchaseForm = document.getElementById("purchaseForm");
    const purchaseFormElement = document.getElementById("purchaseFormElement");
    const shipment = document.getElementById("shipment");
    const pickup = document.getElementById("pickup");
    const addressContainer = document.getElementById("address-container");
    const address = document.getElementById("address");
    const dateContainer = document.getElementById("date-container");
    const date = document.getElementById("date");

    closeFormButton.addEventListener("click", () => {
        purchaseForm.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === purchaseForm) {
            purchaseForm.style.display = "none";
        }
    });

    try {
        date.min = new Date().toISOString();

        shipment.onclick = function() {
            addressContainer.style.display = "";
            address.required = true;
            dateContainer.style.display = "none";
            date.required = false;
        }
        pickup.onclick = function() {
            addressContainer.style.display = "none";
            address.required = false;
            dateContainer.style.display = "";
            date.required = true;
        }

        purchaseForm.style.display = "flex";
    } catch (error) {
        console.error('Error loading item details:', error);
        purchaseForm.style.display = "none";
    }
}
