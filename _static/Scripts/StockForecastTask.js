(() => {
    const SVG_NS = 'http://www.w3.org/2000/svg';
    const chartElement = document.getElementById('stock-chart');
    const seriesDataElement = document.getElementById('stock-series-data');
    const answerElement = document.getElementById('forecast-answer');
    const submitButton = document.getElementById('submit-answer');
    const copyButton = document.getElementById('copy-matrix');
    const copyStatusElement = document.getElementById('copy-status');
    const feedbackElement = document.getElementById('feedback');
    const questionNumberElement = document.getElementById('question-number');
    const cumulativeScoreElement = document.getElementById('cumulative-score');
    const timerSlotElement = document.getElementById('task-timer-slot');
    let displayedSeries = [];
    let chartGeometry = null;

    if (!chartElement || !answerElement || !submitButton || !feedbackElement) return;

    const otreeTimerElement = document.querySelector('.otree-timer');
    if (timerSlotElement && otreeTimerElement) {
        timerSlotElement.appendChild(otreeTimerElement);
    }

    function svgElement(name, attributes = {}) {
        const element = document.createElementNS(SVG_NS, name);
        Object.entries(attributes).forEach(([key, value]) => {
            element.setAttribute(key, value);
        });
        return element;
    }

    function renderSeries(series) {
        displayedSeries = series.map(value => Number(value).toFixed(2));
        chartElement.replaceChildren();
        const width = 640;
        const height = 215;
        const margin = {top: 18, right: 18, bottom: 22, left: 58};
        const plotWidth = width - margin.left - margin.right;
        const plotHeight = height - margin.top - margin.bottom;
        const values = series.map(Number);
        const rawMin = Math.min(...values);
        const rawMax = Math.max(...values);
        const padding = Math.max((rawMax - rawMin) * 0.08, 1);
        const minValue = rawMin - padding;
        const maxValue = rawMax + padding;
        const range = maxValue - minValue;
        const x = index => margin.left + index / (values.length - 1) * plotWidth;
        const y = value => margin.top + (maxValue - value) / range * plotHeight;

        for (let tick = 0; tick <= 4; tick += 1) {
            const tickY = margin.top + tick / 4 * plotHeight;
            const tickValue = maxValue - tick / 4 * range;
            chartElement.appendChild(svgElement('line', {
                x1: margin.left, y1: tickY, x2: width - margin.right, y2: tickY,
                class: 'chart-grid-line',
            }));
            const label = svgElement('text', {
                x: margin.left - 8, y: tickY + 4, class: 'chart-y-label',
            });
            label.textContent = tickValue.toFixed(2);
            chartElement.appendChild(label);
        }
        chartElement.appendChild(svgElement('line', {
            x1: margin.left, y1: margin.top, x2: margin.left,
            y2: height - margin.bottom, class: 'chart-axis-line',
        }));
        chartElement.appendChild(svgElement('line', {
            x1: margin.left, y1: height - margin.bottom,
            x2: width - margin.right, y2: height - margin.bottom,
            class: 'chart-axis-line',
        }));
        const points = values.map((value, index) => `${x(index)},${y(value)}`).join(' ');
        chartElement.appendChild(svgElement('polyline', {
            points, class: 'chart-price-line',
        }));

        const hoverPoint = svgElement('circle', {
            r: 4,
            class: 'chart-hover-point',
        });
        const tooltip = svgElement('g', {class: 'chart-tooltip'});
        const tooltipBox = svgElement('rect', {
            x: 0, y: -27, width: 62, height: 25, rx: 5,
        });
        const tooltipText = svgElement('text', {x: 8, y: -10});
        tooltip.append(tooltipBox, tooltipText);
        chartElement.append(hoverPoint, tooltip);
        chartGeometry = {
            width,
            margin,
            plotWidth,
            values,
            x,
            y,
            hoverPoint,
            tooltip,
            tooltipText,
        };
        if (seriesDataElement) {
            seriesDataElement.textContent = displayedSeries.join(', ');
            seriesDataElement.scrollTop = 0;
        }
        if (copyStatusElement) copyStatusElement.textContent = '';
    }

    function showHoveredPrice(event) {
        if (!chartGeometry) return;
        const bounds = chartElement.getBoundingClientRect();
        const svgX = (event.clientX - bounds.left) / bounds.width * chartGeometry.width;
        const relativeX = Math.max(
            0,
            Math.min(chartGeometry.plotWidth, svgX - chartGeometry.margin.left)
        );
        const index = Math.round(
            relativeX / chartGeometry.plotWidth * (chartGeometry.values.length - 1)
        );
        const value = chartGeometry.values[index];
        const pointX = chartGeometry.x(index);
        const pointY = chartGeometry.y(value);
        const tooltipX = Math.min(
            pointX + 9,
            chartGeometry.width - chartGeometry.margin.right - 62
        );

        chartGeometry.hoverPoint.setAttribute('cx', pointX);
        chartGeometry.hoverPoint.setAttribute('cy', pointY);
        chartGeometry.tooltip.setAttribute(
            'transform',
            `translate(${tooltipX},${Math.max(pointY, 38)})`
        );
        chartGeometry.tooltipText.textContent = value.toFixed(2);
        chartElement.classList.add('show-chart-hover');
    }

    function hideHoveredPrice() {
        chartElement.classList.remove('show-chart-hover');
    }

    async function copySeries() {
        const text = displayedSeries.join('\n');
        try {
            await navigator.clipboard.writeText(text);
        } catch (error) {
            const temporaryTextArea = document.createElement('textarea');
            temporaryTextArea.value = text;
            temporaryTextArea.style.position = 'fixed';
            temporaryTextArea.style.opacity = '0';
            document.body.appendChild(temporaryTextArea);
            temporaryTextArea.select();
            document.execCommand('copy');
            temporaryTextArea.remove();
        }
        if (copyStatusElement) copyStatusElement.textContent = '已复制';
    }

    function setSubmitting(value) {
        submitButton.disabled = value;
        answerElement.disabled = value;
    }

    function submitAnswer() {
        if (answerElement.value === '') {
            feedbackElement.className = 'error-feedback';
            feedbackElement.textContent = '请输入预测价格。';
            return;
        }
        setSubmitting(true);
        liveSend({type: 'submit', answer: answerElement.value});
    }

    if (copyButton) copyButton.addEventListener('click', copySeries);
    chartElement.addEventListener('pointermove', showHoveredPrice);
    chartElement.addEventListener('pointerleave', hideHoveredPrice);
    submitButton.addEventListener('click', submitAnswer);
    answerElement.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            submitAnswer();
        }
    });

    window.liveRecv = data => {
        if (data.type === 'chat_response' || data.type === 'chat_error') {
            window.dispatchEvent(new CustomEvent('ai-chat-message', {detail: data}));
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
        if (data.series) renderSeries(data.series);
        if (data.question_number) questionNumberElement.textContent = data.question_number;
        if (js_vars.show_feedback && cumulativeScoreElement) {
            cumulativeScoreElement.textContent = Number(data.cumulative_score || 0).toFixed(2);
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

    renderSeries(js_vars.initial_series);
    questionNumberElement.textContent = js_vars.initial_question_number;
    if (js_vars.show_feedback && cumulativeScoreElement) {
        cumulativeScoreElement.textContent = Number(js_vars.initial_cumulative_score).toFixed(2);
    }
    answerElement.focus();
    document.addEventListener('DOMContentLoaded', () => liveSend({type: 'load'}));
})();
