// 游戏变量
let canvas, ctx;
let snake = []; // 蛇的身体坐标数组
let food = {};  // 食物坐标
let direction = 'right'; // 当前移动方向
let nextDirection = 'right'; // 下一个移动方向
let score = 0; // 当前得分
let highScore = 0; // 最高分
let gameInterval; // 游戏循环间隔
let isPaused = false; // 游戏是否暂停
let gameSpeed = 150; // 游戏速度(毫秒)

// 初始化游戏
function initGame() {
    // 获取画布和上下文
    canvas = document.getElementById('game-canvas');
    ctx = canvas.getContext('2d');
    
    // 尝试从本地存储获取最高分
    highScore = localStorage.getItem('snakeHighScore') || 0;
    document.getElementById('high-score').textContent = highScore;
    
    // 初始化蛇 - 3节，位于画布中央
    snake = [
        {x: 200, y: 200},
        {x: 180, y: 200},
        {x: 160, y: 200}
    ];
    
    // 生成第一个食物
    generateFood();
    
    // 初始化分数
    score = 0;
    updateScore();
    
    // 设置事件监听器
    document.getElementById('start-btn').addEventListener('click', startGame);
    document.getElementById('restart-btn').addEventListener('click', startGame);
    document.getElementById('pause-btn').addEventListener('click', togglePause);
    document.getElementById('difficulty').addEventListener('change', changeDifficulty);
    document.addEventListener('keydown', handleKeyDown);
    
    // 移动端控制按钮事件
    document.querySelectorAll('.mobile-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const dir = this.getAttribute('data-direction');
            changeDirection(dir);
        });
    });
    
    // 绘制初始游戏状态
    drawGame();
}

// 开始游戏
function startGame() {
    // 重置游戏状态
    direction = 'right';
    nextDirection = 'right';
    isPaused = false;
    
    // 初始化蛇
    snake = [
        {x: 200, y: 200},
        {x: 180, y: 200},
        {x: 160, y: 200}
    ];
    
    // 生成食物
    generateFood();
    
    // 重置分数
    score = 0;
    updateScore();
    
    // 更新UI
    document.getElementById('game-over').style.display = 'none';
    document.getElementById('start-btn').style.display = 'none';
    document.getElementById('pause-btn').style.display = 'inline-block';
    document.getElementById('pause-btn').textContent = '暂停';
    
    // 清除之前的游戏循环
    if (gameInterval) clearInterval(gameInterval);
    
    // 开始新游戏循环
    gameInterval = setInterval(gameLoop, gameSpeed);
}

// 游戏主循环
function gameLoop() {
    if (isPaused) return;
    
    moveSnake(); // 移动蛇
    
    // 检查碰撞
    if (checkCollision()) {
        gameOver();
        return;
    }
    
    drawGame(); // 绘制游戏
}

// 移动蛇
function moveSnake() {
    // 更新方向
    direction = nextDirection;
    
    // 获取蛇头当前位置
    const head = {x: snake[0].x, y: snake[0].y};
    
    // 根据方向计算新的头部位置
    switch (direction) {
        case 'up': head.y -= 20; break;
        case 'down': head.y += 20; break;
        case 'left': head.x -= 20; break;
        case 'right': head.x += 20; break;
    }
    
    // 在数组开头添加新的头部
    snake.unshift(head);
    
    // 检查是否吃到食物
    if (head.x === food.x && head.y === food.y) {
        // 增加分数
        score += 10;
        updateScore();
        
        // 生成新食物
        generateFood();
    } else {
        // 没吃到食物则移除尾部
        snake.pop();
    }
}

// 检查碰撞
function checkCollision() {
    const head = snake[0];
    
    // 1. 检查是否撞到边界
    if (head.x < 0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height) {
        return true;
    }
    
    // 2. 检查是否撞到自己
    for (let i = 1; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            return true;
        }
    }
    
    return false;
}

// 生成食物
function generateFood() {
    // 在网格上随机生成食物位置
    food = {
        x: Math.floor(Math.random() * (canvas.width / 20)) * 20,
        y: Math.floor(Math.random() * (canvas.height / 20)) * 20
    };
    
    // 确保食物不会出现在蛇身上
    for (let segment of snake) {
        if (segment.x === food.x && segment.y === food.y) {
            // 如果重叠，重新生成
            return generateFood();
        }
    }
}

// 处理键盘输入
function handleKeyDown(e) {
    // 空格键暂停/继续
    if (e.keyCode === 32) {
        togglePause();
        return;
    }
    
    // 方向键改变方向
    changeDirectionByKey(e.keyCode);
}

// 根据按键码改变方向
function changeDirectionByKey(keyCode) {
    // 防止180度转弯
    if (keyCode === 37 && direction !== 'right') nextDirection = 'left';      // 左箭头
    else if (keyCode === 38 && direction !== 'down') nextDirection = 'up';   // 上箭头
    else if (keyCode === 39 && direction !== 'left') nextDirection = 'right'; // 右箭头
    else if (keyCode === 40 && direction !== 'up') nextDirection = 'down';    // 下箭头
}

// 改变方向(通用方法)
function changeDirection(newDirection) {
    // 防止180度转弯
    if (newDirection === 'left' && direction !== 'right') nextDirection = 'left';
    else if (newDirection === 'up' && direction !== 'down') nextDirection = 'up';
    else if (newDirection === 'right' && direction !== 'left') nextDirection = 'right';
    else if (newDirection === 'down' && direction !== 'up') nextDirection = 'down';
}

// 绘制游戏
function drawGame() {
    // 清空画布
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制网格线
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < canvas.width; i += 20) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
    }
    
    // 绘制蛇
    ctx.fillStyle = '#4CAF50';
    snake.forEach((segment, index) => {
        // 蛇头用不同颜色
        if (index === 0) {
            ctx.fillStyle = '#2E7D32'; // 深绿色蛇头
        } else {
            ctx.fillStyle = '#4CAF50'; // 绿色蛇身
        }
        ctx.fillRect(segment.x, segment.y, 20, 20);
        ctx.strokeStyle = '#000';
        ctx.strokeRect(segment.x, segment.y, 20, 20);
    });
    
    // 绘制食物
    ctx.fillStyle = '#F44336';
    ctx.beginPath();
    const centerX = food.x + 10;
    const centerY = food.y + 10;
    ctx.arc(centerX, centerY, 10, 0, Math.PI * 2);
    ctx.fill();
}

// 更新分数显示
function updateScore() {
    document.getElementById('score').textContent = `得分: ${score}`;
    
    // 更新最高分
    if (score > highScore) {
        highScore = score;
        document.getElementById('high-score').textContent = highScore;
        localStorage.setItem('snakeHighScore', highScore);
    }
}

// 游戏结束
function gameOver() {
    clearInterval(gameInterval);
    document.getElementById('final-score').textContent = score;
    document.getElementById('game-over').style.display = 'block';
    document.getElementById('start-btn').style.display = 'inline-block';
    document.getElementById('pause-btn').style.display = 'none';
}

// 切换暂停状态
function togglePause() {
    isPaused = !isPaused;
    document.getElementById('pause-btn').textContent = isPaused ? '继续' : '暂停';
}

// 改变游戏难度
function changeDifficulty() {
    const speed = parseInt(this.value);
    gameSpeed = speed;
    
    // 如果游戏正在进行中，更新游戏速度
    if (gameInterval && !isPaused) {
        clearInterval(gameInterval);
        gameInterval = setInterval(gameLoop, gameSpeed);
    }
}

// 页面加载完成后初始化游戏
window.onload = initGame;