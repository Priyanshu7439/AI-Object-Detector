const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const videoFeed = document.getElementById('videoFeed');
const videoPlaceholder = document.getElementById('videoPlaceholder');
const statusBadge = document.getElementById('statusBadge');
const statusText = document.getElementById('statusText');

startBtn.addEventListener('click', async () => {
    try {
        startBtn.disabled = true;
        videoPlaceholder.classList.add('loading');
        videoPlaceholder.querySelector('p').textContent = 'Starting camera...';

        const response = await fetch('/start_feed');
        const data = await response.json();

        console.log("START RESPONSE:", data);

        if (data.status !== 'error') {
            videoFeed.src = '/video_feed';
            videoFeed.style.display = 'block';
            videoPlaceholder.style.display = 'none';

            statusBadge.classList.add('online');
            statusText.textContent = 'Live';
            stopBtn.disabled = false;
        } else {
            alert('Error: ' + (data.message || 'Unknown error'));
            startBtn.disabled = false;
            videoPlaceholder.classList.remove('loading');
            videoPlaceholder.querySelector('p').textContent = 'Camera failed to start';
        }

    } catch (error) {
        console.error('REAL ERROR:', error);
        alert('Failed to connect to server');

        startBtn.disabled = false;
        videoPlaceholder.classList.remove('loading');
    }
});

stopBtn.addEventListener('click', async () => {
    try {
        stopBtn.disabled = true;

        await fetch('/stop_feed');

        videoFeed.src = '';
        videoFeed.style.display = 'none';
        videoPlaceholder.style.display = 'flex';

        videoPlaceholder.classList.remove('loading');
        videoPlaceholder.querySelector('p').textContent = 'Camera is stopped';

        statusBadge.classList.remove('online');
        statusText.textContent = 'Offline';

        startBtn.disabled = false;

    } catch (error) {
        console.error('Failed to stop stream:', error);
        stopBtn.disabled = false;
    }
});