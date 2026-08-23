(() => {
    const messagesElement = document.getElementById('chat-messages');
    const inputElement = document.getElementById('chat-input');
    const sendButton = document.getElementById('chat-send');
    const statusElement = document.getElementById('chat-status');
    const chatPanelElement = inputElement?.closest('.chat-panel');
    const workspaceElement = chatPanelElement?.closest('.task-workspace');
    const taskElement = workspaceElement?.querySelector('.counting-zero-module');
    let isComposing = false;
    let awaitingResponse = false;

    if (!messagesElement || !inputElement || !sendButton) return;

    function syncChatPanelHeight() {
        if (!chatPanelElement || !taskElement) return;
        if (window.matchMedia('(max-width: 900px)').matches) {
            chatPanelElement.style.removeProperty('height');
            chatPanelElement.style.removeProperty('max-height');
            return;
        }
        const taskHeight = Math.round(taskElement.getBoundingClientRect().height);
        chatPanelElement.style.setProperty('height', `${taskHeight}px`);
        chatPanelElement.style.setProperty('max-height', `${taskHeight}px`);
    }

    syncChatPanelHeight();
    window.addEventListener('resize', syncChatPanelHeight);
    if ('ResizeObserver' in window && taskElement) {
        new ResizeObserver(syncChatPanelHeight).observe(taskElement);
    }

    function appendMessage(sender, text) {
        const message = document.createElement('div');
        message.className = `chat-message ${sender}`;
        message.textContent = text;
        messagesElement.appendChild(message);
        messagesElement.scrollTop = messagesElement.scrollHeight;
    }

    function setAwaitingResponse(value) {
        awaitingResponse = value;
        sendButton.disabled = value;
        inputElement.disabled = value;
        statusElement.textContent = value ? 'AI 正在回复……' : '';
        if (!value) inputElement.focus();
    }

    function sendMessage() {
        const text = inputElement.value.trim();
        if (!text || awaitingResponse) return;
        appendMessage('participant', text);
        inputElement.value = '';
        setAwaitingResponse(true);
        liveSend({type: 'chat', text});
    }

    inputElement.addEventListener('compositionstart', () => {
        isComposing = true;
    });
    inputElement.addEventListener('compositionend', () => {
        isComposing = false;
    });
    inputElement.addEventListener('keydown', event => {
        if (event.key === 'Enter' && !event.shiftKey && !isComposing) {
            event.preventDefault();
            sendMessage();
        }
    });
    sendButton.addEventListener('click', sendMessage);

    window.addEventListener('ai-chat-message', event => {
        const data = event.detail;
        if (data.type === 'chat_response') {
            appendMessage('ai', data.text);
        } else {
            appendMessage('error', data.text);
        }
        setAwaitingResponse(false);
    });

    (js_vars.initial_chat_log || []).forEach(item => {
        appendMessage(item.sender === 'Participant' ? 'participant' : 'ai', item.text);
    });
})();
