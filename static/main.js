let rows = 0;
let cols = 0;

function setMsg(text) {
    const el = document.getElementById('message');
    if (el) el.textContent = text;
}

function getDiff() {
    const select = document.getElementById('difficulty');
    return select ? select.value : 'easy';
}

async function newGame() {
    setMsg('Creating a fresh board...');

    const res = await fetch('/api/new_game', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({difficulty: getDiff()})
    });
    const data = await res.json();

    rows = data.rows;
    cols = data.cols;

    renderGrid(rows, cols);
    setMsg(`New game ready. Mines hidden: ${data.mines_total}.`);

    if (data.revealed) {
        data.revealed.forEach(cell => {
            updateCell(cell.r, cell.c, cell.clue);
        });
    }
}

function renderGrid(r, c) {
    const grid = document.getElementById('grid');
    grid.style.gridTemplateColumns = `repeat(${c}, var(--cell-size))`;
    grid.classList.remove('disabled');
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

function showMines(mines) {
    mines.forEach(cell => {
        const el = document.getElementById(`c-${cell.r}-${cell.c}`);
        if (el && !el.classList.contains('revealed')) {
            el.classList.add('revealed');
            el.textContent = '💣';
        }
    });
}

function endGame(outcome) {
    const grid = document.getElementById('grid');
    grid.classList.add('disabled');
    if (outcome === 'win') {
        setMsg('🎉 You solved the board! Logic wins.');
    } else if (outcome === 'lose') {
        setMsg('💔 Game over. Try again with a new board.');
    }
}

function getClueColor(n) {
    const colors = ['#4a4a4a', '#3a6ea5', '#2e8b57', '#d35400', '#8e44ad', '#8b4513', '#16a085', '#2c3e50', '#7f8c8d'];
    return colors[n] || '#4a4a4a';
}

async function clickCell(r, c) {
    const cell = document.getElementById(`c-${r}-${c}`);
    if (!cell || cell.classList.contains('revealed')) return;
    if (cell.classList.contains('flagged')) {
        setMsg('Cell is flagged. Remove the flag first.');
        return;
    }

    setMsg(`Checking (${r}, ${c}) with Prover9...`);

    const res = await fetch('/api/click', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({r: r, c: c})
    });
    const data = await res.json();

    if (data.status === 'over') {
        endGame(data.outcome);
        return;
    }

    if (data.status === 'safe') {
        updateCell(data.r, data.c, data.clue);
        if (data.game_over) {
            endGame(data.outcome);
        } else {
            setMsg('🌸 Safe and proven by logic!');
        }
        return;
    }

    if (data.status === 'blocked') {
        if (data.reason === 'not_provable') {
            setMsg('Move blocked: Prover9 cannot prove this is safe.');
        } else {
            setMsg(data.message || 'Move blocked.');
        }
        cell.classList.add('blocked');
        setTimeout(() => cell.classList.remove('blocked'), 300);
        return;
    }

    if (data.status === 'boom') {
        cell.classList.add('revealed');
        cell.textContent = '💥';
        if (data.mines) {
            showMines(data.mines);
        }
        endGame(data.outcome);
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

    if (data.status === 'over') {
        endGame(data.outcome);
        return;
    }

    if (data.flagged) {
        cell.classList.add('flagged');
        cell.textContent = '🚩';
    } else {
        cell.classList.remove('flagged');
        cell.textContent = '';
    }
}

async function getHint() {
    setMsg('✨ Searching for provably safe cells...');
    const res = await fetch('/api/hint', { method: 'POST' });
    const data = await res.json();

    document.querySelectorAll('.safe-hint').forEach(el => {
        el.classList.remove('safe-hint');
        if (!el.classList.contains('revealed') && !el.classList.contains('flagged') && el.textContent === '🌸') {
            el.textContent = '';
        }
    });

    if (data.status === 'over') {
        endGame(data.outcome);
        return;
    }

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
        setMsg(`✨ ${data.cells.length} safe cell(s) highlighted.`);
    } else {
        setMsg(data.message || 'No logic hints available.');
    }
}

async function checkConsistency() {
    setMsg('Checking consistency with Mace4...');
    const res = await fetch('/api/check', { method: 'POST' });
    const data = await res.json();

    if (data.status === 'over') {
        endGame(data.outcome);
        return;
    }

    if (data.consistent === null) {
        const details = data.error ? ` (${data.error})` : '';
        setMsg(`Mace4 is unavailable.${details}`);
        return;
    }

    if (data.consistent) {
        setMsg('✅ State is consistent with all clues.');
    } else {
        setMsg('⚠️ Flags contradict the revealed numbers.');
    }
}

async function autoSolve() {
    setMsg('Solving what logic can prove...');
    const res = await fetch('/api/solve', { method: 'POST' });
    const data = await res.json();

    if (data.status === 'over') {
        endGame(data.outcome);
        return;
    }

    if (data.cells) {
        data.cells.forEach(cell => {
            updateCell(cell.r, cell.c, cell.clue);
        });
    }

    if (data.game_over) {
        endGame(data.outcome);
        return;
    }

    if (data.status === 'stuck') {
        setMsg('Solver is stuck. No more provably safe cells.');
    } else {
        setMsg('Solver revealed all provably safe cells.');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('new-game').addEventListener('click', newGame);
    document.getElementById('hint').addEventListener('click', getHint);
    document.getElementById('solve').addEventListener('click', autoSolve);
    document.getElementById('check').addEventListener('click', checkConsistency);
    document.getElementById('difficulty').addEventListener('change', newGame);
    newGame();
});
