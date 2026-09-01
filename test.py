import streamlit as st
import streamlit.components.v1 as components
import base64

st.set_page_config(page_title="10단계 벽돌 깨기 게임", layout="centered")

st.title("🧱 10단계 벽돌 깨기 (아이템 모드)")
st.caption("마우스 또는 터치로 패들을 조작하세요. 벽돌을 깨면 10% 확률로 아이템이 떨어집니다!")

# HTML/JS 코드 정의
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        * { padding: 0; margin: 0; touch-action: none; box-sizing: border-box; }
        body { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            background: #0e1117; 
            overflow: hidden; 
            font-family: sans-serif;
            width: 100vw;
            height: 100vh;
        }
        canvas { 
            background: #161b22; 
            border: 2px solid #30363d; 
            border-radius: 12px; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }
    </style>
</head>
<body>

<canvas id="myCanvas" width="480" height="380"></canvas>

<script>
    const canvas = document.getElementById("myCanvas");
    const ctx = canvas.getContext("2d");

    let currentStage = 1;
    const maxStage = 10;
    let score = 0;
    let lives = 3;

    let paddleHeight = 12;
    let basePaddleWidth = 80;
    let paddleWidth = basePaddleWidth;
    let paddleX = (canvas.width - paddleWidth) / 2;

    let paddleExpandTimer = 0;
    let safetyFloorTimer = 0;

    let balls = [];
    let items = [];
    let bricks = [];

    const ITEM_TYPES = [
        { type: 'DOUBLE', label: '공 2배', color: '#f39c12' },
        { type: 'ADD10', label: '공 +10', color: '#e74c3c' },
        { type: 'PADDLE', label: '판 확대', color: '#2ecc71' },
        { type: 'FLOOR', label: '안전 바닥', color: '#9b59b6' }
    ];

    function getCanvasPos(e) {
        let rect = canvas.getBoundingClientRect();
        let clientX = e.touches ? e.touches[0].clientX : e.clientX;
        let scaleX = canvas.width / rect.width;
        return (clientX - rect.left) * scaleX;
    }

    document.addEventListener("mousemove", function(e) {
        let relativeX = getCanvasPos(e);
        if (relativeX > 0 && relativeX < canvas.width) {
            paddleX = relativeX - paddleWidth / 2;
        }
    }, false);

    document.addEventListener("touchmove", function(e) {
        let relativeX = getCanvasPos(e);
        if (relativeX > 0 && relativeX < canvas.width) {
            paddleX = relativeX - paddleWidth / 2;
        }
    }, { passive: false });

    function initStage(stageNum) {
        balls = [{
            x: canvas.width / 2,
            y: canvas.height - 35,
            dx: (Math.random() < 0.5 ? 1 : -1) * (2.2 + stageNum * 0.15),
            dy: -(2.5 + stageNum * 0.15),
            radius: 7,
            color: "#58a6ff"
        }];

        items = [];
        paddleWidth = basePaddleWidth;
        paddleX = (canvas.width - paddleWidth) / 2;
        
        let rows = Math.min(3 + Math.floor((stageNum - 1) / 2), 6);
        let cols = Math.min(5 + Math.floor((stageNum - 1) / 2), 8);
        
        let brickPadding = 6;
        let brickOffsetTop = 45;
        let brickOffsetLeft = 15;
        let availableWidth = canvas.width - (brickOffsetLeft * 2);
        let brickWidth = (availableWidth - (brickPadding * (cols - 1))) / cols;
        let brickHeight = 16;

        const stageColors = ["#f85149", "#d29922", "#3fb950", "#a371f7", "#58a6ff"];

        bricks = [];
        for (let c = 0; c < cols; c++) {
            bricks[c] = [];
            for (let r = 0; r < rows; r++) {
                let hp = 1;
                if (stageNum >= 3 && Math.random() < 0.25) hp = 2;
                if (stageNum >= 7 && Math.random() < 0.35) hp = 3;

                bricks[c][r] = {
                    x: 0,
                    y: 0,
                    status: hp,
                    width: brickWidth,
                    height: brickHeight,
                    color: stageColors[(r + stageNum) % stageColors.length]
                };
            }
        }
    }

    function spawnItem(x, y) {
        if (Math.random() < 0.10) {
            let randomType = ITEM_TYPES[Math.floor(Math.random() * ITEM_TYPES.length)];
            items.push({
                x: x,
                y: y,
                width: 50,
                height: 18,
                dy: 1.8,
                type: randomType.type,
                label: randomType.label,
                color: randomType.color
            });
        }
    }

    function applyItemEffect(type) {
        if (type === 'DOUBLE') {
            let len = balls.length;
            for (let i = 0; i < len; i++) {
                let b = balls[i];
                balls.push({
                    x: b.x,
                    y: b.y,
                    dx: -b.dx,
                    dy: b.dy,
                    radius: b.radius,
                    color: '#f39c12'
                });
            }
        } else if (type === 'ADD10') {
            for (let i = 0; i < 10; i++) {
                let angle = ((i - 4.5) / 5) * (Math.PI / 3);
                balls.push({
                    x: paddleX + paddleWidth / 2,
                    y: canvas.height - paddleHeight - 15,
                    dx: Math.sin(angle) * 3,
                    dy: -Math.abs(Math.cos(angle) * 3),
                    radius: 6,
                    color: '#e74c3c'
                });
            }
        } else if (type === 'PADDLE') {
            paddleWidth = basePaddleWidth * 1.5;
            paddleExpandTimer = 600;
        } else if (type === 'FLOOR') {
            safetyFloorTimer = 600;
        }
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // 1. 벽돌
        let brickOffsetTop = 45;
        let brickOffsetLeft = 15;
        let brickPadding = 6;

        for (let c = 0; c < bricks.length; c++) {
            for (let r = 0; r < bricks[c].length; r++) {
                let brick = bricks[c][r];
                if (brick.status > 0) {
                    let brickX = (c * (brick.width + brickPadding)) + brickOffsetLeft;
                    let brickY = (r * (brick.height + brickPadding)) + brickOffsetTop;
                    brick.x = brickX;
                    brick.y = brickY;

                    ctx.beginPath();
                    ctx.rect(brickX, brickY, brick.width, brick.height);
                    ctx.fillStyle = brick.status > 1 ? "#e74c3c" : brick.color;
                    ctx.fill();
                    ctx.closePath();
                }
            }
        }

        // 2. 패들
        ctx.beginPath();
        ctx.rect(paddleX, canvas.height - paddleHeight - 5, paddleWidth, paddleHeight);
        ctx.fillStyle = paddleExpandTimer > 0 ? "#2ecc71" : "#238636";
        ctx.fill();
        ctx.closePath();

        // 3. 안전 바닥
        if (safetyFloorTimer > 0) {
            ctx.beginPath();
            ctx.rect(0, canvas.height - 4, canvas.width, 4);
            ctx.fillStyle = "#9b59b6";
            ctx.fill();
            ctx.closePath();
        }

        // 4. 아이템
        for (let i = items.length - 1; i >= 0; i--) {
            let item = items[i];
            item.y += item.dy;

            ctx.fillStyle = item.color;
            ctx.fillRect(item.x - item.width / 2, item.y, item.width, item.height);

            ctx.font = "bold 10px sans-serif";
            ctx.fillStyle = "#ffffff";
            ctx.textAlign = "center";
            ctx.fillText(item.label, item.x, item.y + 13);

            if (item.y + item.height >= canvas.height - paddleHeight - 5 &&
                item.y <= canvas.height - 5 &&
                item.x >= paddleX - 10 && item.x <= paddleX + paddleWidth + 10) {
                applyItemEffect(item.type);
                items.splice(i, 1);
                continue;
            }

            if (item.y > canvas.height) items.splice(i, 1);
        }

        // 5. 공
        for (let i = balls.length - 1; i >= 0; i--) {
            let b = balls[i];

            ctx.beginPath();
            ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
            ctx.fillStyle = b.color;
            ctx.fill();
            ctx.closePath();

            if (b.x + b.dx > canvas.width - b.radius || b.x + b.dx < b.radius) b.dx = -b.dx;
            if (b.y + b.dy < b.radius) b.dy = -b.dy;

            if (b.y + b.dy > canvas.height - paddleHeight - b.radius - 5 &&
                b.y + b.dy < canvas.height - 5 &&
                b.x >= paddleX && b.x <= paddleX + paddleWidth) {
                b.dy = -Math.abs(b.dy);
            }

            if (safetyFloorTimer > 0 && b.y + b.dy >= canvas.height - b.radius - 4) {
                b.dy = -Math.abs(b.dy);
            }

            if (b.y + b.dy > canvas.height - b.radius) {
                balls.splice(i, 1);
                continue;
            }

            for (let c = 0; c < bricks.length; c++) {
                for (let r = 0; r < bricks[c].length; r++) {
                    let brick = bricks[c][r];
                    if (brick.status > 0) {
                        if (b.x > brick.x && b.x < brick.x + brick.width &&
                            b.y > brick.y && b.y < brick.y + brick.height) {
                            b.dy = -b.dy;
                            brick.status--;
                            score += 10;
                            if (brick.status === 0) spawnItem(brick.x + brick.width / 2, brick.y + brick.height);
                        }
                    }
                }
            }

            b.x += b.dx;
            b.y += b.dy;
        }

        if (balls.length === 0) {
            lives--;
            if (lives <= 0) {
                alert("🎮 게임 오버!\n점수: " + score);
                document.location.reload();
            } else {
                initStage(currentStage);
            }
        }

        // 6. 상단 UI
        ctx.font = "bold 12px sans-serif";
        ctx.fillStyle = "#f0f6fc";
        ctx.textAlign = "left";
        ctx.fillText("Stage " + currentStage + " | 점수:" + score + " | 공:" + balls.length, 10, 20);
        ctx.textAlign = "right";
        ctx.fillText("목숨:" + lives, canvas.width - 10, 20);

        if (paddleExpandTimer > 0) paddleExpandTimer--;
        if (safetyFloorTimer > 0) safetyFloorTimer--;

        // 7. 클리어 체크
        let remaining = 0;
        for (let c = 0; c < bricks.length; c++) {
            for (let r = 0; r < bricks[c].length; r++) {
                if (bricks[c][r].status > 0) remaining++;
            }
        }

        if (remaining === 0) {
            if (currentStage >= maxStage) {
                alert("🏆 올클리어! 최종점수: " + score);
                document.location.reload();
            } else {
                currentStage++;
                initStage(currentStage);
            }
        }

        requestAnimationFrame(draw);
    }

    initStage(1);
    draw();
</script>

</body>
</html>
"""

# Base64 인코딩을 적용해 파이썬-HTML 간 파싱 문제 완전 방지
b64_html = base64.b64encode(game_html.encode('utf-8')).decode('utf-8')
iframe_code = f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="410" frameborder="0" scrolling="no"></iframe>'

st.components.v1.html(iframe_code, height=420)
