function setupMain() {
    console.log('dictarticle', 'setup main');

    setupPage();
}

function setupPage() {
    console.log('dictarticle', 'setup page');

    registerSpanEventListener();
}

function registerSpanEventListener() {
    $('span').on('click', (evt) => {
        const url = `https://cn.bing.com/dict/search?q=${evt.target.innerText}`;
        window.open(url, '_self', 'width=600,height=800');
    });
}
