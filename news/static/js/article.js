function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name + '='))
        ?.split('=')[1];
    return cookieValue;
}

function trackArticle(link, title) {
    fetch('/track_article/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ link: link, title: title })
    })
        .then(response => response.json())
        .then(data => console.log(data));
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.article-link').forEach(a => {
        a.addEventListener('click', (e) => {
            const link = a.href;
            const title = a.dataset.title;
            trackArticle(link, title);
        });
    });
});