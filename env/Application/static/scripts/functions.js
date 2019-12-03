var xhttp = new XMLHttpRequest();

function signup () {
    var isformvalid = true;
    var data = new FormData();
    var confirm_error_section = document.getElementById('password-confirm-error');
    var password_error_paragraph = document.getElementById('password-match-error');
    var firstname = document.getElementById('firstname-field').value.trim();
    var lastname = document.getElementById('lastname-field').value.trim();
    var username = document.getElementById('username-field').value.trim();
    var password = document.getElementById('password-field').value;
    var password_confirm = document.getElementById('confirm-password-field').value;
    var username_error_section = document.getElementById('username-error-section');
    var username_error_paragraph = document.getElementById ('username-error');
    if (firstname == '' || firstname == ' ') {
        isformvalid = false;
    }

    if (lastname == '' || lastname == ' ') {
        isformvalid = false;
    }

    if (username == '' || username == ' ') {
        isformvalild = false;
    }

    if (password == '') {
        isformvalid = false;
    }

    if (password_confirm == '') {
        isformvalid = false;
    }

    if (isformvalid == false) {
        alert('Please fill out the entire form');
    }
    else {
        if(password === password_confirm) {
            data.append('firstname', firstname);
            data.append('lastname', lastname);
            data.append('username', username);
            data.append('password', password);

            xhttp.onreadystatechange = function() {
                if (this.readyState == 4 && this.status == 200) {
                    username_error_section.style.display = 'none';
                    document.getElementById('firstname-field').value = '';
                    document.getElementById('lastname-field').value = '';
                    document.getElementById('username-field').value = '';
                    document.getElementById('password-field').value = '';
                    document.getElementById('confirm-password-field').value = '';
                    $('#toggle-button').click();
                }
                
                if (this.readyState == 4 && this.status == 500) {
                    username_error_paragraph.innerHTML = JSON.parse(this.responseText).message;
                    username_error_section.style.display = 'block';
                }
            };   
            
            xhttp.open('POST', '/user_create', true);
            xhttp.send(data);
            confirm_error_section.style.display = 'none';     
        }
        else {
            password_error_paragraph.innerHTML = 'Password did not match';
            confirm_error_section.style.display = 'block';
        }
        
    }
}

function login() {
    var username = document.getElementById('login-username');
    var password = document.getElementById('login-password');
    var login_error_section = document.getElementById('login-error-section');
    var login_error_paragrah = document.getElementById('login-error-paragraph');
    var data = new FormData();
    data.append('username', username.value);
    data.append('password', password.value);

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            login_error_paragrah.style.display = 'none';
            window.location.href = JSON.parse(this.responseText).path;
        }

        if (this.readyState == 4 && this.status == 500) {
            login_error_section.style.display = 'block';
            login_error_paragrah.innerHTML = JSON.parse(this.responseText).message;
        }
    }
    xhttp.open('POST', '/user_login', true);
    xhttp.send(data);
}