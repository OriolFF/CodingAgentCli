/* ---------- CONFIGURATION ---------- */
const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = 30;          // px
const FALL_INTERVAL = 500;      // ms (speed increases with level)
const COLORS = [
    null, '#FF0', '#0FF', '#F0F',
    '#00F', '#F80', '#0F0', '#FF0000'
];

/* ---------- CANVASES ---------- */
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const nextCanvas = document.getElementById('next');
const nextCtx = nextCanvas.getContext('2d');

/* ---------- STATE ---------- */
let board = createMatrix(COLS, ROWS);
let score = 0;
let lines = 0;
let level = 1;
let fallTime = 0;
let lastTime = 0;
let playing = true;
let current = null;
let next = randomPiece();

/* ---------- UTILS ---------- */
function createMatrix(w, h) {
    const matrix = [];
    while (h--) matrix.push(new Array(w).fill(0));
    return matrix;
}

function randomPiece() {
    const pieces = 'IJLOSTZ';
    const type = pieces[Math.floor(Math.random() * pieces.length)];
    const shape = TETROMINOS[type];
    return { type, shape, x: Math.floor(COLS / 2) - 2, y: -2 };
}

function drawMatrix(matrix, offset, context) {
    matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                context.fillStyle = COLORS[value];
                context.fillRect((x + offset.x) * BLOCK_SIZE,
                    (y + offset.y) * BLOCK_SIZE,
                    BLOCK_SIZE, BLOCK_SIZE);
                context.strokeStyle = '#000';
                context.strokeRect((x + offset.x) * BLOCK_SIZE,
                    (y + offset.y) * BLOCK_SIZE,
                    BLOCK_SIZE, BLOCK_SIZE);
            }
        });
    });
}

function rotate(matrix, dir) {
    // Transpose
    for (let y = 0; y < matrix.length; ++y) {
        for (let x = 0; x < y; ++x) {
            [matrix[x][y], matrix[y][x]] = [matrix[y][x], matrix[x][y]];
        }
    }
    // Reverse rows or columns
    if (dir > 0) {
        matrix.forEach(row => row.reverse());
    } else {
        matrix.reverse();
    }
}

/* ---------- GAME LOGIC ---------- */
function collide(board, player) {
    const [m, o] = [player.shape, player];
    for (let y = 0; y < m.length; ++y) {
        for (let x = 0; x < m[y].length; ++x) {
            if (m[y][x] !== 0 &&
                (board[y + o.y] &&
                    board[y + o.y][x + o.x]) !== 0) {
                return true;
            }
        }
    }
    return false;
}

function merge(board, player) {
    player.shape.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value !== 0) {
                board[y + player.y][x + player.x] = value;
            }
        });
    });
}

function reset() {
    current = next;
    next = randomPiece();
    current.x = Math.floor(COLS / 2) - 2;
    current.y = -2;

    if (collide(board, current)) {
        playing = false;
        document.getElementById('game-over').style.display = 'block';
    }
}

function clearLines() {
    let linesCleared = 0;
    outer: for (let y = board.length - 1; y >= 0; --y) {
        for (let x = 0; x < board[y].length; ++x) {
            if (board[y][x] === 0) continue outer;
        }
        const row = board.splice(y, 1)[0].fill(0);
        board.unshift(row);
        ++linesCleared;
        ++y; // check same line again after shift
    }
    if (linesCleared > 0) {
        lines += linesCleared;
        score += linesCleared * 100;
        level = Math.floor(lines / 10) + 1;
    }
}

function playerDrop() {
    current.y++;
    if (collide(board, current)) {
        current.y--;
        merge(board, current);
        reset();
        clearLines();
    }
    fallTime = 0;
}

function playerMove(dir) {
    current.x += dir;
    if (collide(board, current)) {
        current.x -= dir;
    }
}

function playerRotate(dir) {
    const pos = current.x;
    let offset = 1;
    rotate(current.shape, dir);
    while (collide(board, current)) {
        current.x += offset;
        offset = -(offset + (offset > 0 ? 1 : -1));
        if (offset > current.shape[0].length) {
            rotate(current.shape, -dir);
            current.x = pos;
            return;
        }
    }
}

/* ---------- RENDER ---------- */
function draw() {
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawMatrix(board, { x: 0, y: 0 }, ctx);
    drawMatrix(current.shape, { x: current.x, y: current.y }, ctx);
}

function drawNext() {
    nextCtx.fillStyle = '#111';
    nextCtx.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
    drawMatrix(TETROMINOS[next.type], { x: 2, y: 2 }, nextCtx);
}

/* ---------- MAIN LOOP ---------- */
function update(time = 0) {
    const delta = time - lastTime;
    lastTime = time;
    fallTime += delta;
    if (fallTime > FALL_INTERVAL / level) {
        playerDrop();
    }
    draw();
    drawNext();
    if (playing) {
        requestAnimationFrame(update);
    }
}

/* ---------- INPUT ---------- */
document.addEventListener('keydown', event => {
    if (!playing) {
        if (event.key === 'r' || event.key === 'R') {
            restart();
        }
        return;
    }
    if (event.key === 'ArrowLeft') {
        playerMove(-1);
    } else if (event.key === 'ArrowRight') {
        playerMove(1);
    } else if (event.key === 'ArrowDown') {
        playerDrop();
    } else if (event.key === 'ArrowUp') {
        playerRotate(1);
    }
});

/* ---------- INITIALIZE ---------- */
const TETROMINOS = {
    I: [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    J: [
        [2, 0, 0],
        [2, 2, 2],
        [0, 0, 0]
    ],
    L: [
        [0, 0, 3],
        [3, 3, 3],
        [0, 0, 0]
    ],
    O: [
        [4, 4],
        [4, 4]
    ],
    S: [
        [0, 5, 5],
        [5, 5, 0],
        [0, 0, 0]
    ],
    T: [
        [0, 6, 0],
        [6, 6, 6],
        [0, 0, 0]
    ],
    Z: [
        [7, 7, 0],
        [0, 7, 7],
        [0, 0, 0]
    ]
};

function restart() {
    board = createMatrix(COLS, ROWS);
    score = 0;
    lines = 0;
    level = 1;
    playing = true;
    document.getElementById('game-over').style.display = 'none';
    current = null;
    next = randomPiece();
    reset();
    lastTime = 0;
    fallTime = 0;
    requestAnimationFrame(update);
}

/* ---------- START ---------- */
reset();
lastTime = 0;
update();