document.getElementById('distributeBtn').onclick = async () => {
    const response = await fetch('/api/distribute');
    const data = await response.json();
    renderSchedule(data.schedule);
    document.getElementById('resetBtn').disabled = false;
};

document.getElementById('resetBtn').onclick = async () => {
    const response = await fetch('/api/reset');
    const data = await response.json();
    renderSchedule(data.schedule);
    document.getElementById('resetBtn').disabled = true;
};

function renderSchedule(schedule) {
    const tbody = document.querySelector('#scheduleTable tbody');
    tbody.innerHTML = '';
    
    schedule.forEach(daySchedule => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${daySchedule[0]?.day || ''}</td>
            ${daySchedule.map(slot => `
                <td class="${slot.is_ai ? 'ai-filled' : slot.is_manual ? 'manual' : 'empty'}">
                    ${slot.driver_id || 'Свободно'}
                </td>
            `).join('')}
        `;
        tbody.appendChild(row);
    });
}
