import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="10단계 벽돌 깨기 게임", layout="centered")

st.title("🧱 10단계 벽돌 깨기 (아이템 모드)")
st.caption("마우스 또는 터치로 패들을 조작하세요. 벽돌을 깨면 10% 확률로 아이템이 떨어집니다!")

# JavaScript & HTML 기반 벽돌 깨기 게임 코드
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        * { padding: 0; margin: 0; touch-action: none; box-sizing: border-box; }
        body { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            background: #0e1117; 
            overflow: hidden; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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

<canvas id="myCanvas" width="520" height="380"></canvas>

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

    // 아이템 종류 정의
    const ITEM_TYPES = [
        { type: 'DOUBLE', label: '공 2배', color: '#f39c12' },
        { type: 'ADD10', label: '공 +10', color: '#e74c3c' },
        { type: 'PADDLE', label: '판 확대', color: '#2ecc71' },
        { type: 'FLOOR', label: '안전 바닥', color: '#9b59b6' }
    ];

    // 마우스 및 터치 조작 핸들러
    document.addEventListener("mousemove", mouseMoveHandler, false);
    document.addEventListener("touchstart", touchHandler, { passive: false });
    document.addEventListener("touchmove", touchHandler, { passive: false });

    function mouseMoveHandler(e) {
        let rect = canvas.getBoundingClientRect();
        let relativeX = e.clientX - rect.left;
        if (relativeX > 0 && relativeX < canvas.width) {
            paddleX = relativeX - paddleWidth / 2;
        }
    }

    function touchHandler(e) {
        if (e.touches.length > 0) {
            let rect = canvas.getBoundingClientRect();
            let relativeX = e.touches[0].clientX - rect.left;
            if (relativeX > 0 && relativeX < canvas.width) {
                paddleX = relativeX - paddleWidth / 2;
            }
        }
    }

    // 스테이지 초기화
    function initStage(stageNum) {
        balls = [];
        items = [];
        
        // 공 초기화
        balls.push({
            x: canvas.width / 2,
            y: canvas.height - 35,
            dx: (Math.random() < 0.5 ? 1 : -1) * (2.2 + stageNum * 0.15),
            dy: -(2.5 + stageNum * 0.15),
            radius: 7,
            color: "#58a6ff"
        });

        paddleWidth = basePaddleWidth;
        paddleX = (canvas.width - paddleWidth) / 2;
        
        // 스테이지 난이도별 벽돌 배치
        let rows = Math.min(3 + Math.floor((stageNum - 1) / 2), 7);
        let cols = Math.min(5 + Math.floor((stageNum - 1) / 1.8), 9);
        
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
                // 고단계에서 일부 내구도 높은 벽돌 등장
                if (stageNum >= 3 && Math.random() < 0.2) hp = 2;
                if (stageNum >= 6 && Math.random() < 0.3) hp = 2;
                if (stageNum >= 9 && Math.random() < 0.4) hp = 3;

                let color = stageColors[(r + stageNum) % stageColors.length];

                bricks[c][r] = {
                    x: 0,
                    y: 0,
                    status: hp,
                    maxHp: hp,
                    width: brickWidth,
                    height: brickHeight,
                    color: color
                };
            }
        }
    }

    // 아이템 생성 (10% 확률)
    function spawnItem(x, y) {
        if (Math.random() < 0.10) {
            let randomType = ITEM_TYPES[Math.floor(Math.random() * ITEM_TYPES.length)];
            items.push({
                x: x,
                y: y,
                width: 54,
                height: 20,
                dy: 1.8,
                type: randomType.type,
                label: randomType.label,
                color: randomType.color
            });
        }
    }

    // 아이템 효과 적용
    function applyItemEffect(type) {
        if (type === 'DOUBLE') {
            let currentCount = balls.length;
            for (let i = 0; i < currentCount; i++) {
                let b = balls[i];
                let angle = (Math.random() - 0.5) * 1.5;
                let speed = Math.sqrt(b.dx * b.dx + b.dy * b.dy);
                balls.push({
                    x: b.x,
                    y: b.y,
                    dx: Math.sin(angle) * speed,
                    dy: -Math.abs(Math.cos(angle) * speed),
                    radius: b.radius,
                    color: '#f39c12'
                });
            }
        } else if (type === 'ADD10') {
            for (let i = 0; i < 10; i++) {
                let angle = ((i - 4.5) / 5) * (Math.PI / 3);
                let speed = 3.2;
                balls.push({
                    x: paddleX + paddleWidth / 2,
                    y: canvas.height - paddleHeight - 15,
                    dx: Math.sin(angle) * speed,
                    dy: -Math.abs(Math.cos(angle) * speed),
                    radius: 6,
                    color: '#e74c3c'
                });
            }
        } else if (type === 'PADDLE') {
            paddleWidth = basePaddleWidth * 1.6;
            paddleExpandTimer = 600; // 약 10초
        } else if (type === 'FLOOR') {
            safetyFloorTimer = 600; // 약 10초
        }
    }

    // 아이템 업데이트 및 그리기도
    function updateAndDrawItems() {
        for (let i = items.length - 1; i >= 0; i--) {
            let item = items[i];
            item.y += item.dy;

            // 아이템 그리기
            ctx.fillStyle = item.color;
            ctx.beginPath();
            ctx.rect(item.x - item.width / 2, item.y, item.width, item.height);
            ctx.fill();
            ctx.closePath();

            ctx.font = "bold 11px sans-serif";
            ctx.fillStyle = "#ffffff";
            ctx.textAlign = "center";
            ctx.fillText(item.label, item.x, item.y + 14);

            // 패들 충돌 검사 (아이템 획득)
            if (item.y + item.height >= canvas.height - paddleHeight - 5 &&
                item.y <= canvas.height - 5 &&
                item.x >= paddleX - 10 && item.x <= paddleX + paddleWidth + 10) {
                
                applyItemEffect(item.type);
                items.splice(i, 1);
                continue;
            }

            // 화면 밖으로 나감
            if (item.y > canvas.height) {
                items.splice(i, 1);
            }
        }
    }

    // 공 업데이트 및 그려주기
    function updateAndDrawBalls() {
        for (let i = balls.length - 1; i >= 0; i--) {
            let b = balls[i];

            ctx.beginPath();
            ctx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
            ctx.fillStyle = b.color || "#58a6ff";
            ctx.fill();
            ctx.closePath();

            // 좌우 벽 충돌
            if (b.x + b.dx > canvas.width - b.radius || b.x + b.dx < b.radius) {
                b.dx = -b.dx;
            }
            // 천장 충돌
            if (b.y + b.dy < b.radius) {
                b.dy = -b.dy;
            }

            // 패들 충돌
            if (b.y + b.dy > canvas.height - paddleHeight - b.radius - 5 &&
                b.y + b.dy < canvas.height - 5 &&
                b.x >= paddleX && b.x <= paddleX + paddleWidth) {
                
                let hitPos = (b.x - (paddleX + paddleWidth / 2)) / (paddleWidth / 2);
                let speed = Math.sqrt(b.dx * b.dx + b.dy * b.dy);
                let maxAngle = Math.PI / 3;
                let angle = hitPos * maxAngle;

                b.dx = speed * Math.sin(angle);
                b.dy = -speed * Math.cos(angle);
            }

            // 안전 바닥판 충돌
            if (safetyFloorTimer > 0 && b.y + b.dy >= canvas.height - b.radius - 6) {
                b.dy = -Math.abs(b.dy);
            }

            // 바닥에 떨어짐 (공 소멸)
            if (b.y + b.dy > canvas.height - b.radius) {
                balls.splice(i, 1);
                continue;
            }

            // 벽돌 충돌
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

                        if (b.x > brickX && b.x < brickX + brick.width &&
                            b.y > brickY && b.y < brickY + brick.height) {
                            
                            b.dy = -b.dy;
                            brick.status--;
                            score += 10;

                            if (brick.status === 0) {
                                spawnItem(brickX + brick.width / 2, brickY + brick.height);
                            }
                        }
                    }
                }
            }

            b.x += b.dx;
            b.y += b.dy;
        }

        // 공이 모두 사라졌을 때
        if (balls.length === 0) {
            lives--;
            if (lives <= 0) {
                alert("🎮 게임 오버!\n최종 점수: " + score + "\n진행 스테이지: Stage " + currentStage);
                document.location.reload();
            } else {
                balls.push({
                    x: canvas.width / 2,
                    y: canvas.height - 35,
                    dx: (Math.random() < 0.5 ? 1 : -1) * 3,
                    dy: -3,
                    radius: 7,
                    color: "#58a6ff"
                });
                paddleX = (canvas.width - paddleWidth) / 2;
            }
        }
    }

    // 벽돌 그리기
    function drawBricks() {
        let brickOffsetTop = 45;
        let brickOffsetLeft = 15;
        let brickPadding = 6;

        for (let c = 0; c < bricks.length; c++) {
            for (let r = 0; r < bricks[c].length; r++) {
                let brick = bricks[c][r];
                if (brick.status > 0) {
                    let brickX = (c * (brick.width + brickPadding)) + brickOffsetLeft;
                    let brickY = (r * (brick.height + brickPadding)) + brickOffsetTop;
                    
                    ctx.beginPath();
                    ctx.rect(brickX, brickY, brick.width, brick.height);
                    ctx.fillStyle = brick.status > 1 ? "#e74c3c" : brick.color;
                    ctx.fill();
                    ctx.closePath();
                }
            }
        }
    }

    // 패들 그리기
    function drawPaddle() {
        ctx.beginPath();
        ctx.rect(paddleX, canvas.height - paddleHeight - 5, paddleWidth, paddleHeight);
        ctx.fillStyle = paddleExpandTimer > 0 ? "#2ecc71" : "#238636";
        ctx.fill();
        ctx.closePath();
    }

    // 안전 바닥판 그리기
    function drawSafetyFloor() {
        if (safetyFloorTimer > 0) {
            ctx.beginPath();
            ctx.rect(0, canvas.height - 6, canvas.width, 6);
            ctx.fillStyle = "#9b59b6";
            ctx.fill();
            ctx.closePath();
        }
    }

    // 상단 UI (점수, 스테이지, 목숨, 버프 상태)
    function drawHUD() {
        ctx.font = "bold 13px sans-serif";
        ctx.fillStyle = "#f0f6fc";
        ctx.textAlign = "left";
        ctx.fillText("Stage " + currentStage + "/" + maxStage, 10, 22);
        ctx.fillText("점수: " + score, 110, 22);
        ctx.fillText("공: " + balls.length + "개", 210, 22);

        ctx.textAlign = "right";
        ctx.fillText("목숨: " + "❤️".repeat(lives), canvas.width - 10, 22);

        // 버프 타이머 상태 표시
        let buffText = [];
        if (paddleExpandTimer > 0) buffText.push("판확대(" + Math.ceil(paddleExpandTimer / 60) + "s)");
        if (safetyFloorTimer > 0) buffText.push("안전바닥(" + Math.ceil(safetyFloorTimer / 60) + "s)");
        
        if (buffText.length > 0) {
            ctx.font = "12px sans-serif";
            ctx.fillStyle = "#2ecc71";
            ctx.textAlign = "center";
            ctx.fillText("버프: " + buffText.join(" | "), canvas.width / 2, 22);
        }
    }

    // 타이머 관리
    function updateTimers() {
        if (paddleExpandTimer > 0) {
            paddleExpandTimer--;
            if (paddleExpandTimer === 0) paddleWidth = basePaddleWidth;
        }
        if (safetyFloorTimer > 0) {
            safetyFloorTimer--;
        }
    }

    // 스테이지 클리어 체크
    function checkStageClear() {
        let remainingBricks = 0;
        for (let c = 0; c < bricks.length; c++) {
            for (let r = 0; r < bricks[c].length; r++) {
                if (bricks[c][r].status > 0) remainingBricks++;
            }
        }

        if (remainingBricks === 0) {
            if (currentStage >= maxStage) {
                alert("🏆 축하합니다! 모든 10개 스테이지를 클리어하셨습니다!\n최종 점수: " + score);
                document.location.reload();
            } else {
                currentStage++;
                alert("🎉 Stage " + (currentStage - 1) + " 클리어!\nStage " + currentStage + "로 이동합니다!");
                initStage(currentStage);
            }
        }
    }

    // 메인 루프
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        drawBricks();
        drawPaddle();
        drawSafetyFloor();
        updateAndDrawItems();
        updateAndDrawBalls();
        drawHUD();
        updateTimers();
        checkStageClear();

        requestAnimationFrame(draw);
    }

    // 게임 시작
    initStage(1);
    draw();
</script>

</body>
</html>
"""

components.html(game_html, height=410)
