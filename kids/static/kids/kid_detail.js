document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.color-btn').forEach(button => {
        button.onclick = function() {
            document.querySelector('body').style.fontWeight = button.dataset.font_weight;
        }
    })
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