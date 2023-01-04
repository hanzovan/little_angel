document.addEventListener('DOMContentLoaded', function() {
    const show_register_btn = document.querySelector('#show_course_register');
    const hide_register_btn = document.querySelector('#hide_course_register');
    const register_form = document.querySelector('#register-course');
    const show_quit_btn = document.querySelector('#show_course_quit');
    const hide_quit_btn = document.querySelector('#hide_course_quit');
    const quit_form = document.querySelector('#quit-course');

    // By default the form and the hide btn was hide
    register_form.style.display = 'none';
    hide_register_btn.style.display = 'none';
    quit_form.style.display = 'none';
    hide_quit_btn.style.display = 'none';


    // If user click show btn, show the form, or vice versa for hide btn
    show_register_btn.onclick = function() {
        register_form.style.display = 'block';
        hide_register_btn.style.display = 'block';
        show_register_btn.style.display = 'none';
    }
    hide_register_btn.onclick = function() {
        register_form.style.display = 'none';
        show_register_btn.style.display = 'block';
        hide_register_btn.style.display = 'none';
    }
    show_quit_btn.onclick = function() {
        quit_form.style.display = 'block';
        hide_quit_btn.style.display = 'block';
        show_quit_btn.style.display = 'none';
    }
    hide_quit_btn.onclick = function() {
        quit_form.style.display = 'none';
        hide_quit_btn.style.display = 'none';
        show_quit_btn.style.display = 'block';
    }
})