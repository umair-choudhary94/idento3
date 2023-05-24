$(document).ready(function () {
    // alert("Sanity check!");
    fetch("/payments/config/")
        .then((result) => {
            return result.json();
        })
        .then((data) => {
            // Initialize Stripe.js
            const stripe = Stripe(data.publicKey);

            // new
            // Event handler
            document.querySelector("#submitBtn").addEventListener("click", () => {
                // Get Checkout Session ID
                fetch("/payments/create-checkout-session/")
                    .then((result) => {
                        return result.json();
                    })
                    .then((data) => {
                        alert(data);
                        alert(data.sessionId);
                        alert(sessionId);
                        // Redirect to Stripe Checkout
                        return stripe.redirectToCheckout({sessionId: data.sessionId})
                    })
                    .then((res) => {
                        alert(res);
                    });
            });
        });
});

