(() => {
    const matrixElement = document.getElementById('matrix');
    const answerElement = document.getElementById('zero-answer');
    const submitButton = document.getElementById('submit-answer');
    const copyButton = document.getElementById('copy-matrix');
    const copyStatusElement = document.getElementById('copy-status');
    const feedbackElement = document.getElementById('feedback');
    const questionNumberElement = document.getElementById('question-number');
    const cumulativeScoreElement = document.getElementById('cumulative-score');
    const timerSlotElement = document.getElementById('task-timer-slot');
    let displayedMatrix = [];

    if (!matrixElement || !answerElement || !submitButton || !feedbackElement) return;

    const otreeTimerElement = document.querySelector('.otree-timer');
    if (timerSlotElement && otreeTimerElement) {
        timerSlotElement.appendChild(otreeTimerElement);
    }

    function renderMatrix(matrix) {
        displayedMatrix = matrix;
        matrixElement.replaceChildren();
        const fragment = document.createDocumentFragment();
        matrix.flat().forEach(value => {
            const cell = document.createElement('span');
            cell.className = 'matrix-cell';
            cell.textContent = value;
            fragment.appendChild(cell);
        });
        matrixElement.appendChild(fragment);
        if (copyStatusElement) copyStatusElement.textContent = '';
    }

    async function copyMatrix() {
        const matrixText = displayedMatrix
            .map(row => row.join('\t'))
            .join('\n');
        try {
            await navigator.clipboard.writeText(matrixText);
        } catch (error) {
            const temporaryTextArea = document.createElement('textarea');
            temporaryTextArea.value = matrixText;
            temporaryTextArea.style.position = 'fixed';
            temporaryTextArea.style.opacity = '0';
            document.body.appendChild(temporaryTextArea);
            temporaryTextArea.select();
            document.execCommand('copy');
            temporaryTextArea.remove();
        }
        if (copyStatusElement) copyStatusElement.textContent = '已复制';
    }

    function setSubmitting(isSubmitting) {
        submitButton.disabled = isSubmitting;
        answerElement.disabled = isSubmitting;
    }

    function submitAnswer() {
        if (answerElement.value === '') {
            feedbackElement.className = 'error-feedback';
            feedbackElement.textContent = '请输入 0 的数量。';
            return;
        }
        setSubmitting(true);
        liveSend({type: 'submit', answer: answerElement.value});
    }

    if (copyButton) copyButton.addEventListener('click', copyMatrix);
    submitButton.addEventListener('click', submitAnswer);
    answerElement.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            submitAnswer();
        }
    });

    window.liveRecv = data => {
        if (data.type === 'chat_response' || data.type === 'chat_error') {
            window.dispatchEvent(
                new CustomEvent('ai-chat-message', {detail: data})
            );
            return;
        }
        if (data.error) {
            feedbackElement.className = 'error-feedback';
            feedbackElement.textContent = data.error;
            setSubmitting(false);
            answerElement.focus();
            return;
        }
        if (data.time_up) {
            submitButton.disabled = true;
            answerElement.disabled = true;
            return;
        }
        if (data.matrix) renderMatrix(data.matrix);
        if (data.question_number) {
            questionNumberElement.textContent = data.question_number;
        }
        if (js_vars.show_feedback && cumulativeScoreElement) {
            cumulativeScoreElement.textContent =
                Number(data.cumulative_score || 0).toFixed(2);
        }
        if (js_vars.show_feedback && data.feedback) {
            feedbackElement.className = 'score-feedback';
            feedbackElement.textContent =
                `本次得分：${Number(data.feedback.score).toFixed(2)}；` +
                `累计得分：${Number(data.feedback.cumulative_score).toFixed(2)}`;
        }
        answerElement.value = '';
        setSubmitting(false);
        answerElement.focus();
    };

    renderMatrix(js_vars.initial_matrix);
    questionNumberElement.textContent = js_vars.initial_question_number;
    if (js_vars.show_feedback && cumulativeScoreElement) {
        cumulativeScoreElement.textContent =
            Number(js_vars.initial_cumulative_score).toFixed(2);
    }
    answerElement.focus();

    document.addEventListener('DOMContentLoaded', () => {
        liveSend({type: 'load'});
    });
})();
