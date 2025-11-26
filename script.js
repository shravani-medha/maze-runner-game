// --- BASIC PAC-MAZE RUNNER GAME ENGINE ---

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const tile = 32;

// Maze layout (1 = wall, 0 = path)
const maze = [
  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
  [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1],
  [1,0,1,1,1,0,0,1,0,1,0,1,0,0,1,1,1,0,0,1],
  [1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
  [1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1],
  [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1],
  [1,0,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1],
  [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
];

// Load sprites
const runnerImg = new Image();
runnerImg.src = "girl.png";

const catcherImg = new Image();
catcherImg.src = "hod.png";

const boosterImg = new Image();
boosterImg.src = "note.png";

// Player / enemy
let runner = { x: 1, y: 1, speed: 2 };
let catcher = { x: 18, y: 7, speed: 0.5 };

let boosters = [
  {x:5, y:1, active:true},
  {x:10, y:5, active:true},
  {x:15, y:3, active:true}
];

let keys = {};

document.addEventListener("keydown", e => keys[e.key] = true);
document.addEventListener("keyup", e => keys[e.key] = false);

function canMove(nx, ny) {
  return maze[ny] && maze[ny][nx] === 0;
}

function moveRunner() {
  let nx = runner.x;
  let ny = runner.y;

  if (keys["ArrowUp"]) ny -= runner.speed / tile;
  if (keys["ArrowDown"]) ny += runner.speed / tile;
  if (keys["ArrowLeft"]) nx -= runner.speed / tile;
  if (keys["ArrowRight"]) nx += runner.speed / tile;

  if (canMove(Math.floor(nx), Math.floor(runner.y))) runner.x = nx;
  if (canMove(Math.floor(runner.x), Math.floor(ny))) runner.y = ny;
}

function moveCatcher() {
  // Simple homing AI
  let dx = runner.x - catcher.x;
  let dy = runner.y - catcher.y;
  let d = Math.sqrt(dx*dx + dy*dy);

  catcher.x += (dx/d) * catcher.speed / tile;
  catcher.y += (dy/d) * catcher.speed / tile;
}

function checkBoosters() {
  boosters.forEach(b => {
    if (b.active &&
        Math.abs(runner.x - b.x) < 0.5 &&
        Math.abs(runner.y - b.y) < 0.5) {
      b.active = false;
      runner.speed = 4; // Speed boost
      setTimeout(() => runner.speed = 2, 5000);
    }
  });
}

function checkLose() {
  if (Math.abs(runner.x - catcher.x) < 0.3 &&
      Math.abs(runner.y - catcher.y) < 0.3) {
    alert("Caught! Game Over.");
    location.reload();
  }
}

function draw() {
  ctx.clearRect(0,0,canvas.width,canvas.height);

  // Draw maze
  for (let y=0; y<maze.length; y++) {
    for (let x=0; x<maze[y].length; x++) {
      if (maze[y][x] === 1) {
        ctx.fillStyle = "#0af";
        ctx.fillRect(x*tile, y*tile, tile, tile);
      }
    }
  }

  // Draw boosters
  boosters.forEach(b => {
    if (b.active) ctx.drawImage(boosterImg, b.x*tile, b.y*tile, tile, tile);
  });

  // Draw runner
  ctx.drawImage(runnerImg, runner.x*tile, runner.y*tile, tile, tile);

  // Draw catcher
  ctx.drawImage(catcherImg, catcher.x*tile, catcher.y*tile, tile, tile);
}

function gameLoop() {
  moveRunner();
  moveCatcher();
  checkBoosters();
  checkLose();
  draw();
  requestAnimationFrame(gameLoop);
}

gameLoop();