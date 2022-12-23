document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.color-btn').forEach(button => {
        button.onclick = function() {
            document.querySelector('body').style.fontWeight = button.dataset.font_weight;
        }
    })
})