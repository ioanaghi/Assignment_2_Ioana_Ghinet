let rows = 0;
let cols = 0;

function setMessage(text) {
    const el = document.getElementById('message');
    if (el) el.textContent = text;
}

function getDifficulty() {
    const select = document.getElementById('difficulty');
    return select ? select.value : 'easy';
}

async function newGame() {
    setMessage('Creating a fresh board...');

    const res = await fetch('/api/new_game', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({difficulty: getDifficulty()})
    });
    const data = await res.json();

    rows = data.rows;
    cols = data.cols;

    renderGrid(rows, cols);
    setMessage(`New game ready. Mines hidden: ${data.mines_total}.`);

    if (data.revealed) {
        data.revealed.forEach(cell => {
            updateCell(cell.r, cell.c, cell.clue);
        });
    }
}

function renderGrid(r, c) {
    const grid = document.getElementById('grid');
    grid.style.gridTemplateColumns = `repeat(${c}, var(--cell-size))`;
    grid.innerHTML = '';

    const size = Math.max(32, Math.min(48, Math.floor(360 / c)));
    grid.style.setProperty('--cell-size', `${size}px`);

    for (let i = 0; i < r; i++) {
        for (let j = 0; j < c; j++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.id = `c-${i}-${j}`;
            cell.addEventListener('click', () => clickCell(i, j));
            cell.addEventListener('contextmenu', (event) => {
                event.preventDefault();
                toggleFlag(i, j);
            });
            grid.appendChild(cell);
        }
    }
}

function updateCell(r, c, clue) {
    const cell = document.getElementById(`c-${r}-${c}`);
    if (!cell) return;

    cell.classList.add('revealed');
    cell.classList.remove('safe-hint', 'flagged', 'blocked');
    cell.textContent = clue > 0 ? clue : '';
    cell.style.color = getClueColor(clue);
}

function getClueColor(n) {
    const colors = ['#4a4a4a', '#3a6ea5', '#2e8b57', '#d35400', '#8e44ad', '#8b4513', '#16a085', '#2c3e50', '#7f8c8d'];
    return colors[n] || '#4a4a4a';
}

async function clickCell(r, c) {
    const cell = document.getElementById(`c-${r}-${c}`);
    if (!cell || cell.classList.contains('revealed')) return;
    if (cell.classList.contains('flagged')) {
        setMessage('Cell is flagged. Remove the flag first.');
        return;
    }

    setMessage(`Checking (${r}, ${c}) with Prover9...`);

    const res = await fetch('/api/click', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({r: r, c: c})
    });
    const data = await res.json();

    if (data.status === 'safe') {
        updateCell(data.r, data.c, data.clue);
        setMessage('🌸 Safe and proven by logic!');
        return;
    }

    if (data.status === 'blocked') {
        setMessage(data.message || 'Logic cannot prove safety yet.');
        cell.classList.add('blocked');
        setTimeout(() => cell.classList.remove('blocked'), 300);
        return;
    }

    if (data.status === 'boom') {
        setMessage('That was a mine.');
        cell.classList.add('revealed');
        cell.textContent = '💥';
    }
}

async function toggleFlag(r, c) {
    const cell = document.getElementById(`c-${r}-${c}`);
    if (!cell || cell.classList.contains('revealed')) return;

    const res = await fetch('/api/flag', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({r: r, c: c})
    });
    const data = await res.json();

    if (data.flagged) {
        cell.classList.add('flagged');
        cell.textContent = '🚩';
    } else {
        cell.classList.remove('flagged');
        cell.textContent = '';
    }
}

async function getHint() {
    setMessage('✨ Searching for provably safe cells...');
    const res = await fetch('/api/hint', { method: 'POST' });
    const data = await res.json();

    document.querySelectorAll('.safe-hint').forEach(el => {
        el.classList.remove('safe-hint');
        if (!el.classList.contains('revealed') && !el.classList.contains('flagged') && el.textContent === '🌸') {
            el.textContent = '';
        }
    });

    if (data.type === 'safe') {
        data.cells.forEach(cell => {
            const el = document.getElementById(`c-${cell.r}-${cell.c}`);
            if (el && !el.classList.contains('revealed')) {
                el.classList.add('safe-hint');
                if (!el.classList.contains('flagged')) {
                    el.textContent = '🌸';
                }
            }
        });
        setMessage(`✨ ${data.cells.length} safe cell(s) highlighted.`);
    } else {
        setMessage(data.message || 'No logic hints available.');
    }
}

async function checkConsistency() {
    setMessage('Checking consistency with Mace4...');
    const res = await fetch('/api/check', { method: 'POST' });
    const data = await res.json();

    if (data.consistent) {
        setMessage('✅ State is consistent with all clues.');
    } else {
        setMessage('⚠️ Flags contradict the revealed numbers.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('new-game').addEventListener('click', newGame);
    document.getElementById('hint').addEventListener('click', getHint);
    document.getElementById('check').addEventListener('click', checkConsistency);
    document.getElementById('difficulty').addEventListener('change', newGame);
    newGame();
});
