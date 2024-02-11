var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: 'rgb(205, 178, 149)',
        fontSize: '14px',
        '::placeholder': {
            color: 'rgb(205, 178, 149)'
        }
    },
    invalid: {
        color: '#000',
        iconColor: '#000'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-element');


// React to real-time validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var htmlContent = '<span class="icon" role="alert"><i class="fas fa-times"></i></span><span>' + event.error.message + '</span>';
        errorDiv.innerHTML = htmlContent;
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', async function (ev) {
    ev.preventDefault();

    // Disable card and submit button during processing
    card.update({ disabled: true });
    $('#submit-button').attr('disabled', true);

    try {
        // Confirm card payment with Stripe
        const result = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
            },
        });

        if (result.error) {
            // Display error message
            const errorDiv = document.getElementById('card-errors');
            const html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);

            // Re-enable card and submit button
            card.update({ disabled: false });
            $('#submit-button').attr('disabled', false);
        } else {
            // If payment is successful, submit the form
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    } catch (error) {
        // Handle unexpected errors
        console.error('An unexpected error occurred:', error);

        // Re-enable card and submit button
        card.update({ disabled: false });
        $('#submit-button').attr('disabled', false);
    }
});

