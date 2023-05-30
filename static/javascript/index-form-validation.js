function checkforblank() {
    var location = document.getElementById('city-search');
    var invalid = location.value == "";

    if (invalid) {
        alert('Please enter city');
        location.className = 'error';
        return false;
    }
    else {
        location.className = '';
        return true;
    }


}


function checkdates() {
    var in_date_error = document.getElementById('in-date');
    var out_date_error = document.getElementById('out-date');
    var in_date = document.getElementById('in-date').value;
    var out_date = document.getElementById('out-date').value;

    if (out_date <= in_date) {
        alert('Please enter correct date');
        in_date_error.className = 'error';
        out_date_error.className = 'error';
        return false;
    }

    return true;
}


function validateForm() {
    if (!checkforblank() || !checkdates()) {
        return false;
    }
    return true;
}


