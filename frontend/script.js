// variables
let selectedFile = null;
let processedBlob = null;
let processedImageURL = null;

const input = document.getElementById("fileInput");
input.addEventListener("change", (e) => {
    selectedFile = e.target.files[0];
    const url = URL.createObjectURL(selectedFile);
    document.getElementById("originalPreview").src = url;
}
);

const container = document.querySelector(".container");
// Process image function
async function processImage() {
    // checks if user uploaded an image
    if (!selectedFile) {
        alert("Upload image first");
        return;
    }
    const status = document.getElementById("status");
    status.innerText = "Processing image...";
    const formData = new FormData();
    formData.append("image", selectedFile);
    const photoSize = document.getElementById("photoSize").value;
    formData.append("type", photoSize);
    try {
        const response =
            // response from webhook
            await fetch("http://localhost:5678/webhook-test/id-upload", {
                method: "POST",
                body: formData
            }
            );

        if (!response.ok) { throw new Error("Failed"); }
        processedBlob = await response.blob();
        processedImageURL = URL.createObjectURL(processedBlob);
        document.getElementById("outputPreview").src = processedImageURL;
        status.innerText = "Processing complete";
        generatePrintLayout();

        const processedDone = document.getElementById("process-button");
        
        processedDone.classList.add("active");
        processedDone.disabled = true;
        container.classList.add("active");
    }

    catch (error) {
        console.error(error);
        alert("Error processing image");
    }
}

// Generate Print layout function
function generatePrintLayout() {

    if (!processedImageURL) return;
    const size = document.getElementById("photoSize").value;
    const sheet = document.getElementById("printSheet");
    sheet.innerHTML = "";

    let width;
    let height;

    if (size === "1x1") {
        width = "1in";
        height = "1in";
    }

    else if (size === "1.5x1.5") {
        width = "1.5in";
        height = "1.5in";
    }

    else if (size === "2x2") {
        width = "2in";
        height = "2in";
    }

    else if (size === "passport") {
        width = "35mm";
        height = "45mm";
    }

    // Duplicate images into six copies
    for (let i = 0; i < 6; i++) {
        const img = document.createElement("img");
        img.src = processedImageURL;
        img.classList.add("print-photo");
        img.style.width = width;
        img.style.height = height;
        sheet.appendChild(img);
    }
}




function downloadImage() {
    if (!processedBlob) {
        alert("No processed image");
        return;
    }
    const url =
        URL.createObjectURL(processedBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "id-photo.png";
    a.click();
}

function printPhotos() {

    if (!processedImageURL) {
        alert("Process image first");
        return;
    }
    window.print();
}

document
    .getElementById("photoSize")
    .addEventListener("change", generatePrintLayout);


