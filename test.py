my-brick-breaker/
app.py
requirements.txt
streamlit
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="벽돌 깨기 게임", layout="centered")

st.title("🧱 클래식 벽돌 깨기")
st.write("마우스로 패들을 조작하여 공을 반사하고 모든 벽돌을 깨보세요!")

# JavaScript & HTML 기반 벽돌 깨기 게임 코드
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        * { padding: 0; margin: 0; }
        body { display: flex; justify-content: center; align-items: center; background: #0e1117; }
        canvas { background: #161b22; border: 2px solid #30363d; border-radius: 8px; }
    </style>
</head>
<body>

<canvas id="myCanvas" width="480" height="320"></canvas>

<script>
    const canvas = document.getElementById("myCanvas");
    const ctx = canvas.getContext("2d");

    let ballRadius = 8;
    let x = canvas.width / 2;
    let y = canvas.height - 30;
    let dx = 2.5;
    let dy = -2.5;

    let paddleHeight = 10;
    let paddleWidth = 75;
    let paddleX = (canvas.width - paddleWidth) / 2;

    let rowCount = 4;
    let columnCount = 5;
    let brickWidth = 75;
    let brickHeight = 20;
    let brickPadding = 10;
    let brickOffsetTop = 30;
    let brickOffsetLeft = 30;

    let score = 0;
    let lives = 3;

    let bricks = [];
    for (let c = 0; c < columnCount; c++) {
        bricks[c] = [];
        for (let r = 0; r < rowCount; r++) {
            bricks[c][r] = { x: 0, y: 0, status: 1 };
        }
    }

    document.addEventListener("mousemove", mouseMoveHandler, false);

    function mouseMoveHandler(e) {
        let relativeX = e.clientX - canvas.offsetLeft;
        if (relativeX > 0 && relativeX < canvas.width) {
            paddleX = relativeX - paddleWidth / 2;
        }
    }

    function collisionDetection() {
        for (let c = 0; c < columnCount; c++) {
            for (let r = 0; r < rowCount; r++) {
                let b = bricks[c][r];
                if (b.status == 1) {
                    if (x > b.x && x < b.x + brickWidth && y > b.y && y < b.y + brickHeight) {
                        dy = -dy;
                        b.status = 0;
                        score++;
                        if (score == rowCount * columnCount) {
                            alert("🎉 승리했습니다! 축하합니다!");
                            document.location.reload();
                        }
                    }
                }
            }
        }
    }

    function drawBall() {
        ctx.beginPath();
        ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
        ctx.fillStyle = "#58a6ff";
        ctx.fill();
        ctx.closePath();
    }

    function drawPaddle() {
        ctx.beginPath();
        ctx.rect(paddleX, canvas.height - paddleHeight - 5, paddleWidth, paddleHeight);
        ctx.fillStyle = "#238636";
        ctx.fill();
        ctx.closePath();
    }

    function drawBricks() {
        for (let c = 0; c < columnCount; c++) {
            for (let r = 0; r < rowCount; r++) {
                if (bricks[c][r].status == 1) {
                    let brickX = (c * (brickWidth + brickPadding)) + brickOffsetLeft;
                    let brickY = (r * (brickHeight + brickPadding)) + brickOffsetTop;
                    bricks[c][r].x = brickX;
                    bricks[c][r].y = brickY;
                    ctx.beginPath();
                    ctx.rect(brickX, brickY, brickWidth, brickHeight);
                    ctx.fillStyle = "#f85149";
                    ctx.fill();
                    ctx.closePath();
                }
            }
        }
    }

    function drawScore() {
        ctx.font = "14px sans-serif";
        ctx.fillStyle = "#f0f6fc";
        ctx.fillText("점수: " + score, 8, 20);
    }

    function drawLives() {
        ctx.font = "14px sans-serif";
        ctx.fillStyle = "#f0f6fc";
        ctx.fillText("목숨: " + lives, canvas.width - 65, 20);
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawBricks();
        drawBall();
        drawPaddle();
        drawScore();
        drawLives();
        collisionDetection();

        if (x + dx > canvas.width - ballRadius || x + dx < ballRadius) {
            dx = -dx;
        }
        if (y + dy < ballRadius) {
            dy = -dy;
        } else if (y + dy > canvas.height - ballRadius - 5) {
            if (x > paddleX && x < paddleX + paddleWidth) {
                dy = -dy;
            } else {
                lives--;
                if (!lives) {
                    alert("게임 오버!");
                    document.location.reload();
                } else {
                    x = canvas.width / 2;
                    y = canvas.height - 30;
                    dx = 2.5;
                    dy = -2.5;
                    paddleX = (canvas.width - paddleWidth) / 2;
                }
            }
        }

        x += dx;
        y += dy;
        requestAnimationFrame(draw);
    }

    draw();
</script>

</body>
</html>
"""

# Streamlit에 HTML 구성 요소 삽입
components.html(game_html, height=360)
