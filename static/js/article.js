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
        .then(data => console.log('閲覧履歴保存', data))
        .catch(err => console.error(err));
}

function initTrackLinks() {
    document.querySelectorAll('.track-link').forEach(link => {
        link.addEventListener('click', function (e) {
            const articleUrl = this.href;
            const articleTitle = this.dataset.title || this.textContent;
            trackArticle(articleTitle, articleUrl);
        });
    });
}

function initFavoriteButtons() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEvebtListener('click', async function (e) {
            e.preventDefault();
            const articleId = this.dataset.id;
            const csrftoken = getCookie('csrftoken');

            const response = await fetch('/toggle_favorite/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({ article_id: articleId })
            });

            const data = await response.json();
            if (data.status === 'added') {
                this.classList.add('active');
                this.textContent = '💔';
            } else if (data.status === 'removed') {
                this.classList.remove('active');
                this.textContent = '❤';
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initTrackLinks();
    initFavoriteButtons();
});