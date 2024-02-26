let countrySelected = $('#id_default_country').val();
if(!countrySelected) {
    $('#id_default_country').css('color', 'rgb(205, 178, 149)');
};
$('#id_default_country').change(function() {
    countrySelected = $(this).val();
    if(!countrySelected) {
        $(this).css('color', 'rgb(205, 178, 149)');
    } else {
        $(this).css('color', 'rgb(103, 88, 70)');
    }
});

