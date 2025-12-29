let rows = 0;
let cols = 0;

async function newGame(diff) {
    document.getElementById('message').textContent = "Generating game...";

    const res = await fetch('/api/new_game', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({difficulty: diff})
    });
    const data = await res.json();
    rows = data.rows;
    cols = data.cols;

    renderGrid(rows, cols);
    document.getElementById('message').textContent = `Started ${diff} game. Mines: ${data.mines_total}`;

    // Process initial revealed cells (the auto-start cell)
    if (data.revealed) {
        data.revealed.forEach(cellData => {
            updateCell(cellData.r, cellData.c, cellData.clue);
        });
    }
}

function renderGrid(r, c) {
    const grid = document.getElementById('grid');
    grid.style.gridTemplateColumns = `repeat(${c}, 40px)`;
    grid.innerHTML = '';

    for(let i=0; i<r; i++) {
        for(let j=0; j<c; j++) {
            let cell = document.createElement('div');
            cell.className = 'cell';
            cell.id = `c-${i}-${j}`;
            cell.onclick = () => clickCell(i, j);
            grid.appendChild(cell);
        }
    }
}

function updateCell(r, c, clue) {
    const cell = document.getElementById(`c-${r}-${c}`);
    if (!cell) return;

    cell.classList.add('revealed');
    cell.classList.remove('safe-hint');
    cell.classList.remove('mine-flag'); // Clear any previous hints

    if (clue > 0) {
        cell.textContent = clue;
        cell.style.color = getClueColor(clue);
    } else {
        cell.textContent = "";
    }
}

function getClueColor(n) {
    const colors = ['#000', 'blue', 'green', 'red', 'darkblue', 'brown', 'cyan', 'black', 'gray'];
    return colors[n] || 'black';
}

async function clickCell(r, c) {
    const cell = document.getElementById(`c-${r}-${c}`);
    if(cell.classList.contains('revealed')) return;

    document.getElementById('message').textContent = `Checking (${r}, ${c}) with Prover9...`;

    try {
        const res = await fetch('/api/click', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({r: r, c: c})
        });
        const data = await res.json();

        if (data.status === 'safe') {
            updateCell(data.r, data.c, data.clue);
            document.getElementById('message').textContent = "Safe! Proved by logic.";
        } else if (data.status === 'blocked') {
            document.getElementById('message').textContent = data.message;
            cell.style.backgroundColor = "#ffaaaa"; // Red flash for blocked
            setTimeout(() => {
                if(!cell.classList.contains('revealed')) cell.style.backgroundColor = "";
            }, 500);
        }
    } catch (e) {
        document.getElementById('message').textContent = "Error communicating with server.";
    }
}

async function getHint() {
    document.getElementById('message').textContent = "Prover9 is thinking...";
    const res = await fetch('/api/hint', { method: 'POST' });
    const data = await res.json();

    if (data.type === 'safe') {
        document.getElementById('message').textContent = `Hint: (${data.r}, ${data.c}) is PROVABLY SAFE.`;
        const cell = document.getElementById(`c-${data.r}-${data.c}`);
        cell.classList.add('safe-hint');
    } else if (data.type === 'mine') {
        document.getElementById('message').textContent = `Hint: (${data.r}, ${data.c}) is PROVABLY A MINE.`;
        const cell = document.getElementById(`c-${data.r}-${data.c}`);
        cell.classList.add('mine-flag');
        cell.textContent = "!";
    } else {
        document.getElementById('message').textContent = data.message || "No logic hints available.";
    }
}

async function checkConsistency() {
    document.getElementById('message').textContent = "Mace4 is checking models...";
    const res = await fetch('/api/check', { method: 'POST' });
    const data = await res.json();

    if (data.consistent) {
        document.getElementById('message').textContent = "State is CONSISTENT.";
    } else {
        document.getElementById('message').textContent = "State is INCONSISTENT (Logic Error!)";
    }
}