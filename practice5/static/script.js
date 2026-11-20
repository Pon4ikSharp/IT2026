// Завантажуємо дані з Flask API та показуємо їх у таблиці.
let documents = [];
const statuses = ['не виконано', 'в процесі', 'виконано'];

function showMessage(text) {
    document.getElementById('message').textContent = text;
}

async function loadTypes() {
    const response = await fetch('/api/document-types');
    if (!response.ok) throw new Error('Не вдалося отримати типи документів');
    const types = await response.json();
    const formSelect = document.getElementById('type_id');
    const filterSelect = document.getElementById('type-filter');

    types.forEach(type => {
        const option = new Option(type.type_name, type.type_id);
        formSelect.add(option);
        filterSelect.add(new Option(type.type_name, type.type_name));
    });
}

async function loadDocuments() {
    const response = await fetch('/api/documents');
    if (!response.ok) throw new Error('Не вдалося отримати документи');
    documents = await response.json();
    showDocuments();
}

function showDocuments() {
    const body = document.querySelector('#documents-table tbody');
    const search = document.getElementById('search').value.trim().toLowerCase();
    const type = document.getElementById('type-filter').value;
    body.replaceChildren();

    const filtered = documents.filter(doc => {
        const matchesText = (doc.number + ' ' + doc.content).toLowerCase().includes(search);
        const matchesType = !type || doc.type_name === type;
        return matchesText && matchesType;
    });

    filtered.forEach(doc => {
        const row = body.insertRow();
        [doc.document_id, doc.number, doc.type_name, doc.content, doc.date].forEach(value => {
            const cell = row.insertCell();
            cell.textContent = value;
        });

        const statusCell = row.insertCell();
        const statusSelect = document.createElement('select');
        statuses.forEach(status => statusSelect.add(new Option(status, status)));
        statusSelect.value = doc.completion_status;
        statusSelect.addEventListener('change', async () => {
            try {
                const response = await fetch('/api/documents/' + doc.document_id + '/status', {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({completion_status: statusSelect.value})
                });
                if (!response.ok) throw new Error('Помилка зміни статусу');
                showMessage('Статус змінено');
                await loadDocuments();
            } catch (error) {
                showMessage(error.message);
                await loadDocuments().catch(() => {});
            }
        });
        statusCell.appendChild(statusSelect);

        const actionCell = row.insertCell();
        const button = document.createElement('button');
        button.textContent = 'Видалити';
        button.addEventListener('click', async () => {
            if (!confirm('Видалити цей документ?')) return;
            try {
                const response = await fetch('/api/documents/' + doc.document_id, {method: 'DELETE'});
                if (!response.ok) throw new Error('Помилка видалення');
                showMessage('Документ видалено');
                await loadDocuments();
            } catch (error) {
                showMessage(error.message);
            }
        });
        actionCell.appendChild(button);
    });

    // Найпростіший аналіз: рахуємо документи за статусами.
    document.getElementById('total').textContent = documents.length;
    document.getElementById('done').textContent = documents.filter(d => d.completion_status === 'виконано').length;
    document.getElementById('in-progress').textContent = documents.filter(d => d.completion_status === 'в процесі').length;
    document.getElementById('not-done').textContent = documents.filter(d => d.completion_status === 'не виконано').length;
}

document.getElementById('document-form').addEventListener('submit', async event => {
    event.preventDefault();
    const data = {
        number: document.getElementById('number').value,
        type_id: document.getElementById('type_id').value,
        content: document.getElementById('content').value,
        date: document.getElementById('date').value,
        completion_status: document.getElementById('completion_status').value
    };

    try {
        const response = await fetch('/api/documents', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const result = await response.json();
            throw new Error(result.error || 'Помилка додавання');
        }
        event.target.reset();
        showMessage('Документ додано');
        await loadDocuments();
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById('search').addEventListener('input', showDocuments);
document.getElementById('type-filter').addEventListener('change', showDocuments);

async function start() {
    try {
        await loadTypes();
        await loadDocuments();
    } catch (error) {
        showMessage(error.message + '. Перевірте PostgreSQL і файл .env.');
    }
}

start();
