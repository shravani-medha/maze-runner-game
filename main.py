<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Maze Runner</title>
<style>
    body { margin: 0; background: #fff; font-family: sans-serif; }
    canvas { display: block; margin: auto; background: #eee; }
    #info { text-align: center; font-size: 20px; margin: 10px; }
    button { font-size: 18px; margin: 10px; padding: 10px 20px; }
</style>
</head>
<body>
<div id="info">Lives: 3 | Score: 0</div>
<canvas id="gameCanvas" width="800" height="600"></canvas>
<button id="restartBtn">Restart Game</button>

<script>
// --- Canvas Setup ---
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// --- Game Settings ---
const TILE_SIZE = 40;
const PLAYER_SPEED = 4;
const ENEMY_SPEED = 4;
const MAX_LIVES = 3;

// --- Sprites ---
const playerImg = new Image();
playerImg.src = "boy.png";  // use your sprite
const enemyImg = new Image();
enemyImg.src = "hod.png";    // enemy sprite

// --- Sounds ---
const eatSound = new Audio("eat.wav");
const hitSound = new Audio("hit.wav");
const winSound = new Audio("win.wav");
const bgm = new Audio("bgm.mp3");
bgm.loop = true;
bgm.play().catch(()=>{});  // play if allowed

// --- Levels (0=empty, 1=wall, 2=pellet) ---
const LEVELS = [
[
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,2,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,2,0,1],
[1,0,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1],
[1,0,1,0,0,0,0,0,2,0,0,0,0,0,0,1,0,0,0,1],
[1,0,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1],
[1,0,0,0,0,0,2,0,0,0,2,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]
];

// --- Game Variables ---
let currentLevel = 0;
let maze = LEVELS[currentLevel].map(r => r.slice());
let lives = MAX_LIVES;
let score = 0;

const player = { x: TILE_SIZE, y: TILE_SIZE, width: TILE_SIZE, height: TILE_SIZE };
const enemy = { x: canvas.width - TILE_SIZE*2, y: canvas.height - TILE_SIZE*2, width: TILE_SIZE, height: TILE_SIZE };

// --- Input ---
const keys = {};
document.addEventListener("keydown", e => keys[e.key] = true);
document.addEventListener("keyup", e => keys[e.key] = false);

// Touch controls
let touchStart = null;
canvas.addEventListener("touchstart", e => {
    const t = e.touches[0];
    touchStart = { x: t.clientX, y: t.clientY };
});
canvas.addEventListener("touchmove", e => {
    if(!touchStart) return;
    const t = e.touches[0];
    const dx = t.clientX - touchStart.x;
    const dy = t.clientY - touchStart.y;
    if(Math.abs(dx) > Math.abs(dy)){
        keys['ArrowRight'] = dx>0;
        keys['ArrowLeft'] = dx<0;
    } else {
        keys['ArrowDown'] = dy>0;
        keys['ArrowUp'] = dy<0;
    }
});
canvas.addEventListener("touchend", e => { 
    keys['ArrowUp']=keys['ArrowDown']=keys['ArrowLeft']=keys['ArrowRight']=false; 
    touchStart=null;
});

// --- Helper Functions ---
function drawMaze(){
    for(let y=0; y<maze.length; y++){
        for(let x=0; x<maze[y].length; x++){
            const tile = maze[y][x];
            if(tile===1){
                ctx.fillStyle="black";
                ctx.fillRect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE);
            } else if(tile===2){
                ctx.fillStyle="green";
                ctx.beginPath();
                ctx.arc(x*TILE_SIZE+TILE_SIZE/2, y*TILE_SIZE+TILE_SIZE/2, 5,0,Math.PI*2);
                ctx.fill();
            }
        }
    }
}

function collideRect(a, b){
    return !(a.x + a.width < b.x || a.x > b.x + b.width || a.y + a.height < b.y || a.y > b.y + b.height);
}

function getTileAt(px, py){
    const x = Math.floor(px / TILE_SIZE);
    const y = Math.floor(py / TILE_SIZE);
    return maze[y] && maze[y][x];
}

function setTileAt(px, py, val){
    const x = Math.floor(px / TILE_SIZE);
    const y = Math.floor(py / TILE_SIZE);
    if(maze[y] && maze[y][x] !== undefined) maze[y][x]=val;
}

// --- Game Loop ---
function update(){
    // Move player
    let dx=0, dy=0;
    if(keys['ArrowLeft']) dx=-PLAYER_SPEED;
    if(keys['ArrowRight']) dx=PLAYER_SPEED;
    if(keys['ArrowUp']) dy=-PLAYER_SPEED;
    if(keys['ArrowDown']) dy=PLAYER_SPEED;

    let newPlayer = { ...player, x: player.x+dx, y: player.y+dy };
    // collision with walls
    if(getTileAt(newPlayer.x, newPlayer.y)==1 || getTileAt(newPlayer.x+player.width-1, newPlayer.y)==1 ||
       getTileAt(newPlayer.x, newPlayer.y+player.height-1)==1 || getTileAt(newPlayer.x+player.width-1, newPlayer.y+player.height-1)==1){
        // cannot move
    } else player.x+=dx, player.y+=dy;

    // collect pellets
    if(getTileAt(player.x+player.width/2, player.y+player.height/2)===2){
        setTileAt(player.x+player.width/2, player.y+player.height/2,0);
        score++;
        eatSound.play();
    }

    // Move enemy towards player
    if(enemy.x < player.x) enemy.x += ENEMY_SPEED;
    if(enemy.x > player.x) enemy.x -= ENEMY_SPEED;
    if(enemy.y < player.y) enemy.y += ENEMY_SPEED;
    if(enemy.y > player.y) enemy.y -= ENEMY_SPEED;

    // Collision with enemy
    if(collideRect(player, enemy)){
        lives--;
        hitSound.play();
        player.x = TILE_SIZE; player.y = TILE_SIZE;
        enemy.x = canvas.width - TILE_SIZE*2; enemy.y = canvas.height - TILE_SIZE*2;
        if(lives<=0){
            alert("GAME OVER");
            resetGame();
        }
    }

    // Check if all pellets eaten
    if(maze.flat().every(t=>t!==2)){
        winSound.play();
        currentLevel++;
        if(currentLevel<LEVELS.length){
            maze = LEVELS[currentLevel].map(r=>r.slice());
            player.x = TILE_SIZE; player.y = TILE_SIZE;
            enemy.x = canvas.width - TILE_SIZE*2; enemy.y = canvas.height - TILE_SIZE*2;
        } else {
            alert("YOU WIN!");
            resetGame();
        }
    }

    // Draw everything
    draw();
    requestAnimationFrame(update);
}

function draw(){
    ctx.fillStyle="white";
    ctx.fillRect(0,0,canvas.width,canvas.height);
    drawMaze();
    ctx.drawImage(playerImg, player.x, player.y, TILE_SIZE, TILE_SIZE);
    ctx.drawImage(enemyImg, enemy.x, enemy.y, TILE_SIZE, TILE_SIZE);
    document.getElementById("info").textContent=`Lives: ${lives} | Score: ${score}`;
}

// Restart button
function resetGame(){
    lives=MAX_LIVES;
    score=0;
    currentLevel=0;
    maze = LEVELS[currentLevel].map(r=>r.slice());
    player.x=TILE_SIZE; player.y=TILE_SIZE;
    enemy.x=canvas.width - TILE_SIZE*2; enemy.y=canvas.height - TILE_SIZE*2;
}

document.getElementById("restartBtn").addEventListener("click", resetGame);

// Start game
update();
</script>
</body>
</html>
