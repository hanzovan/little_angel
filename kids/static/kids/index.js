document.addEventListener('DOMContentLoaded', function() {
    // Every time user visit this page, the local storage rate turn back to 1 as the 1 USD = 1 USD
    localStorage.setItem('rate', 1);

    // The website url that provide API for the exchange rate
    const exchange_rate_source = 'https://api.exchangerate.host/latest?base=USD';

    // Every time the select was changed, action
    document.querySelector('#currency').onchange = function() {

        // Get the API from exchange rate page
        fetch(exchange_rate_source)

        // Turn the response to json format
        .then(response => response.json())

        // For the data that coming back
        .then(data => {

            // Get the rate from the option value in select dropdown choice
            const rate = data.rates[this.value];

            // Get the rate from previous selected option
            const old_rate = localStorage.getItem('rate');

            // For every line of course cost, multiply the value to the rate and divided it to the old rate (because the
            // rate was base on USD)
            document.querySelectorAll('#cost').forEach(strong => {
                let cost_default = parseFloat(strong.innerHTML);
                strong.innerHTML = (cost_default*rate/old_rate).toFixed(0);
            })

            // Change the currency symbol accordingly to the user's choice
            document.querySelectorAll('#cost-currency').forEach(strong => {
                strong.innerHTML = this.value;
            })

            // Record the last rate value
            localStorage.setItem('rate', rate);
        })
        .catch(error => {
            console.log('Error: ', error);
        })
    }
    
    document.querySelectorAll('.course-item').forEach(li => {
        li.style.display = 'none';
    })

    // Initially show 2 courses
    setTimeout(showCourse, 500);

    // Show course if user scroll to the bottom of the page, but don't allow multiple shot
    let lastfire = 0;
    let delay = 500;

    window.onscroll = function() {
        if ((Date.now() - lastfire) < delay) {
            return;
        }
        if ((window.innerHeight + scrollY) >= document.body.offsetHeight) {
            setTimeout(showCourse, 500);
        }        
        lastfire = Date.now();
    }
    
})

function showCourse() {
    let counter = 0
    const quantity = 2

    document.querySelectorAll('.course-item').forEach(li => {
        if (counter < quantity) {
            if (li.style.display == 'none') {
                li.style.display = 'block';
                counter = counter + 1;
            }
        }
    })
}