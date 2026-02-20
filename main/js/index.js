document.getElementById('currency').addEventListener('change', () => {
    Array.from(document.getElementById('catalog-items').getElementsByTagName("p")).forEach(element => {
        if (element.getAttribute("name") == document.getElementById('currency').value) {
            element.classList.remove("hide");
        }
        else {
            element.classList.add("hide");
        }
    });
    Array.from(document.getElementById('recommended-items').getElementsByTagName("p")).forEach(element => {
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
