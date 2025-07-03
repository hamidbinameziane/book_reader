
document.addEventListener('DOMContentLoaded', () => {
    const page1 = document.getElementById('page-1');
    const page2 = document.getElementById('page-2');
    let currentPageIndex = 0;
    let totalPages = 0;
    let codeBuffer = "";

    const loadPages = () => {
        if (currentPageIndex >= 0 && currentPageIndex < totalPages) {
            page1.src = `/api/page/${currentPageIndex}`;
        } else {
            page1.src = "";
        }
        if (currentPageIndex + 1 < totalPages) {
            page2.src = `/api/page/${currentPageIndex + 1}`;
        } else {
            page2.src = "";
        }
    };

    const savePosition = () => {
        fetch('/api/position', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ page_index: currentPageIndex })
        });
    };

    const init = async () => {
        const posResponse = await fetch('/api/position');
        const posData = await posResponse.json();
        currentPageIndex = posData.page_index || 0;

        const totalResponse = await fetch('/api/total_pages');
        const totalData = await totalResponse.json();
        totalPages = totalData.total_pages;

        loadPages();
    };

    document.addEventListener('keydown', (event) => {
        switch (event.key) {
            case 'ArrowUp':
                if (currentPageIndex - 2 >= 0) {
                    currentPageIndex -= 2;
                    loadPages();
                    savePosition();
                }
                break;
            case 'ArrowDown':
                if (currentPageIndex + 2 < totalPages) {
                    currentPageIndex += 2;
                    loadPages();
                    savePosition();
                }
                break;
            case 'Escape':
                // Fullscreen exit is handled by the browser
                break;
        }

        if (event.key >= '0' && event.key <= '9') {
            codeBuffer += event.key;
            if (codeBuffer.length === 4) {
                const targetPage = parseInt(codeBuffer, 10);
                if (targetPage > 0 && targetPage <= totalPages) {
                    currentPageIndex = targetPage - 1;
                    loadPages();
                    savePosition();
                }
                codeBuffer = "";
            }
        }
    });

    // Request fullscreen on user gesture
    document.body.addEventListener('click', () => {
        if (document.body.requestFullscreen) {
            document.body.requestFullscreen();
        }
    });

    init();
});
