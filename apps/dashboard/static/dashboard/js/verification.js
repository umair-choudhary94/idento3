$(document).ready(function () {
});

function initiateVerification(id) {
    let endpoint = `/verification/initiate/${id}/`;
    let button = document.getElementById("initiate_" + id.toString());
    button.classList.add('disabled');
    $.ajax({
        url: endpoint,
        type: "GET",
        dataType: "json",
        success: (jsonResponse) => {
            // Extract data from the response
            let button = document.getElementById("initiate_" + id.toString());
            let successMsg = document.createElement("span");
            successMsg.style.color = "green";
            successMsg.style.fontWeight = "bold";
            successMsg.innerHTML = "Email sent!";
            button.parentNode.replaceChild(successMsg, button);
        },
        error: (jsonResponse) => alert("Failed to call api " + endpoint + "!" + jsonResponse.data.errorMesssage + json.errorMesssage)
    });
}
