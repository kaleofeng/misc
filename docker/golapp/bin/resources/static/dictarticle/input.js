function setupMain() {
    console.log('dictarticle', 'setup main');

    setupPage();
}

function setupPage() {
    console.log('dictarticle', 'setup page');

    //registerSubmitButtonEventListener();
}

function registerSubmitButtonEventListener() {
    $('#btn_submit').click(function () {
        const title = $('#txt_article_title').prop('value').trim();
        const content = $('#txt_article_content').prop('value').trim();

        const data = {
            title: title,
            content: content,
        };

        console.log('dictarticle', 'on submit', data);

        $.ajax({
            url: '#',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            dataType: 'json',
            beforeSend: function (xhr) {
                $('#btn_submit').attr('disabled', true);
            },
            success: function (rsp) {
                console.log('dictarticle', 'on submit', 'ajax success', rsp);

                $('#btn_submit').attr('disabled', false);

                if (rsp.code !== ResultSuccess) {
                    return;
                }
            },
            error: function (xhr, err, ex) {
                console.log('dictarticle', 'on submit', 'ajax error', err, ex);
            }
        });
    });
}
