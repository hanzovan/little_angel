document.addEventListener('DOMContentLoaded', function() {
    
    const show_btn = document.querySelector('#showForm');
    const hide_btn = document.querySelector('#hideForm');
    const learn_form = document.querySelector('#learn-course');
    const show_detail_btn = document.querySelector('#show_kid_detail');
    const hide_detail_btn = document.querySelector('#hide_kid_detail');
    const kid_detail = document.querySelector('#kid_detail');

    // By default the form is hidden
    learn_form.style.display = 'none';
    kid_detail.style.display = 'none';
    
    // The hide button is also hidden
    hide_btn.style.display = 'none';
    hide_detail_btn.style.display = 'none';

    // When show button is clicked, show the form, hide the show button, show the hide button
    show_btn.onclick = function() {
        learn_form.style.display = 'block';
        show_btn.style.display = 'none';
        hide_btn.style.display = 'block';
    }
    show_detail_btn.onclick = function() {
        kid_detail.style.display = 'block';
        show_detail_btn.style.display = 'none';
        hide_detail_btn.style.display = 'block';
    }

    // When hide button was click, show the show button, hide the form and the hide button
    hide_btn.onclick = function() {
        learn_form.style.display = 'none';
        show_btn.style.display = 'block';
        hide_btn.style.display = 'none';
    }
    hide_detail_btn.onclick = function() {
        kid_detail.style.display = 'none';
        hide_detail_btn.style.display = 'none';
        show_detail_btn.style.display = 'block';
    }

    // Every time user visit this page set the default rate to USD
    localStorage.setItem('rate', 1);

    // The website provide the exchange rate
    const exchange_rate_source = 'https://api.exchangerate.host/latest?base=USD';

    // Every time user select another currency, do this action
    document.querySelector('#currency').onchange = function() {
        // Get the API from exchange rate page
        fetch(exchange_rate_source)
        
        // Turn the response to json
        .then(response => response.json())

        // Use the data
        .then(data => {
            // Get the rate from website
            const rate = data.rates[this.value];

            // Get the rate from previous selected option
            const old_rate = localStorage.getItem('rate');

            // Get the total cost ammount, multiply it for rate and divided it for the old rate
            let cost_default = parseFloat(document.querySelector('#total_cost').innerHTML);
            document.querySelector('#total_cost').innerHTML = (cost_default * rate/old_rate).toFixed(0);

            // Change the currency to the choice user made
            document.querySelector('#cost-currency').innerHTML = this.value;

            // Record the last rate
            localStorage.setItem('rate', rate);
        })
        .catch(error => {
            console.log('Error', error);
        })
    }

})